"""
AI Agents for recruitment system.
Each agent handles a specific domain: RAG, CRM, or Advisory.
"""

import logging
from typing import List, Optional
from config import get_gemini_model

logger = logging.getLogger(__name__)


def generate(prompt: str) -> str:
    """
    Generate text using Gemini LLM.
    
    Args:
        prompt: Input prompt for the LLM
        
    Returns:
        Generated text response
    """
    try:
        model = get_gemini_model("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating content: {e}")
        return f"Lỗi hệ thống: {str(e)}"


class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent.
    Answers questions based on documents/knowledge base.
    """
    
    def __init__(self, rag):
        """
        Initialize RAG Agent.
        
        Args:
            rag: RAGSystem instance with document index
        """
        self.rag = rag

    def run(self, message: str) -> str:
        """
        Answer question using RAG retrieval.
        
        Args:
            message: User question
            
        Returns:
            Answer based on documents
        """
        try:
            # Retrieve relevant documents
            docs = self.rag.query(message)
            context = "\n".join(docs)

            prompt = f"""
Bạn là trợ lý tuyển sinh. Hãy trả lời câu hỏi dựa trên thông tin được cung cấp.

Yêu cầu:
- Chỉ được trả lời dựa trên CONTEXT bên dưới
- Nếu không có thông tin phù hợp → nói "Tôi chưa có thông tin về điều này"
- Trả lời tự nhiên, ngắn gọn

Thông tin tham khảo:
{context}

Câu hỏi: {message}

Trả lời:
"""
            return generate(prompt)
        except Exception as e:
            logger.error(f"RAG Agent error: {e}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi của bạn."


class CRMAgent:
    """
    CRM Agent.
    Retrieves and manages student profile information.
    """
    
    def __init__(self, crm):
        """
        Initialize CRM Agent.
        
        Args:
            crm: CRM instance
        """
        self.crm = crm

    def run(self, user_id: str, message: str = None) -> str:
        """
        Get student CRM information.
        
        Args:
            user_id: Student identifier
            message: Optional context message
            
        Returns:
            Student profile information
        """
        try:
            profile = self.crm.get(user_id)
            
            if not profile:
                return f"Không tìm thấy hồ sơ cho {user_id}"
            
            # Format profile for display
            status = profile.get("status", "N/A")
            major = profile.get("major", "Chưa xác định")
            
            return f"""
Hồ sơ của bạn:
- Trạng thái: {status}
- Ngành dự tuyển: {major}

Vui lòng liên hệ với chúng tôi nếu cần cập nhật thông tin.
"""
        except Exception as e:
            logger.error(f"CRM Agent error: {e}")
            return "Xin lỗi, tôi không thể lấy thông tin hồ sơ của bạn."


class AdvisorAgent:
    """
    Advisor Agent.
    Provides personalized guidance on program selection and career paths.
    """
    
    def run(self, message: str, history: List[dict]) -> str:
        """
        Provide advisory guidance.
        
        Args:
            message: User question/message
            history: Conversation history
            
        Returns:
            Advisory response
        """
        try:
            # Format history for context
            history_text = ""
            for msg in (history or [])[-5:]:  # Last 5 messages
                role = msg.get("role", "user").upper()
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

            prompt = f"""
Bạn là tư vấn tuyển sinh thông minh với nhiều năm kinh nghiệm.

Mục tiêu:
1. Hiểu nhu cầu và khả năng của học sinh
2. Định hướng trường/ngành phù hợp
3. Dẫn dắt hội thoại một cách tự nhiên

Lịch sử hội thoại:
{history_text}

Yêu cầu:
1. Trả lời tự nhiên như một người thực
2. Nếu user chưa rõ → hỏi câu hỏi cụ thể để hiểu rõ
3. Đưa ra gợi ý cụ thể về ngành học và bước tiếp theo
4. Không trả lời như FAQ

User: {message}

Trả lời (ngắn gọn, 2-3 câu):
"""
            return generate(prompt)
        except Exception as e:
            logger.error(f"Advisor Agent error: {e}")
            return "Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn."


class Router:
    """
    Simple rule-based router (fallback if LLM router unavailable).
    Routes messages to appropriate agent based on keywords.
    """
    
    @staticmethod
    def route(message: str) -> str:
        """
        Route message to appropriate agent.
        
        Args:
            message: User message
            
        Returns:
            Route: 'rag', 'crm', 'advisor', or 'fallback'
        """
        m = message.lower()

        # CRM queries
        if any(keyword in m for keyword in ["hồ sơ", "trạng thái", "tài liệu", "nộp"]):
            return "crm"

        # Advisory queries
        elif any(keyword in m for keyword in ["ngành", "phù hợp", "nên chọn", "nào tốt", "định hướng"]):
            return "advisor"

        # Default to RAG
        else:
            return "rag"
