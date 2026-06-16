import re
from langchain_core.tools import tool
from tavily import TavilyClient
from src.config import settings

# Enforce crisp initialization by leveraging our validated configuration module
tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent, reliable information on a given topic query.
    Returns structured results containing Titles, URLs, and contextual Snippets.
    
    Args:
        query (str): Topic or raw keyword query to perform research execution on.
    """
    try:
        # Protect against empty or heavily padded whitespace parameters from the agent
        clean_query = query.strip()
        if not clean_query:
            return "Error: The search engine query cannot be completely blank."

        # Fetch top 5 high-density context articles
        results = tavily.search(query=clean_query, max_results=5)
        
        if not results.get('results'):
            return f"Search Query Notice: No active index or resources found for: '{clean_query}'"
            
        out = []
        for r in results['results']:
            title = r.get('title', 'No Document Title Available')
            url = r.get('url', 'Missing Reference URL')
            content = r.get('content', 'Contextual body snippet is currently unavailable.')
            
            out.append(f"Title: {title}\nURL: {url}\nSnippet: {content}\n")
            
        return "\n---------------------------------------------------------\n".join(out)
        
    except Exception as e:
        return f"Tool Execution Failure (web_search): Encountered upstream index error: {str(e)}"