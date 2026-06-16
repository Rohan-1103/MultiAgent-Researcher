import re
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from tavily import TavilyClient
from src.config import settings

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

def clean_url_argument(url: str) -> str:
    """Cleans up accidental markdown formatting, parameters, or tracking tags."""
    url = url.strip().strip("'\"()[]<>")
    if "google.com/url?" in url or "google.com/search?" in url:
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
    Filters out noisy page layout clutter like headers, footers, scripts, and ads.
    """
    cleaned_url = clean_url_argument(url)
    
    # Strategy A: BeautifulSoup main text harvester
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(cleaned_url, timeout=10, headers=headers)
        resp.raise_for_status() 
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Strip structural noise blocks completely
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "svg", "iframe"]):
            tag.decompose()
            
        # Extract main text body paragraphs and unify erratic whitespacing
        text_content = soup.get_text(separator=" ", strip=True)
        text_content = re.sub(r'\s+', ' ', text_content)
        
        if len(text_content) > 800:
            return text_content[:16000] # Safe context-length text payload
            
    except Exception:
        pass

    # Strategy B: Hardened Headless Markdown Fallback Extraction
    try:
        extraction = tavily.extract(urls=[cleaned_url])
        results = extraction.get('results', [])
        if results and results[0].get('raw_content'):
            return results[0]['raw_content'][:16000]
    except Exception as err:
        return f"Extraction Failure: Unable to parse document strings. Error: {str(err)}"

    return "Extraction Warning: Webpage content evaluated to empty string blocks."