from typing import TypedDict

class ResearchState(TypedDict):
    """
    Represents the unified state machine memory for the InsightEngine framework.
    Passed between individual graph nodes to mutate and track the research progress.
    """
    topic: str             
    search_results: str    
    scraped_content: str   
    report: str            
    feedback: str          
    loop_count: int        
    max_loops: int         # Add this line so the UI parameter is retained