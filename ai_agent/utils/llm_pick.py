import os
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

def pick_llm(level: str):
    """
    Picks the appropriate LLM based on the level of the question.
    Uses Groq or Gemini depending on configured keys.
    """
    if os.getenv("GEMINI_API_KEY"):
        return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0)
        
    if os.getenv("GROQ_API_KEY"):
        return ChatGroq(model_name="openai/gpt-oss-120b", temperature=0)
        
    raise ValueError("No valid API keys found in environment.")

if __name__ == "__main__":
    llm_obj = pick_llm("low")  
    print(llm_obj.invoke("What is the capital of France?"))
