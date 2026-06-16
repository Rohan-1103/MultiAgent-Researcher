from typing import Literal
from langgraph.graph import StateGraph, END
from src.graph.state import ResearchState
from src.graph.nodes import (
    call_search_agent, 
    call_reader_agent, 
    call_writer_chain, 
    call_critic_chain
)

def route_critic_decision(state: ResearchState) -> Literal["writer", "__end__"]:
    feedback = state.get("feedback", "").strip().split("\n")[-1]
    loop_count = state.get("loop_count", 0)
    max_allowed_loops = state.get("max_loops", 3)
    
    if loop_count >= max_allowed_loops:
        print(f"\n⚠️ [System] Dynamic revision limit ({max_allowed_loops}) reached. Forcing completion.")
        return END
        
    if "APPROVED" in feedback:
        print("\n✅ [System] Critic issued structural draft approval.")
        return END
        
    print(f"\n🔄 [System] Structural revision cycle running: {loop_count}")
    return "writer"

# 2. Construct the Workflow Graph
workflow = StateGraph(ResearchState)

# Register Core Agent Nodes
workflow.add_node("search", call_search_agent)
workflow.add_node("reader", call_reader_agent)
workflow.add_node("writer", call_writer_chain)
workflow.add_node("critic", call_critic_chain)

# Linear Topologies matching our self-contained node logic
workflow.set_entry_point("search")
workflow.add_edge("search", "reader")
workflow.add_edge("reader", "writer")
workflow.add_edge("writer", "critic")

# Register dynamic conditional feedback loop
workflow.add_conditional_edges(
    "critic",
    route_critic_decision,
    {
        "writer": "writer",
        "__end__": END
    }
)

app = workflow.compile()