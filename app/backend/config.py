"""
config.py
---------
Responsibility: Centralized LLM and environment configuration.
HINGE RULE: This is the ONLY file that imports google.generativeai or
initialises any LLM client. All agents call get_gemini_model() from here.
Swapping LLM providers = edit this one file only.
"""

import os
import logging
from functools import lru_cache
from dotenv import load_dotenv


# TODO: Uncomment once google-generativeai is installed
import google.generativeai as genai

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "sqlite:///./vinuni_match.db"  # SQLite fallback for dev
)
USE_MOCK: bool = os.getenv("USE_MOCK", "True").lower() == "true"
REDIS_URL: str | None = os.getenv("REDIS_URL")
HUMAN_WEBHOOK: str = os.getenv("HUMAN_WEBHOOK", "http://localhost:9000/handoff")
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "10"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
DAILY_LLM_BUDGET: float = float(os.getenv("DAILY_LLM_BUDGET", "100"))

# TODO: Raise ValueError if GEMINI_API_KEY is empty in non-development environments
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY not set — LLM calls will fail at runtime.")

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


# ---------------------------------------------------------------------------
# LLM client factory (hinge rule)
# ---------------------------------------------------------------------------

class MockGenerativeModel:
    """
    A mock object that mimics the interface of google.generativeai.GenerativeModel.
    Used when USE_MOCK=True to avoid external API calls.
    """
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate_content(self, prompt: str, **kwargs):
        """
        Returns a simulated response based on detected prompt keywords to ensure 
        JSON parsers in agents don't break.
        """
        text = "Đây là phản hồi giả lập từ hệ thống VinUni Major Matcher."
        
        # Detect agent-specific intents for structured JSON responses
        if "top3" in prompt: # AdvisorAgent
            text = '{"top3": [{"major_id": "cs", "match_reason": "Dựa trên sở thích công nghệ và logic của bạn.", "match_score": 95}], "fallback": false}'
        elif "suggested_majors" in prompt: # CVAgent
            text = '{"suggested_majors": ["cs", "ba"], "confidence": 0.9, "evidence": ["Hồ sơ có thế mạnh về lập trình."]}'
        elif "pass" in prompt: # JudgeAgent
            text = '{"pass": true, "reason": "Nội dung an toàn và phù hợp.", "score": 100}'
        elif "summary" in prompt and "education" in prompt: # CVParser
            text = '{"summary": "Sinh viên tiềm năng.", "education": [], "experience": [], "skills": ["Python", "AI"], "projects": [], "achievements": []}'
        elif "intent" in prompt: # LLMRouter.classify_intent
            text = '{"intent": "INFO_QUERY", "confidence": 1.0}'
        elif "rag, crm, advisor, fallback" in prompt: # LLMRouter.route
            text = "rag"

        class MockResponse:
            def __init__(self, t):
                self.text = t
        
        return MockResponse(text)

    def embed_content(self, content: str, **kwargs):
        """Mock embedding response."""
        class MockEmbedding:
            def __init__(self): self.embedding = [0.1] * 768
        return MockEmbedding()

@lru_cache(maxsize=1)
def get_gemini_model(model_name: str = "gemini-1.5-flash"):
    """
    Return a cached Gemini GenerativeModel instance.
    lru_cache ensures the model is initialised once per process.

    HINGE RULE: Every agent that needs LLM access imports and calls THIS function.
    No other file should import google.generativeai directly.

    TODO: Un-comment genai lines once google-generativeai is installed.
    TODO: Add retry logic / exponential backoff wrapper around the returned model.
    TODO: Add token-usage tracking to enforce DAILY_LLM_BUDGET.

    Args:
        model_name: Gemini model identifier string.

    Returns:
        A configured GenerativeModel ready to call .generate_content().
    """
    if USE_MOCK:
        logger.info(f"USE_MOCK is True. Returning MockGenerativeModel for {model_name}")
        return None  # Return None to let agents know to use mock responses directly

    # TODO: Replace stub with real initialisation
    # genai.configure(api_key=GEMINI_API_KEY)
    # return genai.GenerativeModel(model_name)
    return None


def get_database_url() -> str:
    """
    Return the database URL from environment.
    Falls back to SQLite for local development if DATABASE_URL is unset.

    TODO: Validate URL format before returning.
    """
    return DATABASE_URL

def embed_text(text: str):
    if USE_MOCK:
        return None

    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    result = genai.embed_content(
        model="gemini-embedding-2",
        content=text
    )
    return result["embedding"]
