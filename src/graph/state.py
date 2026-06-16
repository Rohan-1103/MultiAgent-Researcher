from typing import TypedDict

class ResearchState(TypedDict):
    """
    Represents the unified state machine memory for the InsightEngine framework.
    Passed between individual graph nodes to mutate and track the research progress.
    """
    topic: str             # The core user query or research topic
    search_results: str    # Raw aggregated titles, URLs, and snippets from Tavily
    scraped_content: str   # Deep content text extracted from selected web resources
    report: str            # The markdown compiled research draft written by the Writer
    feedback: str          # Quantitative score and detailed critique logs from the Critic
    loop_count: int        # Counter tracking iterations to protect API wallet limits