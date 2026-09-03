import sys, os, collections
sys.path.insert(0, '.')
sys.stdout = open('scratch/debug_out2.txt', 'w', encoding='utf-8')
import warnings; warnings.filterwarnings('ignore')
from dotenv import load_dotenv; load_dotenv()
from langchain_core.messages import HumanMessage, AIMessage
import ai_agent.agents.data_agent as da

CTX = ("[CONTEXT: The user has selected uploaded dataset 'heart.csv'. Target PostgreSQL table name is 'uploaded_heart_9b85d1'. "
       "Columns and types: {'age': 'BIGINT', 'sex': 'TEXT', 'cholesterol': 'BIGINT', 'heartdisease': 'BIGINT'}]. ")

def route(text):
    st = da.DataAgentSchema(messages=[HumanMessage(content=text)], route_response='')
    return da.router_node(st).route_response

print("=== EXP1: router distribution (6 runs each) ===")
for q in ["yo bro", "what are you doing", "hey", "how are you?", "Delhi is capital of which country?", "tell me"]:
    with_ctx = collections.Counter(route(CTX + q) for _ in range(6))
    no_ctx = collections.Counter(route(q) for _ in range(6))
    print(f"{q!r:40} WITH_CTX={dict(with_ctx)}  CLEAN={dict(no_ctx)}")
    sys.stdout.flush()

print("\n=== EXP2: follow-up with no history (API only gets the single message) ===")
for q in ["How many of them are male?", "What about the second one?"]:
    print(q, "->", collections.Counter(route(CTX + q) for _ in range(4)))
    sys.stdout.flush()

print("\n=== EXP3: etl_node answer shape (etl_analyst stubbed, no network) ===")
class StubETL:
    def invoke(self, payload):
        return {"messages": payload["messages"] + [AIMessage(content=[{"type": "text", "text": "Done extracting."}])]}
da.etl_analyst = StubETL()
st = da.DataAgentSchema(messages=[HumanMessage(content=CTX + "yo bro")], route_response='etl')
out = da.etl_node(st)
print("etl_node final_answer =", repr(out.final_answer))
print("messages types        =", [type(m).__name__ for m in out.messages])

print("\n=== EXP4: reducer duplication through the real compiled graph ===")
res = da.data_agent.invoke({"messages": [HumanMessage(content="hey")], "route_response": ""})
print("types:", [type(m).__name__ for m in res['messages']], "route:", res['route_response'])
print("\nDONE")
