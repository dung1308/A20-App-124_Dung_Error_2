"""
Human fallback/handoff system.
Routes complex issues to human advisors.
"""

import logging
import requests
from typing import Dict, Optional, Any
from config import HUMAN_WEBHOOK

logger = logging.getLogger(__name__)


def send_to_human(
    user_id: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Escalate conversation to human advisor.
    
    Args:
        user_id: User identifier
        message: User message/context
        context: Optional additional context
        
    Returns:
        True if sent successfully, False otherwise
    """
    try:
        payload = {
            "user_id": user_id,
            "message": message,
            "context": context or {}
        }
        
        response = requests.post(
            HUMAN_WEBHOOK,
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully handed off user {user_id} to human advisor")
            return True
        else:
            logger.error(f"Handoff failed with status {response.status_code}")
            return False
    
    except requests.exceptions.Timeout:
        logger.error("Handoff webhook timeout")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending to human advisor: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in human fallback: {e}")
        return False
