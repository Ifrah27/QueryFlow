import sys, os, json
sys.path.insert(0, '.')
sys.stdout = open('scratch/debug_out.txt', 'w', encoding='utf-8')
import warnings; warnings.filterwarnings('ignore')
import psycopg2
from dotenv import load_dotenv
load_dotenv()

import backend.main as bm

# Build a realistic in-memory dataset entry from the real heart table (if present)
conn = psycopg2.connect(dbname=os.environ['database'], user=os.environ['user'],
                        password=os.environ['password'], host=os.environ['host'],
                        port=os.environ.get('port', 5432))
cur = conn.cursor()
cur.execute("select table_name from information_schema.tables where table_schema='public' and table_name like 'uploaded_heart%' limit 1")
row = cur.fetchone()
print("HEART TABLE FOUND:", row)
DS_ID = None
if row:
    t = row[0]
    cur.execute("select column_name, data_type from information_schema.columns where table_name=%s order by ordinal_position", (t,))
    schema = {c: d.upper() for c, d in cur.fetchall()}
    DS_ID = 'dbg'
    bm.in_memory_datasets[DS_ID] = {"id": DS_ID, "filename": "heart.csv", "table_name": t, "schema": schema}
conn.close()

# Wrap data_agent to record the RAW returned state
real_invoke = bm.data_agent.invoke
raw = {}
class Wrap:
    def invoke(self, payload):
        out = real_invoke(payload)
        raw['payload'] = payload
        raw['out'] = out
        return out
bm.data_agent = Wrap()

def describe(m):
    if isinstance(m, dict):
        return "DICT keys=%s final_answer=%r sql=%r" % (list(m.keys()), (m.get('final_answer') or '')[:80], (m.get('generated_sql_query') or '')[:60])
    c = getattr(m, 'content', None)
    return "%s content=%r" % (type(m).__name__, str(c)[:110])

qs = ["yo bro", "what are you doing?", "hey", "How are you?", "Delhi is capital of which country?",
      "tell me", "show me", "How many patients have heart disease?", "What is the average cholesterol?",
      "Show me the first 10 records"]
for q in qs:
    print("\n" + "=" * 70)
    print("USER:", q)
    try:
        res = bm.chat_with_agent(bm.ChatRequest(message=q, dataset_id=DS_ID))
    except Exception as e:
        print("EXCEPTION:", type(e).__name__, str(e)[:200]); sys.stdout.flush(); continue
    out = raw['out']
    print("RAW route_response:", out.get('route_response'))
    print("RAW final_answer  :", repr(out.get('final_answer'))[:150])
    for i, m in enumerate(out.get('messages', [])):
        print("  RAW msg[%d]: %s" % (i, describe(m)))
    print("API intent=%s route=%s sql=%r status=%s" % (res.intent, res.route, (res.sql or '')[:50], res.execution_status))
    print("API answer:", repr(res.answer)[:200])
    sys.stdout.flush()
print("\nDONE")
