from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from src.config import settings
from src.tools.scraper import scrape_url

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=settings.GROQ_API_KEY)

# [CRITICAL UPDATE]: Enforce 'tool_choice' to guarantee URL extraction
reader_llm = llm.bind_tools([scrape_url], tool_choice="scrape_url")

reader_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a detailed reading assistant optimized for precise text extraction and data collection.\n\n"
        "YOUR OBJECTIVE:\n"
        "Analyze the provided search data, pick the absolute most high-value reference website URL, and pass it to the `scrape_url` tool.\n\n"
        "CRITICAL RULES FOR TOOL CALLING:\n"
        "1. NEVER pass a search engine URL (e.g., google.com/search?q=...) or an internal search tracking redirection link to the tool.\n"
        "2. ONLY extract the destination target website URL (e.g., 'https://towardsdatascience.com/article-slug').\n"
        "3. Strip all trailing reference tracking elements (like '?utm_source=...', '&rlz=...', or '&sxsrf=...') before supplying the argument to the tool.\n"
        "4. If your selected destination URL returns an error or fails, fallback and execute `scrape_url` on an alternative resource from the search history index instantly."
    )),
    ("human", "{input}")
])

reader_agent = reader_prompt | reader_llm