# guardrails/output_guard.py
"""
Output redaction and sanitization.
Removes or masks sensitive information from responses.
"""

import logging
import re
from typing import List, Tuple

logger = logging.getLogger(__name__)

# PII patterns to redact
PII_PATTERNS = [
    (r"\b\d{9,12}\b", "[CMND_REDACTED]"),  # CMND/CCCD
    (r"\b\d{10,11}\b", "[PHONE_REDACTED]"),  # phone
    (r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_REDACTED]"),  # email
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN_REDACTED]"),  # Social Security
    (r"\b\d{16}\b", "[CARD_REDACTED]"),  # Credit card
]

# Sensitive keywords to mask
SENSITIVE_KEYWORDS = [
    'password', 'secret', 'token', 'api_key', 'private_key', 'bearer'
]


def redact(text: str) -> str:
    """
    Redact sensitive information from text.
    
    Removes or masks:
    - Passport/ID numbers (CMND/CCCD)
    - Phone numbers
    - Email addresses
    - Social Security Numbers
    - Credit card numbers
    - API keys and secrets
    
    Args:
        text: Text to redact
        
    Returns:
        Redacted text
    """
    if not text:
        return text
    
    redacted = text
    redacted_count = 0
    
    # Apply PII patterns
    for pattern, replacement in PII_PATTERNS:
        matches = len(re.findall(pattern, redacted))
        if matches > 0:
            redacted = re.sub(pattern, replacement, redacted, flags=re.IGNORECASE)
            redacted_count += matches
    
    # Check for sensitive keywords
    for keyword in SENSITIVE_KEYWORDS:
        if keyword.lower() in redacted.lower():
            # Find and mask lines containing sensitive keywords
            lines = redacted.split('\n')
            masked_lines = []
            for line in lines:
                if keyword.lower() in line.lower():
                    masked_lines.append('[SENSITIVE_INFO_REDACTED]')
                    logger.warning(f"Sensitive keyword '{keyword}' found in output and redacted")
                else:
                    masked_lines.append(line)
            redacted = '\n'.join(masked_lines)
            redacted_count += 1
    
    if redacted_count > 0:
        logger.debug(f"Redacted {redacted_count} sensitive items from output")
    
    return redacted


def sanitize(text: str) -> str:
    """
    Sanitize output for display (remove dangerous HTML/scripts).
    
    Args:
        text: Text to sanitize
        
    Returns:
        Sanitized text
    """
    if not text:
        return text
    
    sanitized = text
    
    # Remove HTML tags
    sanitized = re.sub(r'<[^>]+>', '', sanitized)
    
    # Remove common XSS patterns
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)
    
    # Remove script tags
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized
