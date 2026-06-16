from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from src.config import settings

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=settings.GROQ_API_KEY)

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

writer_chain = writer_prompt | llm | StrOutputParser()