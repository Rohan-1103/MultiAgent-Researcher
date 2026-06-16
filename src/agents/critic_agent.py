from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from src.config import settings

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=settings.GROQ_API_KEY)

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

critic_chain = critic_prompt | llm | StrOutputParser()