"""
agents/cv_agent.py
-----------------
Responsibility: Convert structured CVData into weighted major signals.
"""

import json
import logging
from typing import Dict
from config import get_gemini_model
from models.cv_schema import CVData, CVSignals
from utils.logger import get_logger

logger = get_logger(__name__)

SIGNAL_PROMPT = """
Analyze the student's CV data to extract signals for major matching at VinUni.
Majors: cs, ee, me, bme, ba, finance, data_science, liberal_arts, architecture

Mapping Logic:
- Map skills to relevant majors.
- Map projects to domain interest.
- Map education to academic strength.

Respond ONLY with a JSON object:
{
  "suggested_majors": ["major_id1", "major_id2"],
  "confidence": 0.85,
  "evidence": ["Point of evidence 1", "Point of evidence 2"]
}
"""

class CVAgent:
    def __init__(self):
        self.model = get_gemini_model()

    def generate_signals(self, cv_data: CVData) -> CVSignals:
        """Analyze background to produce weighted signals."""
        try:
            prompt = f"{SIGNAL_PROMPT}\n\nCV Data: {cv_data.model_dump_json()}"
            response = self.model.generate_content(prompt)
            
            clean_text = response.text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                
            data = json.loads(clean_text)
            return CVSignals(**data)
        except Exception as e:
            logger.error(f"CVAgent failed: {e}")
            return CVSignals(suggested_majors=[], confidence=0.0, evidence=[])