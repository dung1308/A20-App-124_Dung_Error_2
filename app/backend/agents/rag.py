"""
agents/rag.py
-------------
Responsibility: RAGAgent answers factual questions about VinUni programs,
requirements, and campus life using Retrieval-Augmented Generation.
"""

import logging
from typing import List

from config import USE_MOCK
from services.rag_service import RAGService
from utils.logger import get_logger

logger = get_logger(__name__)

class RAGAgent:
    """
    Retrieves relevant document chunks and generates grounded answers.
    """

    def __init__(self):
        self.rag_service = RAGService()

    def run(self, message: str, user_id: str = None) -> str:
        """
        Answer a factual question using retrieved context.
        """
        logger.info(f"RAGAgent.run() — question: '{message[:60]}'")
        # Delegate to RAGService to utilize the Layer 5 safety and observability pipeline
        return self.rag_service.retrieve_and_answer(message, user_id=user_id)