"""
agents/advisor.py
-----------------
Responsibility: AdvisorAgent handles two tasks:
  1. match_majors(answers) → Top 3 VinUni majors from the wizard flow.
  2. run(message, history)  → Personalized guidance in free-form chat.

Uses get_gemini_model() from config.py (hinge rule — never imports genai directly).
Validates that returned major IDs exist in the 9-item VINUNI_MAJORS list.
Returns fallback=True if Gemini output is ambiguous or cannot be validated.
"""

import json
import logging
from typing import List, Dict, Any

from config import get_gemini_model, USE_MOCK
from models.cv_schema import CVSignals
from utils.logger import get_logger

logger = get_logger(__name__)

# The only valid major IDs. Any AI output outside this set is rejected.
VALID_IDS = {
    "cs", "ee", "me", "bme", "ba",
    "finance", "data_science", "liberal_arts", "architecture",
}

VINUNI_MAJORS_LOOKUP: Dict[str, Dict] = {
    "cs":           {"name": "Khoa học Máy tính",         "what_students_do": "Sinh viên CS tại VinUni làm việc với AI, xây dựng ứng dụng, nghiên cứu thuật toán và thực tập tại các công ty công nghệ như VNG, KMS, FPT."},
    "ee":           {"name": "Kỹ thuật Điện — Điện tử",   "what_students_do": "Sinh viên EE thiết kế mạch điện, lập trình vi điều khiển, làm dự án IoT và thực tập tại các nhà máy sản xuất điện tử."},
    "me":           {"name": "Kỹ thuật Cơ khí",           "what_students_do": "Sinh viên ME làm với CAD/CAM, in 3D, robotics và thực tập tại các nhà máy hoặc công ty sản xuất."},
    "bme":          {"name": "Kỹ thuật Y sinh",            "what_students_do": "Sinh viên BME thiết kế thiết bị y tế, nghiên cứu cùng bệnh viện, có thể học tiếp y khoa hoặc làm trong ngành dược."},
    "ba":           {"name": "Quản trị Kinh doanh",        "what_students_do": "Sinh viên BA làm case study thực tế, tham gia cuộc thi khởi nghiệp, thực tập tại công ty lớn hoặc startup."},
    "finance":      {"name": "Tài chính",                  "what_students_do": "Sinh viên Finance học mô hình tài chính, phân tích cổ phiếu, thực tập tại ngân hàng, quỹ đầu tư."},
    "data_science": {"name": "Khoa học Dữ liệu",           "what_students_do": "Sinh viên Data Science làm Python, SQL, xây model dự đoán và thực tập tại các công ty dữ liệu, fintech."},
    "liberal_arts": {"name": "Khoa học Xã hội & Nhân văn", "what_students_do": "Sinh viên CAS viết nghiên cứu, tranh luận, phân tích xã hội — hướng đến luật, báo chí, chính sách công."},
    "architecture": {"name": "Kiến trúc",                  "what_students_do": "Sinh viên Kiến trúc làm đồ án thiết kế, học AutoCAD/Revit, thực tập tại công ty kiến trúc."},
}

MATCH_SYSTEM_PROMPT = """
Bạn là AI tư vấn tuyển sinh VinUni. Phân tích câu trả lời học sinh và chọn đúng 3 ngành phù hợp nhất.

Ngành hợp lệ (chỉ dùng các id này):
cs, ee, me, bme, ba, finance, data_science, liberal_arts, architecture

Yêu cầu:
1. Trả về JSON thuần — không markdown, không giải thích ngoài JSON.
2. match_reason phải giải thích rõ ràng dựa trên 2 nguồn:
   - 'Dựa trên lựa chọn của bạn': Liên kết với Interests/Strengths/Work-style từ Wizard.
   - 'Dựa trên hồ sơ (CV)': Liên kết với kinh nghiệm/kỹ năng/thành tựu từ CV (nếu có).
3. Nếu dislikes mâu thuẫn với ngành → không chọn ngành đó.
4. Nếu không đủ tín hiệu rõ ràng → trả fallback: true, top3: [].
5. CÔNG THỨC TÍNH ĐIỂM (match_score 0-100):
   - Trọng số mặc định: 0.6 * Wizard Answers + 0.4 * CV Signals.
   - ƯU TIÊN TUYỆT ĐỐI: Nếu có mâu thuẫn giữa Wizard và CV (VD: CV có kinh nghiệm CS nhưng Wizard nói "Ghét lập trình"), phải ưu tiên Wizard và loại bỏ ngành đó khỏi Top 3.
   - ĐIỀU CHỈNH TRỌNG SỐ:
     * Nếu CV trống hoặc chất lượng thấp (Confidence < 0.4): Giảm trọng số CV xuống 0.2 (Wizard 0.8).
     * Nếu CV cực kỳ nhất quán với Wizard: Tăng trọng số CV lên tối đa 0.5 (Wizard 0.5).
   - Kết quả cuối cùng phải được chuẩn hóa (normalized) trong khoảng 0-100.
6. PHÁT HIỆN MÂU THUẪN: Nếu phát hiện mâu thuẫn giữa nền tảng trong CV và sở thích thực tế của học sinh (ngay cả với các ngành không được chọn), hãy đề cập ngắn gọn sự mâu thuẫn này trong phần giải thích của ngành phù hợp nhất để thể hiện sự khách quan.

Format bắt buộc:
{"top3": [{"major_id": "...", "match_reason": "...", "match_score": 0}], "fallback": false}
"""


class AdvisorAgent:
    """
    Provides major-matching and personalized guidance using Gemini.
    """

    def __init__(self):
        # TODO: Store model reference at init to avoid repeated config lookups
        self.model = get_gemini_model()

    def match_majors(self, answers: Dict[str, Any], cv_signals: CVSignals = None) -> Dict[str, Any]:
        """
        Core wizard flow: analyse 4-step answers and return Top 3 majors.

        Args:
            answers: Dict with keys interests (list), strengths (list),
                     dislikes (list), work_style (str).

        Returns:
            Dict: {top3: [...], fallback: bool}
            Each top3 item has: major_id, major_name, match_reason,
                                match_score, what_students_do.

        TODO: 1. Build user prompt from answers using _build_match_prompt(answers).
        TODO: 2. Call self.model.generate_content(prompt).
        TODO: 3. Parse JSON response — catch json.JSONDecodeError → return fallback.
        TODO: 4. Validate every major_id is in VALID_IDS — reject unknowns → fallback.
        TODO: 5. Enrich each item with major_name + what_students_do from VINUNI_MAJORS_LOOKUP.
        TODO: 6. Sort top3 by match_score descending before returning.
        TODO: 7. Wrap all LLM + parse logic in try/except → return fallback on any error.
        """
        logger.info("AdvisorAgent.match_majors() called")

        try:
            # Check for missing data - return fallback (handoff signal)
            # Fix: Ensure all keys exist, even if they are empty lists (don't use all() on values)
            required_keys = ["interests", "strengths", "dislikes", "work_style"]
            if not all(k in answers for k in required_keys):
                logger.warning("AdvisorAgent: Missing data in wizard answers, returning fallback/handoff.")
                return {"top3": [], "fallback": True}

            # TODO: 1. Build user prompt from answers using _build_match_prompt(answers).
            prompt = self._build_match_prompt(answers, cv_signals)

            # TODO: 2. Call self.model.generate_content(prompt).
            if not self.model: return {"top3": [], "fallback": True}
            response = self.model.generate_content(prompt)

            # TODO: 3. Parse JSON response — catch json.JSONDecodeError → return fallback.
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                clean_text = clean_text.split("```")[1].replace("json", "", 1).strip()
            data = json.loads(clean_text)

            # TODO: 4. Validate every major_id is in VALID_IDS — reject unknowns → fallback.
            # TODO: 5. Enrich each item with major_name + what_students_do from VINUNI_MAJORS_LOOKUP.
            enriched = self._validate_and_enrich(data.get("top3", []))

            # TODO: 6. Sort top3 by match_score descending before returning.
            enriched.sort(key=lambda x: x.get("match_score", 0), reverse=True)

            # TODO: 7. Wrap all LLM + parse logic in try/except → return fallback on any error.
            return {"top3": enriched, "fallback": data.get("fallback", False)}
        except (json.JSONDecodeError, ValueError, Exception) as e:
            logger.error(f"AdvisorAgent.match_majors failed: {e}")
            return {"top3": [], "fallback": True}

        # TODO: Remove stub and implement Gemini call + validation
        return {"top3": [], "fallback": True}

    def run(self, message: str, history: List[Dict[str, Any]]) -> str:
        """
        Free-form advisor chat: personalized guidance on major choice.
        Called by Pipeline when router returns "advisor".

        Args:
            message: User question about which major to choose.
            history: Prior conversation turns for context.

        Returns:
            Guidance text in Vietnamese.

        TODO: 1. Build a chat prompt with MATCH_SYSTEM_PROMPT + last 3 history turns + message.
        TODO: 2. Call self.model.generate_content(prompt).
        TODO: 3. Return response.text, stripped of leading/trailing whitespace.
        TODO: 4. Wrap in try/except → return polite error string on failure.
        """
        logger.info("AdvisorAgent.run() called")

        try:
            if USE_MOCK:
                return ("Dựa trên sở thích của bạn về công nghệ và giải quyết vấn đề, "
                        "ngành Khoa học Máy tính hoặc Kỹ thuật tại VinUni sẽ là lựa chọn tuyệt vời. "
                        "Bạn có muốn biết thêm về cơ hội thực tập tại các tập đoàn lớn không?")

            # TODO: 1. Build a chat prompt with MATCH_SYSTEM_PROMPT + last 3 history turns + message.
            hist_ctx = "\n".join([
                f"{'Học sinh' if t.get('role')=='user' else 'Cố vấn'}: {t.get('content')}" 
                for t in history[-3:] 
                if "role" in t and "content" in t
            ])
            prompt = f"{MATCH_SYSTEM_PROMPT}\n\nLịch sử trò chuyện:\n{hist_ctx}\n\nCâu hỏi: {message}"

            # TODO: 2. Call self.model.generate_content(prompt).
            if not self.model: return "Hệ thống đang bận. Vui lòng thử lại sau."
            response = self.model.generate_content(prompt)

            # TODO: 3. Return response.text, stripped of leading/trailing whitespace.
            return response.text.strip()

        # TODO: 4. Wrap in try/except → return polite error string on failure.
        except Exception as e:
            logger.error(f"AdvisorAgent.run failure: {e}")
            return "Tôi xin lỗi, tôi gặp vấn đề khi xử lý câu hỏi này. Bạn có thể hỏi lại về các ngành học tại VinUni không?"

        # TODO: Replace stub with real Gemini response
        return "AdvisorAgent chưa được implement."

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_match_prompt(self, answers: Dict[str, Any], cv_signals: CVSignals = None) -> str:
        """
        Format the wizard answers into a Gemini user prompt.

        Args:
            answers: Dict with interests, strengths, dislikes, work_style.

        Returns:
            Full prompt string combining MATCH_SYSTEM_PROMPT + answers.

        TODO: Format interests/strengths/dislikes lists as Vietnamese bullet strings.
        TODO: Append work_style as a single line.
        """
        # TODO: Implement prompt formatting
        interests = ", ".join(answers.get("interests", []))
        strengths = ", ".join(answers.get("strengths", []))
        dislikes = ", ".join(answers.get("dislikes", []))
        work_style = answers.get("work_style", "")

        user_summary = (
            f"1. Sở thích: {interests}\n2. Thế mạnh: {strengths}\n"
            f"3. Điều không thích: {dislikes}\n4. Phong cách làm việc: {work_style}"
        )

        cv_summary = ""
        if cv_signals:
            # Fix: Handle cv_signals as either an object or a dictionary
            is_dict = isinstance(cv_signals, dict)
            evidence = cv_signals.get("evidence", []) if is_dict else getattr(cv_signals, "evidence", [])
            suggested_list = cv_signals.get("suggested_majors", []) if is_dict else getattr(cv_signals, "suggested_majors", [])
            confidence = cv_signals.get("confidence", 0) if is_dict else getattr(cv_signals, "confidence", 0)

            evidence_str = "\n- ".join(evidence) if evidence else "Không có thông tin cụ thể."
            suggested = ", ".join(suggested_list)
            cv_summary = (
                f"\n\nTín hiệu từ CV (Dùng để tham khảo thêm):\n"
                f"- Độ tin cậy (Confidence): {confidence}\n"
                f"- Các ngành gợi ý từ CV: {suggested}\n"
                f"- Minh chứng: {evidence_str}"
            )

        return f"{MATCH_SYSTEM_PROMPT}\n\nDưới đây là thông tin của học sinh:\n{user_summary}{cv_summary}"

    def _validate_and_enrich(self, top3: List[Dict]) -> List[Dict]:
        """
        Validate major IDs and enrich each item with display data.

        Args:
            top3: Raw list of dicts from Gemini response.

        Returns:
            Enriched list, or raises ValueError if any major_id is invalid.

        TODO: For each item, check major_id in VALID_IDS — raise ValueError if not.
        TODO: Look up major_name and what_students_do from VINUNI_MAJORS_LOOKUP.
        TODO: Merge into the item dict and return.
        """
        enriched = []
        for item in top3:
            major_id = item.get("major_id")
            # TODO: Remove pass and implement validation + enrichment
            if major_id not in VALID_IDS:
                raise ValueError(f"Invalid major_id returned by AI: {major_id}")
            info = VINUNI_MAJORS_LOOKUP[major_id]
            # Mapping keys to match MajorResult pydantic schema
            enriched.append({
                "major_id": major_id,
                "major_name": info["name"],
                "match_reason": item.get("match_reason", ""),
                "match_score": item.get("match_score", 0),
                "what_students_do": info["what_students_do"]
            })
        return enriched
