import os
import re
from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Enforce strict validation on initialization
api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    raise ValueError("CRITICAL: TAVILY_API_KEY is missing from environment variables.")

tavily = TavilyClient(api_key=api_key)

def clean_url_argument(url: str) -> str:
    """Cleans up accidental markdown formatting or whitespace injected by the LLM."""
    url = url.strip().strip("'\"()[]<>")
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

@tool
def web_search(query: str) -> str:
    """
    Search the web for recent, reliable information on a given topic.
    Returns structured results containing Titles, URLs, and contextual snippets.
    
    Args:
        query (str): The search query or research topic.
    """
    try:
        # Protect against empty or malformed inputs
        if not query or len(query.strip()) == 0:
            return "Error: Search query cannot be empty."

        results = tavily.search(query=query, max_results=5)
        
        if not results.get('results'):
            return f"No relevant search results found for query: '{query}'"
            
        out = []
        for r in results['results']:
            title = r.get('title', 'No Title')
            url = r.get('url', 'No URL')
            content = r.get('content', 'No content available.')
            out.append(f"Title: {title}\nURL: {url}\nSnippet: {content}\n")
            
        return "\n---------------------------------------------------------\n".join(out)
        
    except Exception as e:
        return f"An error occurred while executing the web search: {str(e)}"


@tool
def scrape_url(url: str) -> str:
    """
    Scrapes and extracts clean main-text content from a given URL for deeper analytical reading.
    Automatically filters out headers, footers, advertisements, and code blocks.
    
    Args:
        url (str): The absolute web URL to extract text from.
    """
    cleaned_url = clean_url_argument(url)
    
    # Strategy 1: Standard Python Request + BeautifulSoup (Ultra-fast for clean static sites)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(cleaned_url, timeout=10, headers=headers)
        
        # If the server drops us with a client/server error, jump straight to Strategy 2
        resp.raise_for_status() 
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Ruthlessly prune non-content elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg"]):
            tag.decompose()
            
        # Extract content text and collapse whitespace
        text_content = soup.get_text(separator=" ", strip=True)
        # Normalize erratic spacing
        text_content = re.sub(r'\s+', ' ', text_content)
        
        # Senior Threshold: If we successfully extracted substantial text, return it
        if len(text_content) > 800:
            # 16,000 characters gives your Writer ~3,500-4,000 tokens of deep context
            return text_content[:16000]
            
    except Exception as e:
        # Gracefully log/fall through to Strategy 2 without blowing up the agent's workflow
        pass

    # Strategy 2: Fallback to Tavily Extract API (Handles JS execution, cookies, and Captchas)
    try:
        # Tavily's extract endpoint pulls pure main-article markdown text effortlessly
        extraction = tavily.extract(urls=[cleaned_url])
        results = extraction.get('results', [])
        
        if results and results[0].get('raw_content'):
            raw_markdown = results[0]['raw_content']
            return raw_markdown[:16000]
            
    except Exception as err:
        return f"Extraction Pipeline Failure: Unable to scrape content from {cleaned_url}. Reason: {str(err)}"

    return f"Extraction Warning: Extracted page content from {cleaned_url} was too thin or empty."