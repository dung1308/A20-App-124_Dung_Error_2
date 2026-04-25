"""
Centralized configuration management
"""

import os
import logging
from functools import lru_cache
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

logger = logging.getLogger(__name__)

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# API Keys and Secrets (loaded once)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("⚠️ GEMINI_API_KEY not set in .env")

HUMAN_WEBHOOK = os.getenv("HUMAN_WEBHOOK", "http://localhost:9000/handoff")

# Database
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to SQLite for development
    DATABASE_URL = "sqlite:///./recruitment.db"
    logger.warning(f"DATABASE_URL not set, using SQLite: {DATABASE_URL}")


def get_database_url() -> str:
    """Get database URL safely"""
    return DATABASE_URL


# Redis (optional for caching)
REDIS_URL = os.getenv("REDIS_URL", None)

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

# LLM Cost Control
DAILY_LLM_BUDGET = float(os.getenv("DAILY_LLM_BUDGET", "100"))


@lru_cache(maxsize=1)
def get_gemini_client():
    """
    Get Gemini client singleton.
    Uses caching to avoid re-initializing multiple times.
    """
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        raise


def get_gemini_model(model_name: str = "gemini-1.5-flash"):
    """Get Gemini model instance"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.error(f"Failed to get Gemini model {model_name}: {e}")
        raise


# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
