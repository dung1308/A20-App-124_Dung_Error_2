"""
agents/cv_agent.py
-----------------
Responsibility: Convert structured CVData into weighted major signals.
"""

import json
import logging
from typing import Dict, Any, List

from config import USE_MOCK
from services.llm_client import LLMClient
from services.db_service import DBService
from models.cv_schema import CVData, CVSignals
from utils.logger import get_logger

logger = get_logger(__name__)

SIGNAL_PROMPT = """
Analyze the student's CV data to extract signals for major matching at VinUni.
Below are the available majors at VinUni with their descriptions:
{major_descriptions}

Mapping Logic:
- Map skills to relevant majors.
- Map projects to domain interest.
- Map education to academic strength.
- Consider the student's overall profile and background.

Respond ONLY with a JSON object:
{
  "suggested_majors": ["major_id1", "major_id2"],
  "confidence": 0.85,
  "evidence": ["Point of evidence 1", "Point of evidence 2"]
} 
Ensure 'suggested_majors' only contains valid major IDs from the list provided.
"""

class CVAgent:
    def __init__(self):
        self.llm = None if USE_MOCK else LLMClient()
        self.db = DBService()

    def generate_signals(self, cv_data: CVData) -> CVSignals:
        """Analyze background to produce weighted signals."""
        try:
            if USE_MOCK:
                return CVSignals(suggested_majors=["cs"], confidence=0.9, evidence=["Mock: Tech background"])

            # Fetch major descriptions from DB for more accurate signal generation
            majors = self.db.get_majors()
            major_descriptions = []
            for major in majors:
                major_descriptions.append(f"- {major['name']} (ID: {major['id']}): {major['description']}")
            
            if not major_descriptions:
                logger.warning("No major descriptions found in DB, using generic prompt.")
                major_descriptions_str = "Available majors: cs, ee, me, bme, ba, finance, data_science, liberal_arts, architecture."
            else:
                major_descriptions_str = "\n".join(major_descriptions)

            prompt = SIGNAL_PROMPT.format(major_descriptions=major_descriptions_str) + f"\n\nCV Data: {cv_data.model_dump_json()}"
            response_text = self.llm.generate(prompt)
            
            if not response_text or response_text == "I don't know":
                return CVSignals(suggested_majors=[], confidence=0.0, evidence=[])

            clean_text = response_text.strip()
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[1].split("```")[0].strip()
                
            data = json.loads(clean_text)
            return CVSignals(**data)
        except Exception as e:
            logger.error(f"CVAgent failed: {e}")
            return CVSignals(suggested_majors=[], confidence=0.0, evidence=[])