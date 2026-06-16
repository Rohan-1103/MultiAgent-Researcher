import re
from langchain_core.tools import tool
from tavily import TavilyClient
from src.config import settings

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent, reliable information on a given topic query.
    Returns structured results containing Titles, URLs, and contextual Snippets.
    """
    try:
        clean_query = query.strip()
        if not clean_query:
            return "Error: The search engine query cannot be completely blank."

        results = tavily.search(query=clean_query, max_results=5)
        
        if not results.get('results'):
            return f"Search Query Notice: No active index or resources found for: '{clean_query}'"
            
        out = []
        for r in results['results']:
            title = r.get('title', 'No Document Title Available').strip()
            url = r.get('url', 'Missing Reference URL').strip()
            content = r.get('content', 'Contextual body snippet is currently unavailable.').strip()
            
            # Formats the string exactly matching your expected output format
            out.append(f"Title: {title}\nURL: {url}\nSnippet: {content}")
            
        return "\n\n---------------------------------------------------------\n\n".join(out)
        
    except Exception as e:
        return f"Tool Execution Failure (web_search): {str(e)}"