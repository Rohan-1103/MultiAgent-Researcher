import re
import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from tavily import TavilyClient
from src.config import settings

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

def clean_url_argument(url: str) -> str:
    """Cleans up accidental markdown formatting, parameters, or tracking tags injected by the LLM."""
    # Strip basic string artifacts
    url = url.strip().strip("'\"()[]<>")
    
    # Catch structural failures where the model accidentally scrapes or drops a search redirect query directly
    if "google.com/url?" in url or "google.com/search?" in url:
        # Extract the real destination website path from the tracking query parameter parameter loop if found
        match = re.search(r'(?:q|url)=([^&]+)', url)
        if match:
            import urllib.parse
            url = urllib.parse.unquote(match.group(1))
            
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
        
    return url

@tool
def scrape_url(url: str) -> str:
    """
    Scrapes and extracts clean main-text content from a given URL for deeper analytical reading.
    Automatically filters out noisy page layout clutter like headers, footers, scripts, and ads.
    
    Args:
        url (str): The absolute web URL target to extract core body text from.
    """
    cleaned_url = clean_url_argument(url)
    
    # --- Strategy A: High-Speed Standard Python HTTP Request + BeautifulSoup Extraction ---
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Enforce an explicit timeout ceiling to prevent node execution hangs
        resp = requests.get(cleaned_url, timeout=10, headers=headers)
        resp.raise_for_status() 
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Unpack and decompose text layout structures that don't add analytical value
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg", "iframe"]):
            tag.decompose()
            
        # Extract plain string and compress raw multi-whitespace gaps
        text_content = soup.get_text(separator=" ", strip=True)
        text_content = re.sub(r'\s+', ' ', text_content)
        
        # If the page yields a robust block of textual context, return it directly
        if len(text_content) > 800:
            return text_content[:16000]  # Safe token ceiling balancing Groq payload vs data density
            
    except Exception:
        # Pass silently and drop straight through to Strategy B if a firewall or JS rendering blanks out the response
        pass

    # --- Strategy B: Fallback to Tavily Headless Document Extraction API ---
    try:
        # The extraction endpoint parses client-side dynamically rendered JS scripts flawlessly
        extraction = tavily.extract(urls=[cleaned_url])
        results = extraction.get('results', [])
        
        if results and results[0].get('raw_content'):
            raw_markdown = results[0]['raw_content']
            return raw_markdown[:16000]
            
    except Exception as err:
        return f"Extraction Pipeline Failure: Both parsing layers failed to harvest {cleaned_url}. Error: {str(err)}"

    return f"Extraction Pipeline Warning: Document structure at {cleaned_url} was thin or evaluated to empty space."