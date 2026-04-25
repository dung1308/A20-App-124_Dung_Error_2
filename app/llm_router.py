"""
LLM-based intelligent router.
Uses Gemini to classify user intent and route to appropriate agent.
"""

import logging
import json
from typing import List, Dict, Optional
from config import get_gemini_model

logger = logging.getLogger(__name__)


class LLMRouter:
    """
    Routes user messages to appropriate agent using LLM.
    More intelligent than rule-based routing.
    """
    
    def __init__(self):
        """Initialize the router."""
        self.model = get_gemini_model("gemini-1.5-flash")

    def route(
        self,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Classify user intent and route message.
        
        Routes to:
        - "rag": Information questions (học phí, ngành, deadline)
        - "crm": Personal profile questions (trạng thái hồ sơ)
        - "advisor": Guidance questions (định hướng, chọn ngành)
        - "fallback": Unclear intent or need human
        
        Args:
            message: User message
            history: Optional conversation history for context
            
        Returns:
            Route string: 'rag', 'crm', 'advisor', or 'fallback'
        """
        try:
            # Format history for context
            history_text = ""
            if history:
                for msg in history[-3:]:  # Last 3 messages for context
                    if isinstance(msg, dict):
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                        history_text += f"{role}: {content}\n"

            prompt = f"""
Bạn là hệ thống phân loại intent cho chatbot tuyển sinh.

Phân loại câu hỏi của user vào 1 trong các nhóm:
- "rag" → hỏi thông tin trường/ngành (học phí, ngành, deadline, điểm chuẩn...)
- "crm" → hỏi trạng thái hồ sơ cá nhân (hồ sơ, tài liệu, tiến độ...)
- "advisor" → hỏi định hướng (nên chọn ngành nào, trường có phù hợp không...)
- "fallback" → không rõ ý hoặc cần con người xử lý

Lịch sử hội thoại (nếu có):
{history_text}

Câu hỏi của user: {message}

Trả về CHỈ JSON (không có text khác):
{{"route": "rag|crm|advisor|fallback"}}
"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            parsed = json.loads(response_text)
            route = parsed.get("route", "fallback")
            
            # Validate route
            valid_routes = ["rag", "crm", "advisor", "fallback"]
            if route not in valid_routes:
                logger.warning(f"Invalid route returned: {route}, using fallback")
                return "fallback"
            
            return route
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse router response as JSON: {e}")
            return "fallback"
        except Exception as e:
            logger.error(f"Router error: {e}")
            return "fallback"
