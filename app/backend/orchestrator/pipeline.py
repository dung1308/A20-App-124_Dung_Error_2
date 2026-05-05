"""
orchestrator/pipeline.py
------------------------
Responsibility: Main request flow controller.
Coordinates the full pipeline for both /api/match and /api/chat:

  Request
    → [InputGuard]      block injection / length violations
    → [RateLimiter]     enforce per-user quota
    → [LLMRouter]       classify intent  (chat only)
    → [Agent]           RAG / CRM / Advisor based on route
    → [OutputGuard]     redact PII, sanitize HTML
    → [Judge]           safety evaluation (fail-safe: reject on error)
    → [AuditLog]        record everything to DB
    → Response
"""

import logging
import time
from typing import List, Dict, Any, Optional

from orchestrator.router import LLMRouter
from agents.advisor import AdvisorAgent
from agents.rag import RAGAgent
from agents.crm import CRMAgent
from agents.cv_agent import CVAgent
from services.cv_parser import CVParser
from agents.judge import JudgeAgent
from guards.input_guard import InputGuard
from guards.output_guard import OutputGuard
from guards.rate_limiter import RateLimiter
from utils.logger import get_logger
from services.db_service import DBService
from models.cv_schema import CVSignals
from config import USE_MOCK

logger = get_logger(__name__)

DISCLAIMER = (
    "Kết quả do AI phân tích dựa trên câu trả lời của bạn "
    "— không thay thế buổi tư vấn trực tiếp."
)


class Pipeline:
    """
    Wires all components together and executes the two main flows:
      - run_match(): wizard submit → Top 3 majors
      - run_chat():  free-form message → routed agent response
    """

    def __init__(self):
        # TODO: Accept injected dependencies for easier unit testing
        self.router = LLMRouter()
        self.advisor = AdvisorAgent()
        self.rag = RAGAgent()
        self.crm = CRMAgent()
        self.judge = JudgeAgent()
        self.input_guard = InputGuard()
        self.output_guard = OutputGuard()
        self.rate_limiter = RateLimiter()
        self.cv_parser = CVParser()
        self.cv_agent = CVAgent()
        self.db_service = DBService()

    # ------------------------------------------------------------------
    # Wizard flow
    # ------------------------------------------------------------------

    def run_match(self, user_id: str, answers: Dict[str, Any], cv_text: str = None, cv_signals: CVSignals = None) -> Dict[str, Any]:
        """
        Full pipeline for POST /api/match (wizard submit).
        Calls AdvisorAgent to produce Top 3 major recommendations.

        Args:
            user_id: Student identifier string.
            answers:  Dict with keys interests, strengths, dislikes, work_style.

        Returns:
            Dict with keys: top3 (list), fallback (bool), disclaimer (str).

        TODO: 1. input_guard.check(str(answers)) — raise HTTPException 400 if blocked.
        TODO: 2. rate_limiter.allow(user_id)     — raise HTTPException 429 if exceeded.
        TODO: 3. raw_result = advisor.match_majors(answers).
        TODO: 4. safe_result = output_guard.redact(raw_result["disclaimer"] + str(raw_result)).
        TODO: 5. judge_result = judge.evaluate(str(answers), str(raw_result)).
        TODO: 6. If judge_result["pass"] is False → return fallback response.
        TODO: 7. audit_log(user_id, answers, raw_result, judge_result).
        TODO: 8. Return raw_result enriched with disclaimer.
        """
        logger.info(f"run_match for user: {user_id}")

        try:
            if USE_MOCK:
                # Simulate realistic processing time for demo mode
                time.sleep(1.0)
                judge_result = {"pass": True, "score": 1.0}
                # Deterministic mock advisor result
                raw_result = {
                    "top3": [
                        {
                            "major_id": "cs",
                            "major_name": "Khoa học Máy tính",
                            "match_reason": "Dựa trên sở thích công nghệ của bạn (Mock).",
                            "match_score": 95,
                            "what_students_do": "Sinh viên CS làm việc với AI và phần mềm."
                        }
                    ],
                    "fallback": False
                }
            else:
                # 1. Process CV if provided (sanitization happens inside parser)
                if not cv_signals:
                    if cv_text:
                        cv_data = self.cv_parser.parse(cv_text)
                        if cv_data:
                            cv_signals = self.cv_agent.generate_signals(cv_data)

                # 2. Match majors using AdvisorAgent
                raw_result = self.advisor.match_majors(answers, cv_signals)
                # 3. Safety check with JudgeAgent (Only in real mode)
                judge_result = self.judge.evaluate(str(answers), str(raw_result))

            if not judge_result.get("pass", False):
                logger.warning(f"Judge rejected match result for {user_id}")
                return {"top3": [], "fallback": True, "disclaimer": DISCLAIMER}

            # 4. Audit logging
            try:
                self._audit_log(user_id, answers, raw_result, judge_result)
            except Exception as audit_err:
                logger.error(f"Audit log failed (non-blocking): {audit_err}")

            return {**raw_result, "disclaimer": DISCLAIMER}

        except Exception as e:
            logger.error(f"Pipeline match failure for {user_id}: {e}")
            return {"top3": [], "fallback": True, "disclaimer": DISCLAIMER}

    def parse_cv(self, text: str) -> Optional[CVSignals]:
        """
        Extract structured signals from CV text.
        """
        try:
            cv_data = self.cv_parser.parse(text)
            if not cv_data:
                return None
            
            signals = self.cv_agent.generate_signals(cv_data)
            return signals
        except Exception as e:
            logger.error(f"Pipeline parse_cv failure: {e}")
            return None

    # ------------------------------------------------------------------
    # Chat flow
    # ------------------------------------------------------------------

    def run_chat(
        self,
        user_id: str,
        message: str,
        history: List[Dict[str, str]],
    ) -> Dict[str, Any]:
        """
        Full pipeline for POST /api/chat (free-form follow-up).
        Routes message to correct agent based on LLMRouter classification.

        Args:
            user_id: Student identifier string.
            message:  Latest user message.
            history:  Prior conversation turns.

        Returns:
            Dict with keys: response (str), agent (str).

        TODO: 1. input_guard.check(message)      — raise HTTPException 400 if blocked.
        TODO: 2. rate_limiter.allow(user_id)      — raise HTTPException 429 if exceeded.
        TODO: 3. route = router.route(message, history).
        TODO: 4. raw_response = _dispatch(route, user_id, message, history).
        TODO: 5. safe_response = output_guard.redact(raw_response).
        TODO: 6. judge_result = judge.evaluate(message, safe_response).
        TODO: 7. If judge_result["pass"] is False → return fallback string.
        TODO: 8. audit_log(user_id, message, safe_response, judge_result).
        TODO: 9. Return {"response": safe_response, "agent": route}.
        """
        logger.info(f"run_chat for user: {user_id}, route pending")
        
        # Initialize default judge result to prevent unbound errors
        judge_result = {"pass": True, "score": 1.0}

        try:
            if USE_MOCK:
                logger.info("Pipeline operating in MOCK mode")
                # Simulate realistic processing time for demo mode
                time.sleep(0.7)
                # 1. Mock routing (no LLM)
                route = self._mock_route(message)
            else:
                logger.info("Pipeline operating in REAL mode")
                # 1. Real LLM routing using safe history
                route = self.router.route(message, history)
            
            # 2. Dispatch (Real or Mock) with safe history
            raw_response = self._dispatch(route, user_id, message, history)
            safe_response = self.output_guard.redact(raw_response)
            
            # 3. Safety check (Only in real mode)
            if not USE_MOCK:
                judge_result = self.judge.evaluate(message, safe_response)
            
            if not judge_result.get("pass", False):
                logger.warning(f"Judge REJECTED response for user {user_id}. Reason: {judge_result.get('reason', 'Safety violation or API error')}")
                safe_response = "Tôi xin lỗi, nhưng tôi không thể trả lời câu hỏi này vì lý do an toàn. Bạn có câu hỏi nào khác về VinUni không?"
                route = "fallback"
            
            # TODO: 8. audit_log(user_id, message, safe_response, judge_result).
            self._audit_log(user_id, message, safe_response, judge_result)

            # TODO: 9. Return {"response": safe_response, "agent": route}.
            status = "success" if judge_result.get("pass", False) else "rejected"
            return {"response": safe_response, "intent": route, "status": status}

        except Exception as e:
            logger.error(f"Pipeline failure for {user_id}: {str(e)}")
            return {
                "response": "Hệ thống đang gặp sự cố. Vui lòng thử lại sau.",
                "intent": "fallback",
                "status": "error"
            }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _dispatch(
        self,
        route: str,
        user_id: str,
        message: str,
        history: List[Dict[str, Any]],
    ) -> str:
        """
        Call the correct agent based on router output.

        Args:
            route:    One of "rag", "crm", "advisor", "fallback".
            user_id:  Student identifier.
            message:  User message.
            history:  Conversation history.

        Returns:
            Raw response string from the selected agent.

        TODO: Implement all four branches:
              "crm"      → crm.run(user_id, message)
              "advisor"  → advisor.run(message, history)
              "fallback" → return handoff string (optionally call human_fallback.py)
              default    → rag.run(message)
        """
        # TODO: Replace with real dispatch logic
        if route == "fallback":
            return "Bạn muốn được kết nối với tư vấn viên của chúng tôi không?"
        
        if route == "advisor":
            return self.advisor.run(message, history)
        elif route == "crm":
            # Placeholder until CRMAgent is fully implemented
            return f"Dựa trên hồ sơ của bạn, chúng tôi đang xem xét các lựa chọn phù hợp nhất tại VinUni."
        elif route == "rag":
            return self.rag.run(message, user_id=user_id)
        
        # Default: rag
        logger.warning(f"Unknown route '{route}'. Falling back to RAG.")
        return self.rag.run(message)

    def _mock_route(self, message: str) -> str:
        """Deterministic keyword-based router for Mock mode."""
        msg = message.lower()
        if any(word in msg for word in ["hồ sơ", "điểm", "ielts", "gpa", "thông tin cá nhân"]):
            return "crm"
        if any(word in msg for word in ["ngành", "chọn", "tư vấn", "phù hợp", "match"]):
            return "advisor"
        return "rag"

    def _audit_log(
        self,
        user_id: str,
        input_data: Any,
        output_data: Any,
        judge_result: Dict,
    ) -> None:
        """
        Persist an audit record to the database.

        Args:
            user_id:      Student identifier.
            input_data:   Raw input (answers dict or message string).
            output_data:  Agent output before/after redaction.
            judge_result: Result dict from JudgeAgent.evaluate().

        TODO: Call db_service.save_audit_log(user_id, input_data, output_data, judge_result).
        TODO: Also append to audit_log.json for file-based compliance trail.
        """
        # TODO: Implement DB + file audit logging
        logger.info(f"AUDIT [{user_id}] judge_pass={judge_result.get('pass')} — Score: {judge_result.get('score')}")
        self.db_service.save_audit_log(user_id, str(input_data), str(output_data), judge_result)
