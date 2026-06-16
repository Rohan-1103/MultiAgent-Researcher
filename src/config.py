import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Centralized environment configuration and validation."""
    
    def __init__(self):
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
        
        # Immediate strict initialization validation
        if not self.GROQ_API_KEY:
            raise ValueError("CRITICAL: 'GROQ_API_KEY' is missing from your environment setup.")
        if not self.TAVILY_API_KEY:
            raise ValueError("CRITICAL: 'TAVILY_API_KEY' is missing from your environment setup.")

settings = Settings()