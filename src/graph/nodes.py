import sys
from src.graph.state import ResearchState
from src.agents import search_agent, reader_agent, writer_chain, critic_chain

def call_search_agent(state: ResearchState) -> dict:
    """Invokes the search agent. Returns the raw model response."""
    print("\n🚀 [Node: Search] Analyzing scope...", flush=True)
    response = search_agent.invoke({"input": f"Find recent, reliable information about: {state['topic']}"})
    
    # Senior Upgrade: If the LLM requests a tool call, we store the raw AIMessage object 
    # inside a temporary internal dictionary key so LangGraph's ToolNode can read it.
    if hasattr(response, 'tool_calls') and response.tool_calls:
        return {"messages": [response]}
    return {"search_results": response.content}


def call_reader_agent(state: ResearchState) -> dict:
    """Invokes the reader agent based on the updated search results."""
    print("\n📖 [Node: Reader] Contextualizing resources...", flush=True)
    prompt_input = (
        f"Based on the following search results about '{state['topic']}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{state.get('search_results', '')}"
    )
    response = reader_agent.invoke({"input": prompt_input})
    
    if hasattr(response, 'tool_calls') and response.tool_calls:
        return {"messages": [response]}
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