from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# Import our agents, chains, and tools
from agents import search_agent, reader_agent, writer_chain, critic_chain, web_search, scape_url

# 1. Enhanced State Management
class ResearchState(TypedDict):
    topic: str
    search_results: str
    scraped_content: str
    report: str
    feedback: str
    loop_count: int  # Prevent infinite loops between Writer and Critic

# 2. Node Definitions (Strictly Model Invocations)
def call_search_agent(state: ResearchState):
    print("\n🚀 [Node: Search] Analysing research scope...")
    # We pass the entire message history or string; LangGraph natively checks for tool_calls
    response = search_agent.invoke({"input": f"Find recent, reliable information about: {state['topic']}"})
    
    # Check if the agent decided to call a tool
    if response.tool_calls:
        return {"search_results": "tool_called", "messages": [response]} 
    return {"search_results": response.content}

def call_reader_agent(state: ResearchState):
    print("\n📖 [Node: Reader] Contextualizing resources...")
    prompt_input = (
        f"Based on the following search results about '{state['topic']}', "
        f"pick the most relevant URL and scrape it for deeper content.\n\n"
        f"Search Results:\n{state['search_results']}" # Let the LLM read full context or handle via system prompt
    )
    response = reader_agent.invoke({"input": prompt_input})
    return {"scraped_content": response.content}

def call_writer_chain(state: ResearchState):
    print("\n📝 [Node: Writer] Drafting/Refining the structured report...")
    research_combined = f"SEARCH RESULTS:\n{state['search_results']}\n\nDETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    
    # Inject feedback if it exists from a previous loop
    feedback_context = f"\n\nPrevious Critic Feedback to address:\n{state.get('feedback', '')}" if state.get('feedback') else ""
    
    report = writer_chain.invoke({
        "topic": state['topic'], 
        "research": research_combined + feedback_context
    })
    
    # Track iterations to prevent budget overruns
    current_loops = state.get("loop_count", 0)
    return {"report": report, "loop_count": current_loops + 1}

def call_critic_chain(state: ResearchState):
    print("\n🧐 [Node: Critic] Assessing quality standards...")
    feedback = critic_chain.invoke({"report": state['report']})
    return {"feedback": feedback}

# 3. Conditional Routing Logic
def route_critic_decision(state: ResearchState) -> Literal["writer", "__end__"]:
    """Determines whether the report needs revision or is ready for production."""
    feedback = state.get("feedback", "").lower()
    loop_count = state.get("loop_count", 0)
    
    # Set a hard safety ceiling for API costs (e.g., max 3 revisions)
    if loop_count >= 3:
        print("\n⚠️ [System] Maximum revision cycles reached. Forcing finalization.")
        return END
        
    if "approved" in feedback or "accept" in feedback or "looks good" in feedback:
        print("\n✅ [System] Critic approved the report!")
        return END
        
    print(f"\n🔄 [System] Report rejected. Routing back to Writer (Revision cycle: {loop_count})")
    return "writer"

# 4. Native Tool Infrastructure Setup
# Wrapping tools into an official LangGraph ToolNode execution block
tools_node = ToolNode([web_search, scape_url])

# 5. Build Orchestration Graph
workflow = StateGraph(ResearchState)

# Register Nodes
workflow.add_node("search", call_search_agent)
workflow.add_node("reader", call_reader_agent)
workflow.add_node("writer", call_writer_chain)
workflow.add_node("critic", call_critic_chain)

# Register Graph Topology (Flow Control)
workflow.set_entry_point("search")
workflow.add_edge("search", "reader")
workflow.add_edge("reader", "writer")
workflow.add_edge("writer", "critic")

# Dynamic Routers
workflow.add_conditional_edges(
    "critic",
    route_critic_decision,
    {
        "writer": "writer",
        "__end__": END
    }
)

# Compile graph into a runnable production application
app = workflow.compile()

if __name__ == "__main__":
    user_topic = input("\nEnter a research topic: ")
    # Initialize the loop counter at 0 on start
    final_state = app.invoke({"topic": user_topic, "loop_count": 0})
    print("\n✨ Pipeline Complete! Final report compiled.")