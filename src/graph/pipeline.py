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
    """Determines whether the report needs revision or is ready to finish."""
    feedback = state.get("feedback", "").strip().split("\n")[-1]
    loop_count = state.get("loop_count", 0)
    
    # 3-pass safe token budget threshold
    if loop_count >= 3:
        print("\n⚠️ [System] Max revision cycles hit. Closing pipeline.")
        return END
        
    if "APPROVED" in feedback:
        print("\n✅ [System] Critic issued layout approval status.")
        return END
        
    print(f"\n🔄 [System] Structural optimization requested. Cycle: {loop_count}")
    return "writer"

# Building layout graph topology
workflow = StateGraph(ResearchState)

# Add modular execution nodes
workflow.add_node("search", call_search_agent)
workflow.add_node("reader", call_reader_agent)
workflow.add_node("writer", call_writer_chain)
workflow.add_node("critic", call_critic_chain)

# Layout mapping flow
workflow.set_entry_point("search")
workflow.add_edge("search", "reader")
workflow.add_edge("reader", "writer")
workflow.add_edge("writer", "critic")

# Register contextual feedback loop
workflow.add_conditional_edges(
    "critic",
    route_critic_decision,
    {
        "writer": "writer",
        "__end__": END
    }
)

app = workflow.compile()