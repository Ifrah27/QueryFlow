import sys
sys.path.insert(0, '.')
sys.stdout = open('scratch/debug_out3.txt', 'w', encoding='utf-8')
import warnings; warnings.filterwarnings('ignore')
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import ai_agent.agents.data_agent as da
import backend.main as bm

CTX = "[CONTEXT: The user has selected uploaded dataset 'heart.csv'. Target PostgreSQL table name is 'uploaded_heart_9b85d1'.]. "

# --- A. Reproduce the PREVIOUS backend extraction (verbatim from the pre-fix code) on a realistic ETL-route state
def old_extract(messages_list):
    final_text = ""
    for item in reversed(messages_list):
        if hasattr(item, "content") and item.content:
            if isinstance(item.content, list):
                final_text = "\n".join(c.get("text", "") for c in item.content if isinstance(c, dict) and "text" in c)
            else:
                final_text = str(item.content)
            if final_text:
                break
    return final_text or "Task executed successfully."

etl_dict = {"messages": [HumanMessage(content="yo bro"), AIMessage(content=[{"type": "text", "text": "Hi! How can I help?"}])]}
state_msgs = [HumanMessage(content=CTX + "yo bro")] * 2 + [etl_dict]   # etl_node appends a DICT to state.messages
print("A. OLD extraction on ETL-route state ->", repr(old_extract(state_msgs))[:140])

# --- B. Same state through CURRENT etl_node + CURRENT backend
class StubETL:
    def invoke(self, p):
        return etl_dict
da.etl_analyst = StubETL()
st = da.DataAgentSchema(messages=[HumanMessage(content=CTX + "yo bro")], route_response='etl')
out = da.etl_node(st)
print("B. CURRENT etl_node.final_answer     ->", repr(out.final_answer))

# --- C. ETL answer when the model returns content blocks (Gemini style) and last msg is a ToolMessage
etl_dict2 = {"messages": [HumanMessage(content="x"), AIMessage(content=[{"type": "text", "text": "ok"}]), ToolMessage(content="raw tool output: rows=3", tool_call_id="1")]}
class StubETL2:
    def invoke(self, p): return etl_dict2
da.etl_analyst = StubETL2()
st = da.DataAgentSchema(messages=[HumanMessage(content="x")], route_response='etl')
print("C. ETL last message is ToolMessage    ->", repr(da.etl_node(st).final_answer))

# --- D. Cost of an LLM failure (429): what does the user see?
class Boom:
    def invoke(self, p): raise RuntimeError("429 RESOURCE_EXHAUSTED")
real = bm.data_agent
bm.data_agent = Boom()
try:
    bm.chat_with_agent(bm.ChatRequest(message="hey", dataset_id=None))
except Exception as e:
    print("D. LLM failure ->", type(e).__name__, getattr(e, 'status_code', None), str(getattr(e, 'detail', e))[:90])
print("DONE")
