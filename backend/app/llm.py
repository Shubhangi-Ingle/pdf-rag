import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


@lru_cache(maxsize=1)
def get_llm():
    """Create the Gemini chat model once and reuse it."""
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        max_retries=3,
        timeout=30,
    )