import os
from dotenv import load_dotenv

# Standard LangChain Core Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Custom tools
from tools import web_search, scrape_url

load_dotenv()

# 1. Base LLM Setup with Cost/Performance Optimizations
# We keep temperature at 0 for deterministic routing and tool calling.
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: GROQ_API_KEY is missing from environment variables.")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# 2. Native Tool Binding
search_llm = llm.bind_tools([web_search])
reader_llm = llm.bind_tools([scrape_url])

# 3. Production Prompts with Context Control

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

reader_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a detailed reading assistant optimized for text extraction.\n\n"
        "CRITICAL RULES:\n"
        "1. Analyze the provided search results and identify the single most high-value URL.\n"
        "2. You MUST execute the `scrape_url` tool using that exact URL to fetch deeper context.\n"
        "3. If a URL seems broken or restricted, attempt another relevant URL immediately."
    )),
    ("human", "{input}")
])

writer_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an elite technical writer specializing in comprehensive industry research reports.\n\n"
        "Your objective is to synthesize raw web search data and deeper scraped page text into a polished markdown document."
    )),
    ("human", """
    Execute an analytical research draft on the following topic.

    Topic: {topic}
    
    ---
    RAW DATA RETRIEVED:
    {research}
    ---

    CRITICAL INSTRUCTIONS FOR REVISIONS:
    If any feedback is provided below, you MUST aggressively modify your writing style, data presentation, or depth to resolve every critique point raised.
    
    CRITIC FEEDBACK FROM PREVIOUS DRAFT:
    {feedback}

    STRUCTURE REQUIREMENTS:
    - # Introduction (Hook the reader, define scope)
    - # Key Findings (Provide at least 3 distinct, deeply elaborated sections with technical insights)
    - # Strategic Conclusion
    - # Sources & References (Enumerate every unique URL utilized in your research data)

    Deliver a highly comprehensive, executive-ready report in clean Markdown format.
    """)
])

critic_prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a strict, senior-level editor and quality compliance agent.\n"
        "Your job is to thoroughly stress-test drafts against factual depth, clarity, and structural adherence."
    )),
    ("human", """
    Review and grade the following research report draft.

    REPORT FOR EVALUATION:
    \"\"\"
    {report}
    \"\"\"

    EVALUATION CRITERIA:
    1. Does it contain an Introduction, 3 deep Key Findings, a Conclusion, and explicit source URLs?
    2. Is the formatting professional and ready for executive review?
    3. Is it concrete and free of generic AI-generated filler?

    OUTPUT RULES & FORMATTING:
    Provide your review. You must conclude your evaluation with a single word verdict on the final line.
    - Write 'Verdict: APPROVED' if the report meets all standards perfectly.
    - Write 'Verdict: REJECTED' if the writer needs to add content, fix structure, or deepen insights.

    FORMAT:
    ### Quality Score: X/10
    ### Strengths
    - ...
    ### Areas to Refine
    - ...
    
    Verdict: [APPROVED or REJECTED]
    """)
])

# 4. Runnable Expressive Infrastructure (LCEL Engine)
# Notice we pass raw message outputs from tool-bound LLMs to match LangGraph expectations
search_agent = search_prompt | search_llm
reader_agent = reader_prompt | reader_llm

writer_chain = writer_prompt | llm | StrOutputParser()
critic_chain = critic_prompt | llm | StrOutputParser()