# guardrails/anomaly.py
"""
Session anomaly detection.
Tracks suspicious user behavior patterns.
"""

import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
from sqlalchemy.orm import Session
from models import SecurityEvent

logger = logging.getLogger(__name__)


class SessionAnomaly:
    """
    Detects anomalous user behavior.
    Tracks suspicious patterns over time.
    """
    
    def __init__(
        self,
        threshold: int = 3,
        time_window_minutes: int = 30,
        db: Session = None
    ):
        """
        Initialize anomaly detector.
        
        Args:
            threshold: Number of violations before marking suspicious
            time_window_minutes: Time window for tracking violations
            db: Optional database session
        """
        self.threshold = threshold
        self.time_window = timedelta(minutes=time_window_minutes)
        self.db = db
        
        # In-memory tracking
        self.violations: Dict[str, List[dict]] = defaultdict(list)

    def flag(
        self,
        user_id: str,
        reason: str,
        details: dict = None
    ) -> None:
        """
        Record a security violation for user.
        
        Args:
            user_id: User identifier
            reason: Type of violation (prompt_injection, blocked_topic, etc)
            details: Optional additional details
        """
        now = datetime.utcnow()
        violation = {
            "reason": reason,
            "timestamp": now,
            "details": details or {}
        }
        
        self.violations[user_id].append(violation)
        
        # Log to database
        if self.db:
            self._save_to_db(user_id, reason, details)
        
        logger.warning(
            f"User {user_id} flagged for {reason}. "
            f"Violations: {len(self.violations[user_id])}"
        )

    def is_suspicious(self, user_id: str) -> bool:
        """
        Check if user shows suspicious behavior.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if user is suspicious
        """
        # Clean up old violations
        self._cleanup_old_violations(user_id)
        
        violation_count = len(self.violations.get(user_id, []))
        is_suspicious = violation_count >= self.threshold
        
        if is_suspicious:
            logger.warning(
                f"User {user_id} marked as suspicious. "
                f"Violations: {violation_count}"
            )
        
        return is_suspicious

    def _cleanup_old_violations(self, user_id: str) -> None:
        """
        Remove violations outside the time window.
        
        Args:
            user_id: User identifier
        """
        if user_id not in self.violations:
            return
        
        now = datetime.utcnow()
        cutoff = now - self.time_window
        
        self.violations[user_id] = [
            v for v in self.violations[user_id]
            if v["timestamp"] > cutoff
        ]

    def _save_to_db(
        self,
        user_id: str,
        event_type: str,
        details: dict
    ) -> None:
        """
        Save security event to database.
        
        Args:
            user_id: User identifier
            event_type: Type of security event
            details: Event details
        """
        try:
            event = SecurityEvent(
                user_id=user_id,
                event_type=event_type,
                details=details or {},
                severity="warning",
                timestamp=datetime.utcnow()
            )
            self.db.add(event)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving security event: {e}")
            self.db.rollback()

    def get_violations(
        self,
        user_id: str
    ) -> List[dict]:
        """
        Get recent violations for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of violation records
        """
        self._cleanup_old_violations(user_id)
        return self.violations.get(user_id, [])

    def reset(self, user_id: str) -> None:
        """
        Reset violations for a user (e.g., new day).
        
        Args:
            user_id: User identifier
        """
        if user_id in self.violations:
            self.violations[user_id].clear()
            logger.info(f"Reset violations for user {user_id}")
