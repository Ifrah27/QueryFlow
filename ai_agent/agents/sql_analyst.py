import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_agent.utils.llm_pick import pick_llm
from ai_agent.utils.database import DatabaseUtil
from ai_agent.models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END


# -------------------------------------- AI Agent Code--------------------------------------

def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(str(item.get("text", "")))
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts).strip()
    return str(content)


import time
import re

def curate_ques(state: AgentSchema) -> AgentSchema:
    t0 = time.time()
    user_question = extract_text(state.user_question)
    
    # Fast path: Use user question directly without redundant LLM rewriting roundtrip
    state.curated_ques = user_question
    state.messages = state.messages + [HumanMessage(content=f"{user_question}")]
    print(f"[CHAT TIMING] curate_ques: {time.time() - t0:.3f}s (bypassed LLM call)")
    return state


def prompt_query_context(state: AgentSchema) -> AgentSchema:
    t0 = time.time()
    curated_question = state.curated_ques

    obj = DatabaseUtil()
    schema_info = obj.schema_details("public")

    prompt = f"""
    You are an SQL analyst agent. Your task is to convert the user's natural language 
    query into Postgres SQL query that can be executed on the database. You are provided 
    with the user's original query and the schema details of the database, including
    table names, column names, data types, and sample data for each table so that 
    you can understand the structure of the database and generate an accurate SQL query.
    Unless user explicitly asks for specific number of rows, always limit the output to 10 rows.
    Note - Just generate the SQL query without any explanation or additional text because
    this query will be executed directly on the database. So, the output should be SQL
    ready to be executed without any modifications.  
    
    User's Original Query: {curated_question}

    Database Schema Details:
    {schema_info}
    """    

    state.prompt_query_context = prompt
    print(f"[CHAT TIMING] prompt_query_context: {time.time() - t0:.3f}s")
    return state


def generate_sql(state: AgentSchema) -> AgentSchema:
    t0 = time.time()
    prompt = state.prompt_query_context

    llm = pick_llm("medium")
    generated_sql_query = extract_text(llm.invoke(prompt).content)
    generated_sql_query = generated_sql_query.strip().strip("```").lstrip("sql").strip()

    state.generated_sql_query = generated_sql_query
    print(f"[CHAT TIMING] generate_sql: {time.time() - t0:.3f}s")
    return state


def validate_sql_safety(sql: str) -> tuple[bool, str]:
    """
    Robust deterministic read-only SQL validator.
    Allows: SELECT, WITH ... SELECT
    Rejects: INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, GRANT, REVOKE, MERGE, CALL, EXECUTE, COPY, multiple statements.
    """
    if not sql or not isinstance(sql, str):
        return False, "Empty or invalid SQL query format."
    
    clean_sql = sql.strip().rstrip(";")
    
    # Rejects multiple statements separated by semicolon
    if ";" in clean_sql:
        return False, "Multiple SQL statements separated by ';' are prohibited."

    # Remove SQL comments (-- comment and /* comment */)
    no_comments = re.sub(r'--.*?\n', ' ', clean_sql)
    no_comments = re.sub(r'/\*.*?\*/', ' ', no_comments, flags=re.DOTALL).strip()

    # Rejects mutating keywords
    forbidden_pattern = r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|CREATE|GRANT|REVOKE|MERGE|CALL|EXECUTE|COPY)\b'
    match = re.search(forbidden_pattern, no_comments, flags=re.IGNORECASE)
    if match:
        return False, f"SQL command contained forbidden mutating keyword '{match.group(1).upper()}'."

    # Must start with SELECT or WITH
    first_word = no_comments.split()[0].upper() if no_comments.split() else ""
    if first_word not in ("SELECT", "WITH"):
        return False, f"SQL statement must start with SELECT or WITH, received '{first_word}'."

    return True, "Query is safe."


def is_safe_sql(state: AgentSchema) -> AgentSchema:
    t0 = time.time()
    sql_query = state.generated_sql_query

    is_safe, comment = validate_sql_safety(sql_query)
    state.is_safe = "Yes" if is_safe else "No"
    state.comments = comment
    print(f"[CHAT TIMING] is_safe_sql: {time.time() - t0:.3f}s (deterministic check, safe={is_safe})")
    return state


def canceled_sql(state: AgentSchema) -> AgentSchema:
    comments = state.comments
    state.final_answer = f"The generated SQL query was deemed unsafe to execute. Reason: {comments}"
    state.messages = state.messages + [AIMessage(content=f"{state.final_answer}")]
    return state


def execute_sql(state: AgentSchema) -> AgentSchema:
    t0 = time.time()
    sql_query = state.generated_sql_query

    obj = DatabaseUtil()
    execution_result = obj.execute_sql(sql_query)

    state.sql_query_execution_result = execution_result
    print(f"[CHAT TIMING] execute_sql: {time.time() - t0:.3f}s")
    return state


def represent_final_answer(state: AgentSchema) -> AgentSchema:
    t0 = time.time()
    execution_result = state.sql_query_execution_result
    curated_question = state.curated_ques

    # Fast-path: Check for simple single-value / single-count execution result
    if execution_result and execution_result.startswith("[(") and execution_result.endswith(")]"):
        try:
            import ast
            rows = ast.literal_eval(execution_result)
            if len(rows) == 1 and len(rows[0]) == 1:
                val = rows[0][0]
                q_lower = curated_question.lower()
                if "how many" in q_lower or "count" in q_lower or "number of" in q_lower:
                    answer = f"There are {val:,} records matching your query in the dataset."
                else:
                    answer = f"The result is {val}."
                state.final_answer = answer
                state.messages = state.messages + [AIMessage(content=answer)]
                print(f"[CHAT TIMING] represent_final_answer: {time.time() - t0:.3f}s (deterministic formatting)")
                return state
        except Exception:
            pass

    # Fallback to LLM for complex interpretation
    llm = pick_llm("low")
    prompt = f"""
    You are an SQL analyst agent. Your task is to provide a final answer to the user based on the
    execution result of the SQL query and the user's original question. The final answer should be
    concise, clear, and directly address the user's query. Avoid including any SQL code or technical
    details in the final answer. The final answer should be in a user-friendly format that is easy to
    understand. If the execution result is empty or does not provide a clear answer to the user's question, explain this in the final answer. \n
    Here is the execution result: {execution_result} \n
    Here is the user's original question: {curated_question}
    """

    llm_response = extract_text(llm.invoke(prompt).content)
    state.final_answer = llm_response
    state.messages = state.messages + [AIMessage(content=f"{llm_response}")]
    print(f"[CHAT TIMING] represent_final_answer: {time.time() - t0:.3f}s (LLM interpretation)")
    return state



# ------------------------------------------- Graph Building -------------------------------------------

sql_agent_graph = StateGraph(AgentSchema)

# Nodes
sql_agent_graph.add_node(curate_ques,name="curate_ques")
sql_agent_graph.add_node(prompt_query_context,name="prompt_query_context")
sql_agent_graph.add_node(generate_sql,name="generate_sql")
sql_agent_graph.add_node(is_safe_sql,name="is_safe_sql")
sql_agent_graph.add_node(canceled_sql,name="canceled_sql")
sql_agent_graph.add_node(execute_sql,name="execute_sql")
sql_agent_graph.add_node(represent_final_answer,name="represent_final_answer")

# Edges
sql_agent_graph.add_edge(START, "curate_ques")
sql_agent_graph.add_edge("curate_ques", "prompt_query_context")
sql_agent_graph.add_edge("prompt_query_context", "generate_sql")
sql_agent_graph.add_edge("generate_sql", "is_safe_sql")

# Codintional Edge Function
def is_safe_sql_edge(state: AgentSchema) -> str:
    is_safe = state.is_safe

    if is_safe.lower() == "yes":
        return "execute_sql"

    else :
        return "canceled_sql"

sql_agent_graph.add_conditional_edges("is_safe_sql", is_safe_sql_edge,
                                      {
                                          "execute_sql": "execute_sql",
                                          "canceled_sql": "canceled_sql"
                                      })

# sql_agent_graph.add_edge("is_safe_sql", "execute_sql")
# sql_agent_graph.add_edge("is_safe_sql", "canceled_sql")

sql_agent_graph.add_edge("canceled_sql", END)
sql_agent_graph.add_edge("execute_sql", "represent_final_answer")
sql_agent_graph.add_edge("represent_final_answer", END)

# Compile the Graph
sql_analyst = sql_agent_graph.compile()

if __name__ == "__main__":


    # Optional
    from IPython.display import display, Image
    img = Image(sql_analyst.get_graph().draw_mermaid_png())
    with open("sql_analyst_graph.png", "wb") as f:
        f.write(img.data)

    input_schema = {
        "messages": [],
        "user_question": "What are the different types of Payment Methods we have in our database",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }

    # Execute the Graph
    sql_analyst_response = sql_analyst.invoke(input_schema)
    print(sql_analyst_response['messages'])  # Print the final output of the graph execution
    print("********************************")

    print(sql_analyst_response['generated_sql_query'])  # Print the generated SQL query

    print("********************************")

    print(sql_analyst_response['sql_query_execution_result'])  # Print the result of executing the SQL query

    print("********************************")

    print(sql_analyst_response['prompt_query_context'])  # Print the prompt query context
