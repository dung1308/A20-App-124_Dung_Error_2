# guardrails/judge.py
"""
Output evaluation and safety judging.
CRITICAL: Implements fail-safe defaults to REJECT rather than ALLOW.
"""

import logging
import json
from typing import Dict, Any
from config import get_gemini_model

logger = logging.getLogger(__name__)


def evaluate(input_text: str, output_text: str) -> Dict[str, Any]:
    """
    Evaluate response safety, relevance, accuracy, and tone.
    
    ⚠️ FAIL-SAFE: On any error, defaults to REJECTING the response.
    This prevents dangerous content from slipping through.
    
    Args:
        input_text: User's input question
        output_text: System's generated response
        
    Returns:
        Dict with keys:
        - pass: bool (True = safe to show, False = block)
        - reason: str (explanation)
        - score: int (1-10 quality score)
        - error: str (if error occurred)
    """
    
    prompt = f"""
Đánh giá câu trả lời theo các tiêu chí:
- Safety (an toàn - không chứa nội dung nguy hiểm, phân biệt, bạo lực, sexual content)
- Relevance (liên quan - trả lời trực tiếp câu hỏi)
- Accuracy (chính xác - không có thông tin sai lệch)
- Tone (giọng điệu - tự nhiên, lịch sự, phù hợp với chatbot tuyển sinh)

Input: {input_text}
Output: {output_text}

Trả về JSON:
{{
 "pass": true/false,
 "reason": "explanation...",
 "score": 1-10,
 "safety": "safe/warning/danger",
 "relevance": "high/medium/low"
}}
"""
    
    try:
        model = get_gemini_model()
        response = model.generate_content(prompt)
        
        # Parse LLM response
        response_text = response.text.strip()
        
        # Try to extract JSON if wrapped in markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        result = json.loads(response_text)
        
        # Validate required fields
        if not isinstance(result.get("pass"), bool):
            logger.warning("Judge result missing 'pass' field")
            return _fail_safe("Invalid judge response format")
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Judge: Failed to parse JSON: {e}")
        return _fail_safe("JSON parsing error")
    
    except Exception as e:
        logger.error(f"Judge evaluation error: {type(e).__name__}: {e}")
        return _fail_safe(f"Judge system error: {type(e).__name__}")


def _fail_safe(reason: str) -> Dict[str, Any]:
    """
    Fail-safe response: REJECT the output when judge is unavailable.
    
    This is intentional security design:
    - Rather than allowing unknown content (unsafe)
    - We reject it and ask user to contact human advisor
    
    Args:
        reason: Why the judge failed
        
    Returns:
        Safe dict that indicates rejection
    """
    return {
        "pass": False,
        "reason": reason,
        "score": 0,
        "safety": "unknown",
        "error": reason
    }
