import os
import ast
import psycopg2
import pandas as pd
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.messages import HumanMessage
from ai_agent.agents.data_agent import data_agent
from ai_agent.utils.dataset_manager import DatasetManager

from ai_agent.utils.database import get_db_config, get_db_connection

load_dotenv()

app = FastAPI(
    title="AI Data Agent API",
    description="FastAPI Backend for Autonomous AI Data Agent powered by LangGraph, Gemini & PostgreSQL",
    version="2.0.0"
)

# Enable CORS for React Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State / Utilities
dataset_mgr = DatasetManager()
in_memory_datasets: Dict[str, Dict[str, Any]] = {}
in_memory_query_history: List[Dict[str, Any]] = []


def check_db_connection() -> bool:
    try:
        conn = get_db_connection()
        conn.close()
        return True
    except Exception:
        return False



def parse_sql_result_rows(raw_result: str) -> tuple[List[str], List[List[Any]]]:
    """Parses raw python representation of tuples into columns and row lists."""
    if not raw_result or not isinstance(raw_result, str):
        return [], []
    raw_str = raw_result.strip()
    if not (raw_str.startswith("[") and raw_str.endswith("]")):
        return [], []
    try:
        parsed = ast.literal_eval(raw_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            df = pd.DataFrame(parsed)
            cols = [f"col_{i+1}" for i in range(df.shape[1])]
            rows = df.values.tolist()
            return cols, rows
    except Exception:
        pass
    return [], []


# --- Pydantic Schemas ---
class ChatRequest(BaseModel):
    message: str
    dataset_id: Optional[str] = None
    history: List[Dict[str, str]] = []  # recent turns: [{"role": "user"|"assistant", "content": "..."}]


class ChatResponse(BaseModel):
    intent: str  # "dataset" | "off_topic" | "unclear"
    answer: str
    route: str
    sql: Optional[str] = None
    columns: List[str] = []
    rows: List[List[Any]] = []
    row_count: int = 0
    execution_status: Optional[str] = None


# --- Endpoints ---

@app.get("/api/health")
def health_check():
    db_connected = check_db_connection()
    db_cfg = get_db_config()
    return {
        "status": "healthy",
        "database_connected": db_connected,
        "database_name": db_cfg["dbname"]
    }



@app.get("/api/datasets")
def list_datasets():
    return {
        "datasets": list(in_memory_datasets.values())
    }


@app.post("/api/datasets/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
    
    try:
        success, msg, ds_info = dataset_mgr.process_and_upload_csv(file.file, file.filename)
        if not success or not ds_info:
            raise HTTPException(status_code=400, detail=msg)
        
        # Serialize preview_df for JSON response
        preview_data = ds_info["preview_df"].to_dict(orient="records")
        ds_info_serializable = dict(ds_info)
        ds_info_serializable["preview_records"] = preview_data
        del ds_info_serializable["preview_df"]
        
        in_memory_datasets[ds_info["id"]] = ds_info_serializable
        return {
            "message": "Dataset uploaded and loaded into PostgreSQL successfully.",
            "dataset": ds_info_serializable
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {str(e)}")


@app.get("/api/datasets/{dataset_id}")
def get_dataset_details(dataset_id: str):
    if dataset_id not in in_memory_datasets:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return in_memory_datasets[dataset_id]


@app.delete("/api/datasets/{dataset_id}")
def delete_dataset(dataset_id: str):
    if dataset_id not in in_memory_datasets:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    
    table_name = in_memory_datasets[dataset_id]["table_name"]
    dataset_mgr.drop_dataset_table(table_name)
    del in_memory_datasets[dataset_id]
    return {"message": f"Dataset {dataset_id} deleted successfully."}


@app.get("/api/query-history")
def get_query_history():
    return {"history": list(reversed(in_memory_query_history))}


import time

@app.post("/api/chat", response_model=ChatResponse)
def chat_with_agent(req: ChatRequest):
    t_start = time.time()
    context_prefix = ""
    target_dataset_name = "Built-in Database"
    
    if req.dataset_id and req.dataset_id in in_memory_datasets:
        ds = in_memory_datasets[req.dataset_id]
        target_dataset_name = ds["filename"]
        context_prefix = (
            f"[CONTEXT: The user has selected uploaded dataset '{ds['filename']}'. "
            f"Target PostgreSQL table name is '{ds['table_name']}'. "
            f"Columns and types: {ds['schema']}]. "
        )
    
    history_prefix = ""
    recent = [h for h in (req.history or []) if h.get("role") in ("user", "assistant") and h.get("content")][-6:]
    if recent:
        lines = "\n".join(f"{h['role']}: {h['content'][:300]}" for h in recent)
        history_prefix = f"[RECENT CONVERSATION (for resolving follow-up references only):\n{lines}]\nCurrent question: "

    full_prompt = f"{context_prefix}{history_prefix}{req.message}"
    
    try:
        agent_response = data_agent.invoke(
            {
                "messages": [HumanMessage(content=full_prompt)],
                "route_response": ""
            }
        )
        print(f"[CHAT TIMING TOTAL] End-to-end /api/chat latency: {time.time() - t_start:.3f}s")

        
        route = agent_response.get("route_response", "off_topic")
        final_text = agent_response.get("final_answer", "")
        sql_query = ""
        sql_result = ""
        messages_list = agent_response.get("messages", [])
        
        intent_type = "dataset" if route in ["sql", "etl"] else ("unclear" if route == "unclear" else "off_topic")
        exec_status = "executed" if intent_type == "dataset" else None

        if intent_type == "dataset" and route == "sql":
            for item in reversed(messages_list):
                if isinstance(item, dict):
                    sql_query = item.get("generated_sql_query", "")
                    sql_result = item.get("sql_query_execution_result", "")
                    if not final_text:
                        final_text = item.get("final_answer", "")
                    if final_text:
                        break
        
        # Fallback if final_text is still empty: ONLY look for AIMessage or dict.final_answer
        if not final_text:
            for item in reversed(messages_list):
                if isinstance(item, AIMessage) and item.content:
                    final_text = str(item.content)
                    break
                elif isinstance(item, dict) and item.get("final_answer"):
                    final_text = str(item.get("final_answer"))
                    break

        # Strip any internal context prefix if present
        if "[CONTEXT:" in final_text and "]." in final_text:
            final_text = final_text.split("].", 1)[1].strip()
        if "Current question:" in final_text:
            final_text = final_text.split("Current question:", 1)[1].strip()
        
        if not final_text:
            if intent_type == "off_topic":
                final_text = "I'm QueryFlow, an AI data analysis assistant. I'm here to help you explore and analyze your connected dataset. Ask me something about your data and I'll take care of the SQL and analysis."
            elif intent_type == "unclear":
                final_text = "What would you like to know about your dataset? You can ask about counts, averages, trends, comparisons, or specific records."
            else:
                final_text = "QueryFlow assistant response ready."
            
        cols, rows = parse_sql_result_rows(sql_result) if intent_type == "dataset" else ([], [])
        
        # Save to query history audit log if dataset query
        if intent_type == "dataset":
            in_memory_query_history.append({
                "question": req.message,
                "dataset": target_dataset_name,
                "answer": final_text,
                "sql": sql_query,
                "route": route,
                "row_count": len(rows)
            })
        
        return ChatResponse(
            intent=intent_type,
            answer=final_text,
            route=route,
            sql=sql_query if (sql_query and intent_type == "dataset") else None,
            columns=cols if intent_type == "dataset" else [],
            rows=rows if intent_type == "dataset" else [],
            row_count=len(rows) if intent_type == "dataset" else 0,
            execution_status=exec_status
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
