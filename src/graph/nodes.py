import sys
from src.graph.state import ResearchState
from src.agents import search_agent, reader_agent, writer_chain, critic_chain

def call_search_agent(state: ResearchState) -> dict:
    """
    Node 1: Executes the Search Agent to extract web context.
    Swallows tool calls internally or returns the raw message content.
    """
    print("\n🚀 [Node: Search] Analysing research scope and running web indices...", flush=True)
    
    # We pass a highly structured prompt string to guide Llama-3.3-70b
    response = search_agent.invoke({"input": f"Find recent, reliable information about: {state['topic']}"})
    
    # Check if the LLM generated structural tool calls natively
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # LangGraph's ToolNode will pick this up automatically if connected, 
        # or we return a fallback placeholder to notify the state.
        return {"search_results": f"Tool Execution Requested: {response.tool_calls[0]['name']}"}
        
    return {"search_results": response.content}


def call_reader_agent(state: ResearchState) -> dict:
    """
    Node 2: Selects key candidate URLs and processes them via the deep scraping pipeline.
    """
    print("\n📖 [Node: Reader] Processing top search results and extracting deep text...", flush=True)
    
    # Prevent crashing if search results are completely empty
    search_context = state.get("search_results", "No search results available.")
    
    prompt_input = (
        f"Based on the following search results about '{state['topic']}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{search_context}"
    )
    
    response = reader_agent.invoke({"input": prompt_input})
    return {"scraped_content": response.content}


def call_writer_chain(state: ResearchState) -> dict:
    """
    Node 3: Formulates or updates the markdown report draft, integrating previous feedback loops.
    """
    print("\n📝 [Node: Writer] Generating or refining the technical research report...", flush=True)
    
    # Combine collected intelligence layers
    research_combined = (
        f"SEARCH ENGINE HIGHLIGHTS:\n{state.get('search_results', '')}\n\n"
        f"DEEP SCRAPED CONTENT:\n{state.get('scraped_content', '')}"
    )
    
    # Dynamic context injection: If feedback exists from a previous loop, extract it
    previous_feedback = state.get("feedback", "No historical feedback. This is the first draft.")
    
    # Execute LCEL chain
    report_markdown = writer_chain.invoke({
        "topic": state['topic'],
        "research": research_combined,
        "feedback": previous_feedback
    })
    
    # Safely step up loop iterations to track our convergence run
    current_loops = state.get("loop_count", 0)
    
    return {
        "report": report_markdown, 
        "loop_count": current_loops + 1
    }


def call_critic_chain(state: ResearchState) -> dict:
    """
    Node 4: Evaluates the compiled draft against quality and compliance guidelines.
    """
    print("\n🧐 [Node: Critic] Stress-testing document structure and compliance...", flush=True)
    
    report_to_assess = state.get("report", "Empty draft. Assessment aborted.")
    
    # Run the validation chain
    evaluation_logs = critic_chain.invoke({"report": report_to_assess})
    
    return {"feedback": evaluation_logs}