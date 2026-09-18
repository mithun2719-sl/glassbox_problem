import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "glassbox")
PINECONE_HOST = os.getenv("PINECONE_HOST", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", "6000"))
TRACES_DIR = ROOT / "traces"
DOCUMENTS_DIR = ROOT / "data" / "documents"
