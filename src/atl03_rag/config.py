import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROK_API_KEY   = os.getenv("GROK_API_KEY", "")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost:5432/atl03_rag"
)

# Embedding
EMBED_MODEL   = "models/text-embedding-004"
EMBEDDING_DIM = 768

# PDF
PDF_STRATEGY = "fast"

# Chunking
CHUNK_MIN_CHARS          = 100
CHUNK_SEMANTIC_TRIGGER   = 1500

# Retrieval
TOP_K_VECTOR = 10
TOP_K_BM25   = 10
TOP_K_FINAL  = 5
VECTOR_WEIGHT = 0.7
BM25_WEIGHT   = 0.3

# LLM
LLM_MODEL       = "grok-3-mini"
LLM_MAX_TOKENS  = 1024
LLM_TEMPERATURE = 0.1

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR     = PROJECT_ROOT / "data"
RAW_DIR      = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Source documents
ATL03_USER_GUIDE       = RAW_DIR / "atl03_userguide_v007.pdf"
ATL03_DATA_DICTIONARY  = RAW_DIR / "atl03_data_dictionary_v07.pdf"

# Create processed dir if it doesn't exist
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)