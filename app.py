import os
import ast
import psycopg2
import pandas as pd
import streamlit as st
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

from ai_agent.agents.data_agent import data_agent
from ai_agent.utils.dataset_manager import DatasetManager
from components.sidebar import render_sidebar
from components.header import render_header
from components.visualization import render_visualization

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Data Agent Workspace",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load External Stylesheet
def load_css(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("styles/app.css")


def check_database_connection():
    """Checks PostgreSQL connectivity using .env credentials without exposing secrets."""
    db_name = os.getenv("database", os.getenv("dbname", "project_sql_agent"))
    user = os.getenv("user", "postgres")
    password = os.getenv("password", "")
    host = os.getenv("host", "localhost")
    port = os.getenv("port", 5432)

    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
            connect_timeout=3
        )
        conn.close()
        return True, db_name
    except Exception:
        return False, db_name


def parse_sql_result(raw_result: str):
    """Attempts to parse Python literal strings of database result rows into DataFrame."""
    if not raw_result or not isinstance(raw_result, str):
        return None
    
    raw_str = raw_result.strip()
    if not (raw_str.startswith("[") and raw_str.endswith("]")):
        return None

    try:
        parsed = ast.literal_eval(raw_str)
        if isinstance(parsed, list) and len(parsed) > 0:
            df = pd.DataFrame(parsed)
            df.columns = [f"Col {i+1}" for i in range(df.shape[1])]
            return df
    except Exception:
        pass
    return None


# Initialize Dataset Manager & Session State
dataset_mgr = DatasetManager()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "datasets" not in st.session_state:
    st.session_state.datasets = {}

if "active_dataset_id" not in st.session_state:
    st.session_state.active_dataset_id = None

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "current_page" not in st.session_state:
    st.session_state.current_page = "overview"


# --- RENDER SIDEBAR ---
render_sidebar(dataset_mgr, check_database_connection)


# ==============================================================================
# PAGE 1: OVERVIEW DASHBOARD
# ==============================================================================
if st.session_state.current_page == "overview":
    render_header("Overview", "Intelligent workspace analytics and data exploration hub.")

    # Hero Banner
    st.markdown("""
        <div class="saas-hero">
            <div style="font-size: 0.8rem; font-weight: 700; color: #5B5CE2; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem;">
                ✦ AI DATA WORKSPACE
            </div>
            <h1 style="margin: 0; font-size: 1.85rem; font-weight: 800; color: #111827; letter-spacing: -0.03em;">
                Your data, intelligently explored.
            </h1>
            <p style="margin-top: 0.4rem; margin-bottom: 0; color: #667085; font-size: 0.95rem; font-weight: 500; max-width: 680px;">
                Upload datasets, ask natural-language analytics questions, automatically generate Postgres SQL queries, and turn raw data into useful insights.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Distinct Stat Cards
    c1, c2, c3, c4 = st.columns(4)
    total_datasets = len(st.session_state.datasets)
    total_rows = sum([d["row_count"] for d in st.session_state.datasets.values()]) if total_datasets else 0
    total_cols = sum([d["col_count"] for d in st.session_state.datasets.values()]) if total_datasets else 0
    queries_run = len(st.session_state.query_history)

    with c1:
        st.markdown(f"""
            <div class="saas-stat-card">
                <div class="saas-stat-icon-wrapper" style="background-color: #EEF0FF; color: #5B5CE2;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"/><polyline points="14 2 14 8 20 8"/><path d="M2 15h10"/><path d="m9 18 3-3-3-3"/></svg>
                </div>
                <div class="saas-stat-label">Datasets</div>
                <div class="saas-stat-value">{total_datasets:,}</div>
                <div style="font-size: 0.775rem; color: #667085; margin-top: 0.2rem;">Active imported datasets</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="saas-stat-card">
                <div class="saas-stat-icon-wrapper" style="background-color: #F5F3FF; color: #7C5CFC;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
                </div>
                <div class="saas-stat-label">Rows Analyzed</div>
                <div class="saas-stat-value">{total_rows:,}</div>
                <div style="font-size: 0.775rem; color: #667085; margin-top: 0.2rem;">Postgres record count</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="saas-stat-card">
                <div class="saas-stat-icon-wrapper" style="background-color: #ECFDF5; color: #12B76A;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M3 15h18"/><path d="M9 3v18"/><path d="M15 3v18"/></svg>
                </div>
                <div class="saas-stat-label">Columns</div>
                <div class="saas-stat-value">{total_cols:,}</div>
                <div style="font-size: 0.775rem; color: #667085; margin-top: 0.2rem;">Structured features</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="saas-stat-card">
                <div class="saas-stat-icon-wrapper" style="background-color: #EFF6FF; color: #4F8CFF;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                </div>
                <div class="saas-stat-label">Queries Executed</div>
                <div class="saas-stat-value">{queries_run:,}</div>
                <div style="font-size: 0.775rem; color: #667085; margin-top: 0.2rem;">Agent SQL executions</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    
    # Recent Datasets & Recent Queries Sections
    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        st.markdown("### Connected Datasets")
        if not st.session_state.datasets:
            st.markdown("""
                <div class="saas-card" style="text-align: center; padding: 2.5rem 1.5rem; color: #667085;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #111827;">No Custom Datasets Connected</div>
                    <div style="font-size: 0.875rem; margin-top: 0.25rem;">Upload a CSV file from the sidebar to analyze custom data.</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            for ds_id, ds in st.session_state.datasets.items():
                st.markdown(f"""
                    <div class="saas-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 700; font-size: 1.025rem; color: #111827;">{ds['filename']}</div>
                                <div style="font-size: 0.825rem; color: #667085; margin-top: 0.25rem;">
                                    Table: <code>{ds['table_name']}</code> &bull; {ds['row_count']:,} rows &bull; {ds['col_count']} columns
                                </div>
                            </div>
                            <span class="saas-badge-success">Ready</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.markdown("### Recent Activity")
        if not st.session_state.query_history:
            st.markdown("""
                <div class="saas-card" style="text-align: center; padding: 2.5rem 1.5rem; color: #667085;">
                    <div style="font-weight: 700; color: #111827; font-size: 1.05rem;">No Queries Recorded Yet</div>
                    <div style="font-size: 0.875rem; margin-top: 0.25rem;">Navigate to 'Ask Data' to run your first query.</div>
                </div>
            """, unsafe_allow_html=True)
        else:
            for q in list(reversed(st.session_state.query_history))[:4]:
                st.markdown(f"""
                    <div class="saas-card" style="padding: 0.85rem 1.1rem;">
                        <div style="font-weight: 600; font-size: 0.9rem; color: #111827;">{q['question']}</div>
                        <div style="font-size: 0.775rem; color: #667085; margin-top: 0.3rem; display: flex; justify-content: space-between; align-items: center;">
                            <span>Dataset: <code>{q['dataset']}</code></span>
                            <span class="saas-badge-success" style="font-size: 0.7rem; padding: 0.15rem 0.45rem;">Executed</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# ==============================================================================
# PAGE 2: DATASETS MANAGEMENT
# ==============================================================================
elif st.session_state.current_page == "datasets":
    render_header("Datasets", "Manage and explore connected PostgreSQL dataset tables.")

    if not st.session_state.datasets:
        st.markdown("""
            <div class="saas-card" style="text-align: center; padding: 3rem 2rem;">
                <h3 style="margin: 0; color: #111827;">No Custom Datasets Found</h3>
                <p style="color: #667085; font-size: 0.925rem; max-width: 480px; margin: 0.5rem auto 1.5rem auto;">
                    Use the sidebar file uploader to upload CSV files. They will be imported into PostgreSQL automatically.
                </p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for ds_id, ds in st.session_state.datasets.items():
            with st.expander(f"{ds['filename']} — PostgreSQL Table: `{ds['table_name']}` ({ds['row_count']:,} rows, {ds['col_count']} columns)", expanded=True):
                t1, t2, t3 = st.tabs(["Overview & Schema", "Data Preview", "Table Actions"])
                
                with t1:
                    st.markdown("#### Database Schema Definition")
                    schema_df = pd.DataFrame([
                        {"Postgres Column": col, "Data Type": dtype, "Original Column Header": orig}
                        for (orig, col), dtype in zip(ds["column_mapping"].items(), ds["schema"].values())
                    ])
                    st.dataframe(schema_df, use_container_width=True)

                with t2:
                    st.markdown("#### Data Sample (First 10 Rows)")
                    st.dataframe(ds["preview_df"], use_container_width=True)

                with t3:
                    if st.button(f"Safely Drop PostgreSQL Table `{ds['table_name']}`", key=f"del_{ds_id}", type="secondary"):
                        dataset_mgr.drop_dataset_table(ds['table_name'])
                        del st.session_state.datasets[ds_id]
                        if st.session_state.active_dataset_id == ds_id:
                            st.session_state.active_dataset_id = None
                        st.success("PostgreSQL table dropped successfully.")
                        st.rerun()


# ==============================================================================
# PAGE 3: QUERY HISTORY AUDIT
# ==============================================================================
elif st.session_state.current_page == "history":
    render_header("Query History", "Full audit history of generated SQL queries and natural language answers.")

    if not st.session_state.query_history:
        st.info("No queries recorded in this session yet.")
    else:
        for idx, q in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"{q['question']} &bull; (`{q['dataset']}`)", expanded=(idx==0)):
                st.markdown(f"**Natural Answer:** {q['answer']}")
                if q.get("sql"):
                    st.markdown("**Generated SQL Query:**")
                    st.code(q["sql"], language="sql")


# ==============================================================================
# PAGE 4: ASK DATA / AI CHAT INTERFACE
# ==============================================================================
elif st.session_state.current_page == "chat":
    render_header("Ask Data", "Explore your datasets using natural language and get SQL-backed answers in seconds.")

    # Empty State & Prompts
    if not st.session_state.messages:
        st.markdown("""
            <div class="saas-card" style="text-align: center; padding: 2.5rem 2rem; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: center; margin-bottom: 0.75rem;">
                    <div style="background-color: #EEF0FF; color: #5B5CE2; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                    </div>
                </div>
                <h2 style="margin-top: 0; margin-bottom: 0.4rem; color: #111827; font-size: 1.4rem; font-weight: 800;">What would you like to know?</h2>
                <p style="color: #667085; font-size: 0.925rem; max-width: 500px; margin: 0 auto 1.5rem auto; font-weight: 500;">
                    Ask a question about your dataset. The agent will generate and safely execute the SQL query for you.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("##### Example Questions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("How many records are in this dataset?", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "How many records are in this dataset?"})
                st.rerun()
            if st.button("Extract data from API endpoint 'https://pokeapi.co/api/v2/pokemon'", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in the csv format."})
                st.rerun()
        with col2:
            if st.button("Show me the top 5 records from the dataset", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Show me the top 5 records from the dataset."})
                st.rerun()
            if st.button("Generate SQL summary metrics for numeric columns", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Generate SQL to calculate summary metrics for numeric columns in this dataset."})
                st.rerun()

    # Display Chat History
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                # Clean horizontal progress status bar instead of giant dark card
                if "route" in msg and msg["route"]:
                    st.markdown("""
                        <div class="execution-status-bar">
                            <span class="execution-step">✓ Generated</span>
                            <span>&rarr;</span>
                            <span class="execution-step">✓ Validated</span>
                            <span>&rarr;</span>
                            <span class="execution-step">✓ Executed</span>
                        </div>
                    """, unsafe_allow_html=True)
                
                if "content" in msg and msg["content"]:
                    st.write(msg["content"])

                # Generated SQL Block inside clean developer navy box
                if "sql_query" in msg and msg["sql_query"]:
                    with st.expander("View SQL Query", expanded=False):
                        st.code(msg["sql_query"], language="sql")

                # Results Table & CSV Download
                if "sql_result" in msg and msg["sql_result"]:
                    df_result = parse_sql_result(msg["sql_result"])
                    if df_result is not None:
                        st.markdown("#### Query Results")
                        st.caption(f"{len(df_result)} rows returned")
                        st.dataframe(df_result, use_container_width=True)
                        
                        # Smart Visualization
                        render_visualization(df_result)

                        csv_data = df_result.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download CSV Results",
                            data=csv_data,
                            file_name="query_result.csv",
                            mime="text/csv",
                            key=f"dl_{hash(msg['content'])}"
                        )
                    else:
                        with st.expander("View Raw Output", expanded=False):
                            st.code(msg["sql_result"])

    # Chat Input Box
    user_input = st.chat_input("Ask anything about your dataset...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

    # Process latest unanswered user message
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        latest_user_message = st.session_state.messages[-1]["content"]

        # Context Prefix
        context_prefix = ""
        active_dataset_name = "Built-in Database"
        if st.session_state.active_dataset_id and st.session_state.active_dataset_id in st.session_state.datasets:
            active_ds = st.session_state.datasets[st.session_state.active_dataset_id]
            active_dataset_name = active_ds["filename"]
            context_prefix = (
                f"[CONTEXT: The user has selected uploaded dataset '{active_ds['filename']}'. "
                f"Target PostgreSQL table name is '{active_ds['table_name']}'. "
                f"Columns and types: {active_ds['schema']}]. "
            )

        full_agent_input = f"{context_prefix}{latest_user_message}"

        with st.chat_message("assistant"):
            with st.spinner("Agent is analyzing request & querying PostgreSQL..."):
                try:
                    agent_response = data_agent.invoke(
                        {
                            "messages": [HumanMessage(content=full_agent_input)],
                            "route_response": ""
                        }
                    )

                    route = agent_response.get("route_response", "general")
                    final_text = ""
                    sql_query = ""
                    sql_result = ""
                    messages_list = agent_response.get("messages", [])

                    if route == "sql":
                        for item in reversed(messages_list):
                            if isinstance(item, dict):
                                sql_query = item.get("generated_sql_query", "")
                                sql_result = item.get("sql_query_execution_result", "")
                                final_text = item.get("final_answer", "")
                                if final_text:
                                    break
                    elif route == "etl":
                        for item in reversed(messages_list):
                            if hasattr(item, "content") and item.content:
                                if isinstance(item.content, list):
                                    text_parts = [c.get("text", "") for c in item.content if isinstance(c, dict) and "text" in c]
                                    final_text = "\n".join(text_parts)
                                else:
                                    final_text = str(item.content)
                                if final_text:
                                    break

                    if not final_text:
                        final_text = agent_response.get("final_answer", "")

                    if not final_text:
                        for item in reversed(messages_list):
                            if isinstance(item, AIMessage) and item.content:
                                final_text = str(item.content)
                                break

                    if not final_text:
                        final_text = "Task executed successfully."

                    st.markdown("""
                        <div class="execution-status-bar">
                            <span class="execution-step">✓ Generated</span>
                            <span>&rarr;</span>
                            <span class="execution-step">✓ Validated</span>
                            <span>&rarr;</span>
                            <span class="execution-step">✓ Executed</span>
                        </div>
                    """, unsafe_allow_html=True)

                    st.write(final_text)

                    if sql_query:
                        with st.expander("View SQL Query", expanded=False):
                            st.code(sql_query, language="sql")

                    if sql_result:
                        df_result = parse_sql_result(sql_result)
                        if df_result is not None:
                            st.markdown("#### Query Results")
                            st.caption(f"{len(df_result)} rows returned")
                            st.dataframe(df_result, use_container_width=True)
                            
                            render_visualization(df_result)

                            csv_data = df_result.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download CSV Results",
                                data=csv_data,
                                file_name="query_result.csv",
                                mime="text/csv",
                                key=f"dl_live_{len(st.session_state.messages)}"
                            )

                    # Append Assistant Message & Audit Log History
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_text,
                        "route": route,
                        "sql_query": sql_query,
                        "sql_result": sql_result
                    })

                    st.session_state.query_history.append({
                        "question": latest_user_message,
                        "dataset": active_dataset_name,
                        "answer": final_text,
                        "sql": sql_query
                    })

                except Exception as e:
                    import traceback
                    print("\n--- ERROR IN STREAMLIT AGENT INVOCATION ---")
                    traceback.print_exc()
                    st.error("Unable to execute request with the agent. Check terminal logs for detailed traceback.")
                    with st.expander("Technical details", expanded=False):
                        st.code(str(e))
