import sys
sys.path.insert(0, '.')
sys.stdout.reconfigure(encoding='utf-8')
from backend.main import app, ChatRequest, chat_with_agent

cases = [
    (1, "yo bro"),
    (2, "what are you doing?"),
    (3, "Delhi is capital of which country?"),
    (4, "tell me"),
    (5, "How many patients have heart disease?"),
    (6, "What is the average cholesterol?"),
    (7, "Show me the first 10 records"),
    (8, "How many users are there?"),
    (9, "How many of them are active?"),
]

print("=== STARTING COMPLETE PIPELINE TEST VERIFICATION ===")
for num, q in cases:
    req = ChatRequest(message=q, dataset_id=None)
    res = chat_with_agent(req)
    
    print(f"\n[Case {num}] User: \"{q}\"")
    print(f"-> INTENT: {res.intent}")
    print(f"-> ROUTE: {res.route}")
    print(f"-> SQL: {res.sql}")
    print(f"-> EXECUTION STATUS: {res.execution_status}")
    print(f"-> ANSWER:\n{res.answer.strip()}")
    
    # Check assertions:
    assert "[CONTEXT:" not in res.answer, "Leakage bug: [CONTEXT: found in answer!"
    assert "HumanMessage" not in res.answer, "Leakage bug: HumanMessage found in answer!"
    assert "AIMessage" not in res.answer, "Leakage bug: AIMessage found in answer!"
    
    if res.intent in ["off_topic", "unclear"]:
        assert res.sql is None, f"Bug: SQL generated for {res.intent} query!"
        assert res.execution_status is None, f"Bug: execution_status present for {res.intent} query!"
        assert res.answer != q, f"Bug: User question echoed as assistant answer for {q}!"

print("\n==========================================")
print("ALL 10 VERIFICATION TEST CASES PASSED SUCCESSFULLY!")
print("==========================================")
