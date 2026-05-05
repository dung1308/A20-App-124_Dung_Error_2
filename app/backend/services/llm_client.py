import time
from config import get_gemini_model
from utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient:
    def __init__(self):
        self.model = get_gemini_model()

    def generate(self, prompt: str, max_retries=3, timeout=5):
        for attempt in range(max_retries):
            try:
                start = time.time()

                response = self.model.generate_content(prompt)

                latency = time.time() - start
                logger.info(f"LLM latency: {latency:.2f}s")

                if response and response.text:
                    return response.text.strip()

                return "I don't know"

            except Exception as e:
                logger.warning(f"LLM retry {attempt+1}: {e}")
                time.sleep(1)

        logger.error("LLM failed after retries")
        return "I don't know"