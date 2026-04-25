# guardrails/audit.py
"""
Audit logging for compliance and debugging.
Records all system events with timestamps.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logs all system events for audit trail and compliance.
    Useful for debugging, compliance verification, and analytics.
    """
    
    def __init__(self, file: str = "audit_log.json"):
        """
        Initialize audit logger.
        
        Args:
            file: Path to audit log file
        """
        self.file = file

    def log(self, data: Dict[str, Any]) -> bool:
        """
        Log an event to audit trail.
        
        Args:
            data: Event data to log
            
        Returns:
            True if logged successfully
        """
        try:
            data["timestamp"] = datetime.utcnow().isoformat()
            
            with open(self.file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            
            return True
        except Exception as e:
            logger.error(f"Error writing audit log: {e}")
            return False

    @staticmethod
    def _get_timestamp() -> str:
        """
        Get current timestamp in ISO format.
        
        Returns:
            ISO format timestamp
        """
        return datetime.utcnow().isoformat()
