"""
Orchestrator coordinates agent execution.
Routes user messages to appropriate agents and combines their responses.
"""

import logging
from typing import List, Dict, Any
from llm_router import LLMRouter

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator for agent coordination.
    Routes messages to RAG, CRM, or Advisor agents.
    """
    
    def __init__(self, rag_agent, crm_agent, advisor_agent, sentiment):
        """
        Initialize orchestrator with all agents.
        
        Args:
            rag_agent: RAGAgent instance
            crm_agent: CRMAgent instance
            advisor_agent: AdvisorAgent instance
            sentiment: SentimentModel instance
        """
        self.rag_agent = rag_agent
        self.crm_agent = crm_agent
        self.advisor_agent = advisor_agent
        self.sentiment = sentiment
        self.router = LLMRouter()

    def run(
        self,
        user_id: str,
        message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """
        Process user message and return response.
        
        Routing logic:
        - If "crm" → Get user profile
        - If "advisor" → Get personalized guidance
        - If "fallback" → Suggest human advisor
        - Otherwise → Use RAG retrieval
        
        Args:
            user_id: User identifier
            message: User message
            history: Conversation history
            
        Returns:
            Response from appropriate agent
        """
        try:
            # Route message to appropriate agent
            route = self.router.route(message, history)
            logger.info(f"Routing user {user_id} to: {route}")

            if route == "crm":
                # Get CRM profile information
                return self.crm_agent.run(user_id, message)

            elif route == "advisor":
                # Provide personalized guidance
                return self.advisor_agent.run(message, history)

            elif route == "fallback":
                # Suggest human advisor
                return "Bạn muốn được kết nối với tư vấn viên của chúng tôi không?"

            else:  # Default to RAG
                return self.rag_agent.run(message)
        
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return "Xin lỗi, hệ thống gặp lỗi. Vui lòng thử lại."
