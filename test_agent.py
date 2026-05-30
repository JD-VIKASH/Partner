import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = "You are a helpful assistant."

@tool("Search")
def Search(query: str) -> str:
    """Useful for searching the web."""
    return "Search results for " + query

tools = [Search]
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0.7)
llm_with_tools = llm.bind_tools(tools)

chat_history = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="cast the search spell for WS audiologist company")]

try:
    response = llm_with_tools.invoke(chat_history)
    print("Success tool calls:", response.tool_calls)
except Exception as e:
    print("Error:", e)
