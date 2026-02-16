"""
Configuration for Market Research GPT

Loads environment variables and defines application-wide settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ── LangSmith Tracing ────────────────────────────────────────────────────────
# LangChain/LangGraph send traces automatically when these are set.
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "market-research-gpt")

if LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT

# ── LLM Settings ─────────────────────────────────────────────────────────────
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# ── Tavily Search Settings ────────────────────────────────────────────────────
TAVILY_SEARCH_DEPTH = "advanced"  # "basic" or "advanced"
TAVILY_MAX_RESULTS = 5

# ── PDF Settings ──────────────────────────────────────────────────────────────
PDF_MAX_PAGES = 100
PDF_TABLE_EXTRACTION = True

# ── Agent Settings ────────────────────────────────────────────────────────────
PLANNER_MAX_SUBTASKS = 5
WRITER_MAX_TOKENS = 4096

# ── Output ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
