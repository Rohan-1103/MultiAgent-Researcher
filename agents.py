import os
from dotenv import load_dotenv

# Standard LangChain Core Imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

# Custom tools
from tools import web_search, scape_url

load_dotenv()

# Base LLM Setup
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# Bind tools directly to the model instance (Native Tool Calling)
search_llm = llm.bind_tools([web_search])
reader_llm = llm.bind_tools([scape_url])

# Base Prompts for Agents
search_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert search assistant. Find relevant information quickly. "
               "Always call your available tools to discover facts."),
    ("human", "{input}")
])

reader_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a detailed reading assistant. Extract and summarize web content accurately. "
               "Always use your scraping tools to extract the full webpage content."),
    ("human", "{input}")
])

# Runnable Agent Chains
search_agent = search_prompt | search_llm
reader_agent = reader_prompt | reader_llm

# --- Synchronous LLM Chains (No tools needed) ---

# Writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, and insightful reports."),
    ("human", """Write a detailed research on the topic below.
     
     Topic: {topic}
     Research Gathered: {research}
     
     Structure the report as: 
     - Introduction
     - Key findings (Min. 3 well explained points)
     - Conclusion
     - Sources (list all URLs found in the research)
     
     Be detailed, factual, and professional."""),
])
writer_chain = writer_prompt | llm | StrOutputParser()
    
# Critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.
     
     Report: {report}
     
     Respond in this exact format:
      Score: X/10
      
      Strengths:
       - ...
       - ... 
       
      Areas to Improve: 
       - ... 
       - ... 
       
      One line verdict:
      ..."""),
])
critic_chain = critic_prompt | llm | StrOutputParser()
