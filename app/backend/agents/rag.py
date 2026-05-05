"""
agents/rag.py
-------------
Responsibility: RAGAgent answers factual questions about VinUni programs,
requirements, and campus life using Retrieval-Augmented Generation.
"""

import logging
from typing import List

from config import get_gemini_model, USE_MOCK
from services.rag_service import RAGService
from utils.logger import get_logger

logger = get_logger(__name__)

RAG_SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn tuyển sinh VinUni. Trả lời câu hỏi của học sinh dựa trên thông tin đã được cung cấp.

Quy tắc:
- Chỉ sử dụng thông tin trong phần Context bên dưới.
- Nếu thông tin không có trong Context, hãy nói: "Mình chưa có thông tin chính xác về điều này. Hãy kiểm tra trực tiếp tại vinuni.edu.vn hoặc liên hệ tư vấn viên."
- Trả lời bằng tiếng Việt, ngắn gọn và rõ ràng.
- Không bịa thêm thông tin.
"""


class RAGAgent:
    """
    Retrieves relevant document chunks and generates grounded answers.
    """

    def __init__(self):
        # ✅ Only initialize model in REAL mode
        self.model = None if USE_MOCK else get_gemini_model()
        self.rag_service = RAGService()

    def run(self, message: str, user_id: str = None) -> str:
        """
        Answer a factual question using retrieved context.
        """
        logger.info(f"RAGAgent.run() — question: '{message[:60]}'")

        try:
            # 1. Retrieve relevant chunks
            chunks = self.rag_service.retrieve(message, user_id=user_id)

            if not chunks:
                return "Mình chưa có thông tin chính xác về điều này."

            # ==========================================================
            # ✅ MOCK MODE — NO LLM CALLS AT ALL
            # ==========================================================
            if USE_MOCK:
                logger.info("RAGAgent operating in MOCK mode")
                return chunks[0]

            # ==========================================================
            # REAL MODE — USE GEMINI
            # ==========================================================
            if not self.model:
                logger.warning("Gemini model not available")
                return "Mình chưa có thông tin chính xác về điều này."

            prompt = self._build_rag_prompt(message, chunks)
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                return "Mình chưa có thông tin chính xác về điều này."

            return response.text.strip()

        except Exception as e:
            logger.error(f"RAGAgent failure: {e}")
            return "Mình chưa có thông tin chính xác về điều này."

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_rag_prompt(self, question: str, chunks: List[str]) -> str:
        """
        Combine system prompt, retrieved context chunks, and user question.
        """
        context_block = "\n---\n".join(chunks)

        prompt = (
            f"{RAG_SYSTEM_PROMPT}\n\n"
            f"Context:\n{context_block}\n\n"
            f"Câu hỏi: {question}"
        )

        # Safety truncation for context window
        return prompt[:30000]