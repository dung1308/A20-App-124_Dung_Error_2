"""
agents/crm.py
-------------
Responsibility: CRMAgent retrieves the student's stored profile from the
database and uses it to give personalised, context-aware responses.

Typical triggers (router → "crm"):
  - "Hồ sơ của tôi đang ở đâu?"
  - "Điểm IELTS của tôi có đủ không?"
  - "Mình đã điền thông tin gì rồi?"
"""

import logging
from typing import Optional, Dict, Any

from config import get_gemini_model
from services.db_service import DBService
from utils.logger import get_logger

logger = get_logger(__name__)

CRM_SYSTEM_PROMPT = """
Bạn là trợ lý tư vấn tuyển sinh VinUni với quyền truy cập hồ sơ học sinh.
Trả lời câu hỏi của học sinh dựa trên thông tin hồ sơ được cung cấp.
Không tiết lộ thông tin cá nhân của học sinh cho bên thứ ba.
Trả lời bằng tiếng Việt, thân thiện và cụ thể.
"""


class CRMAgent:
    """
    Fetches student profile from PostgreSQL and answers profile-related questions.
    """

    def __init__(self):
        self.model = get_gemini_model()
        # TODO: Inject DBService dependency for easier testing
        self.db = DBService()

    def run(self, user_id: str, message: str) -> str:
        """
        Retrieve student profile and answer a profile-related question.

        Args:
            user_id: Student identifier — used to fetch profile from DB.
            message: User question about their own profile or fit.

        Returns:
            Personalised answer string in Vietnamese.

        TODO: 1. Call self.db.get_student_profile(user_id) → profile dict or None.
        TODO: 2. If profile is None → return "Mình chưa tìm thấy hồ sơ của bạn..."
        TODO: 3. Build prompt: CRM_SYSTEM_PROMPT + formatted profile + question.
        TODO: 4. Call self.model.generate_content(prompt).
        TODO: 5. Return response.text stripped of whitespace.
        TODO: 6. Wrap in try/except → return polite error string on failure.
        """
        logger.info(f"CRMAgent.run() — user: {user_id}")

        # TODO: Remove stub and implement DB fetch + Gemini response
        return "CRMAgent chưa được implement."

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch raw student profile dict from the database.

        Args:
            user_id: Student identifier.

        Returns:
            Profile dict or None if not found.

        TODO: Call db.get_student_profile(user_id).
        TODO: Return None (not raise) if user not found — let caller handle.
        """
        # TODO: Replace stub with real DB call
        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_crm_prompt(self, profile: Dict[str, Any], question: str) -> str:
        """
        Format a student profile dict into a readable prompt block.

        Args:
            profile:  Dict with student fields (gpa, ielts, interests, etc.).
            question: User's question.

        Returns:
            Full prompt string for Gemini.

        TODO: Format each profile key-value pair on its own line.
        TODO: Mask sensitive fields (phone, email) before including in prompt.
        TODO: Append the user question at the end.
        """
        # TODO: Implement formatted profile serialisation
        formatted = "\n".join(f"{k}: {v}" for k, v in profile.items())
        return f"{CRM_SYSTEM_PROMPT}\n\nHồ sơ học sinh:\n{formatted}\n\nCâu hỏi: {question}"
