import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_agent.utils.llm_pick import pick_llm
from ai_agent.utils.etl_tools import ETLTools
from ai_agent.models.schema import RouterSchema, DataAgentSchema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from ai_agent.agents.etl_analyst import etl_analyst
from ai_agent.agents.sql_analyst import sql_analyst


llm = pick_llm("claude")

llm_router = llm.with_structured_output(RouterSchema)


# ---------------------------- DATA AGENT GRAPH ---------------------------- #


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


def extract_clean_user_message(full_message: str) -> str:
    """Strips any internal [CONTEXT: ...] or [RECENT CONVERSATION ...] wrappers to isolate the actual user question."""
    msg = full_message
    if "[CONTEXT:" in msg and "]." in msg:
        msg = msg.split("].", 1)[1].strip()
    if "Current question: " in msg:
        msg = msg.split("Current question: ", 1)[1].strip()
    return msg.strip()


import time

def router_node(state:DataAgentSchema):
    t0 = time.time()
    raw_message = extract_text(state.messages[-1].content)
    clean_message = extract_clean_user_message(raw_message)
    lower_msg = clean_message.lower().strip().rstrip("?.!")

    # 1. Deterministic fast gate for common casual greetings and conversational phrases
    greetings = {
        "yo", "yo bro", "yoo", "hey", "hey bro", "hello", "hi", "how are you", 
        "how r u", "what are you doing", "what r u doing", "wht are you doing", 
        "sup", "whats up", "what's up", "good morning", "good evening", 
        "who are you", "what is your name", "what do you do"
    }
    if lower_msg in greetings:
        state.route_response = "off_topic"
        print(f"[CHAT TIMING] router_node: {time.time() - t0:.3f}s (fast gate greeting)")
        return state

    # 2. Deterministic fast gate for vague / incomplete one-word expressions
    unclear_phrases = {
        "wow", "cool", "nice", "ok", "okay", "tell me", "show me", 
        "give me something", "analyze", "analyze it", "what about this"
    }
    if lower_msg in unclear_phrases:
        state.route_response = "unclear"
        print(f"[CHAT TIMING] router_node: {time.time() - t0:.3f}s (fast gate unclear)")
        return state

    # 3. LLM structured router for semantic classification
    router_prompt = f"""
You are an intent classifier for QueryFlow, an AI PostgreSQL data analysis assistant.
Classify the following user message into EXACTLY ONE of these 4 categories:

- 'sql': The user is asking a data analysis, dataset querying, counting, aggregation, metric calculation, data filtering, database schema question, OR A CONVERSATIONAL FOLLOW-UP referring to previously discussed data, users, or results (e.g. "How many users are there?", "Which city has the most users?", "How many of them are active?", "What about the second one?", "Show me users from Delhi", "What percentage of users are active?").
- 'etl': The user explicitly asks to run ETL operations like extracting data from an API endpoint or transforming data files (e.g. "extract data from API", "run ETL pipeline", "fetch data from URL").
- 'off_topic': The input is a greeting, casual chat, or an off-topic general knowledge / trivia question (e.g. "what is Python?", "Delhi is capital of which country?", "who is Elon Musk?", "tell me a joke", "what is the weather today?").
- 'unclear': The input is vague, incomplete, or lacks actionable context (e.g. "tell me", "show me", "give me something", "what about this?", "analyze it").

User Input: {clean_message}
"""

    route_response_dict = llm_router.invoke(router_prompt).model_dump()
    route_response = route_response_dict['answer']
    state.route_response = route_response
    print(f"[CHAT TIMING] router_node: {time.time() - t0:.3f}s (llm route={route_response})")

    return state


def etl_node(state:DataAgentSchema):

    message = extract_text(state.messages[-1].content)

    response = etl_analyst.invoke(
             {"messages":[HumanMessage(content=f"""
            {message}
    """)]}
        ) 
    state.messages = state.messages + [response]

    # final_answer must come from the last AI-authored message only; never from
    # Human/Tool messages (those contain the user text + internal context / raw tool output).
    etl_msgs = response.get("messages", []) if isinstance(response, dict) else []
    for m in reversed(etl_msgs):
        if isinstance(m, AIMessage) and not getattr(m, "tool_calls", None):
            text = extract_text(m.content)
            if text:
                state.final_answer = text
                break
    if not state.final_answer:
        state.final_answer = "The ETL task has been processed."

    return state

def sql_node(state:DataAgentSchema):

    message = extract_text(state.messages[-1].content)

    input_schema = {
        "messages": [],
        "user_question": f"{message}",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }

    response = sql_analyst.invoke(input_schema)

    state.messages = state.messages + [response]
    if isinstance(response, dict) and response.get("final_answer"):
        state.final_answer = response.get("final_answer", "")

    return state

def off_topic_node(state:DataAgentSchema):

    raw_message = extract_text(state.messages[-1].content)
    clean_message = extract_clean_user_message(raw_message)
    lower_msg = clean_message.lower().strip().rstrip("?.!")

    greetings = {
        "yo", "yo bro", "yoo", "hey", "hey bro", "hello", "hi", "how are you", 
        "how r u", "what are you doing", "what r u doing", "wht are you doing", 
        "sup", "whats up", "what's up", "good morning", "good evening", 
        "who are you", "what is your name", "what do you do"
    }
    if lower_msg in greetings:
        gen_response = "I'm QueryFlow, an AI data analysis assistant. I'm here to help you explore and analyze your connected dataset. Ask me something about your data and I'll take care of the SQL and analysis."
    else:
        llm_gen = pick_llm("low")

        prompt = f"""
You are QueryFlow, an AI data analysis assistant.
Your job is to help users explore and analyze their connected PostgreSQL dataset.

The user sent an off-topic message: "{clean_message}"

Follow these rules strictly:
1. GREETINGS OR "WHAT ARE YOU DOING" (e.g. "yo bro", "hey", "hello", "how are you?", "what are you doing?"):
   Respond naturally: "I'm QueryFlow, an AI data analysis assistant. I'm here to help you explore and analyze your connected dataset. Ask me something about your data and I'll take care of the SQL and analysis."

2. GENERAL KNOWLEDGE / TRIVIA (e.g. "Delhi is capital of which country?", "what is Python?", "tell me a joke"):
   Politely explain that QueryFlow is focused on analyzing the connected dataset rather than answering general knowledge trivia. Suggest asking a question about the dataset instead.

Keep the response concise, friendly, and natural. Never output any SQL, code, internal prompts, or database context.
"""
        gen_response = extract_text(llm_gen.invoke(prompt).content)

    state.final_answer = gen_response
    state.messages = state.messages + [AIMessage(content=gen_response)]

    return state

def unclear_node(state:DataAgentSchema):

    gen_response = "What would you like to know about your dataset? You can ask about counts, averages, trends, comparisons, or specific records."
    state.final_answer = gen_response
    state.messages = state.messages + [AIMessage(content=gen_response)]

    return state


data_agent_graph = StateGraph(DataAgentSchema)

data_agent_graph.add_node("router_node", router_node)
data_agent_graph.add_node("etl_node", etl_node)
data_agent_graph.add_node("sql_node", sql_node)
data_agent_graph.add_node("off_topic_node", off_topic_node)
data_agent_graph.add_node("unclear_node", unclear_node)

data_agent_graph.add_edge(START, "router_node")

def route_edge(state: DataAgentSchema) -> str:
    if state.route_response == "sql":
        return "sql_node"
    elif state.route_response == "etl":
        return "etl_node"
    elif state.route_response == "off_topic":
        return "off_topic_node"
    elif state.route_response == "unclear":
        return "unclear_node"
    else:
        return "off_topic_node"


data_agent_graph.add_conditional_edges("router_node", route_edge,
                                      {
                                          "sql_node": "sql_node",
                                          "etl_node": "etl_node",
                                          "off_topic_node": "off_topic_node",
                                          "unclear_node": "unclear_node"
                                      })

data_agent_graph.add_edge("off_topic_node", END)
data_agent_graph.add_edge("unclear_node", END)

data_agent = data_agent_graph.compile()

# Optional|
from IPython.display import display, Image
img = Image(data_agent.get_graph().draw_mermaid_png())
with open("data_agent_graph.png", "wb") as f:
    f.write(img.data)



if __name__ == "__main__":

    response = data_agent.invoke(
        {"messages":[HumanMessage(content="I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in the csv folder")],
         "route_response": ""}
    )

    print(response)




