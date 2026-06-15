from typing import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our agents and chains
from agents import search_agent, reader_agent, writer_chain, critic_chain, web_search, scape_url

# Define state structure shared across agents
class ResearchState(TypedDict):
    topic: str
    search_results: str
    scraped_content: str
    report: str
    feedback: str

# Node 1: Run Search Agent
def call_search_agent(state: ResearchState):
    print("\n" + "="*50 + "\nStep 1 - Search agent is working ...\n" + "="*50)
    response = search_agent.invoke({"input": f"Find recent, reliable information about: {state['topic']}"})
    
    # Execute tool if the model requested it
    if response.tool_calls:
        tool_output = web_search.invoke(response.tool_calls[0]['args'])
        return {"search_results": str(tool_output)}
    return {"search_results": response.content}

# Node 2: Run Reader Agent
def call_reader_agent(state: ResearchState):
    print("\n" + "="*50 + "\nStep 2 - Reader agent is scraping resources ...\n" + "="*50)
    prompt_input = (
        f"Based on the following search results about '{state['topic']}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{state['search_results'][:800]}"
    )
    response = reader_agent.invoke({"input": prompt_input})
    
    # Execute tool if the model requested it
    if response.tool_calls:
        tool_output = scape_url.invoke(response.tool_calls[0]['args'])
        return {"scraped_content": str(tool_output)}
    return {"scraped_content": response.content}

# Node 3: Run Writer Chain
def call_writer_chain(state: ResearchState):
    print("\n" + "="*50 + "\nStep 3 - Writer is drafting the report ...\n" + "="*50)
    research_combined = f"SEARCH RESULTS:\n{state['search_results']}\n\nDETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    report = writer_chain.invoke({"topic": state['topic'], "research": research_combined})
    return {"report": report}

# Node 4: Run Critic Chain
def call_critic_chain(state: ResearchState):
    print("\n" + "="*50 + "\nStep 4 - Critic is reviewing the report ...\n" + "="*50)
    feedback = critic_chain.invoke({"report": state['report']})
    print("\n--- Final Critic Feedback ---\n", feedback)
    return {"feedback": feedback}

# Build Orchestration Graph
workflow = StateGraph(ResearchState)

# Add processing blocks
workflow.add_node("search", call_search_agent)
workflow.add_node("reader", call_reader_agent)
workflow.add_node("writer", call_writer_chain)
workflow.add_node("critic", call_critic_chain)

# Map linear flow execution path
workflow.set_entry_point("search")
workflow.add_edge("search", "reader")
workflow.add_edge("reader", "writer")
workflow.add_edge("writer", "critic")
workflow.add_edge("critic", END)

# Compile graph into a runnable application
app = workflow.compile()

if __name__ == "__main__":
    user_topic = input("\nEnter a research topic: ")
    final_state = app.invoke({"topic": user_topic})
    print("\nPipeline Complete!")