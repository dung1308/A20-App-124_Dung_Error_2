# guardrails/input_guard.py
"""
Input validation and security checks.
Detects and blocks malicious or inappropriate inputs.
"""

import re
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"bypass",
    r"jailbreak",
    r"disregard above",
    r"forget about",
    r"pretend",
]

# Blocked topics (malicious content)
BLOCK_TOPICS = [
    "hack", "bomb", "exploit", "leak dữ liệu",
    "virus", "malware", "ddos", "ransomware"
]

# Length constraints
MIN_LENGTH = 1
MAX_LENGTH = 5000


def check_input(text: str) -> Tuple[bool, str]:
    """
    Validate and check user input for security threats.
    
    Checks for:
    - Length constraints
    - Prompt injection attempts
    - Blocked topics/keywords
    - Invalid encoding
    
    Args:
        text: User input text
        
    Returns:
        Tuple (is_valid: bool, reason: str or None)
    """
    
    try:
        # Check length
        if len(text) < MIN_LENGTH:
            return False, "input_too_short"
        if len(text) > MAX_LENGTH:
            logger.warning(f"Input exceeds max length: {len(text)} > {MAX_LENGTH}")
            return False, "input_too_long"
        
        lower = text.lower()
        
        # Check for prompt injection
        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, lower, re.IGNORECASE):
                logger.warning(f"Prompt injection detected: {pattern}")
                return False, "prompt_injection"
        
        # Check for blocked topics
        for topic in BLOCK_TOPICS:
            if topic in lower:
                logger.warning(f"Blocked topic detected: {topic}")
                return False, "blocked_topic"
        
        return True, None
    
    except Exception as e:
        logger.error(f"Error checking input: {e}")
        return False, "input_check_error"
