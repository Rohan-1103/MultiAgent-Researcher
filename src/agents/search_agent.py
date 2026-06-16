from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from src.config import settings
from src.tools import web_search

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=settings.GROQ_API_KEY)
search_llm = llm.bind_tools([web_search])

search_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert research specialist operating within an automated multi-agent framework. "
        "Your goal is to gather high-density, accurate, and recent background information.\n\n"
        "CRITICAL RULES:\n"
        "1. You MUST execute the `web_search` tool to uncover real facts. Never assume info.\n"
        "2. Keep search queries brief, distinct, and keyword-focused (no conversational fluff)."
    )),
    ("human", "{input}")
])

search_agent = search_prompt | search_llm