# guardrails/monitoring.py
"""
System monitoring and metrics collection.
Tracks events for analytics and alerting.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
from sqlalchemy.orm import Session
from models import SystemMetric

logger = logging.getLogger(__name__)


class Monitoring:
    """
    Monitor system health and collect metrics.
    
    Tracks:
    - Rate limit violations
    - Input blocks
    - Judge failures
    - LLM costs
    - Response times
    """
    
    def __init__(self, db: Session = None):
        """
        Initialize monitoring.
        
        Args:
            db: Optional database session for persistent metrics
        """
        self.db = db
        
        # In-memory event log with timestamps
        self.events: List[Dict[str, Any]] = []
        
        # Counters
        self.rate_limit_hits = 0
        self.blocks = 0
        self.judge_fail = 0
        self.llm_errors = 0
        self.successful_responses = 0

    def record(
        self,
        event_type: str,
        user_id: str = None,
        details: Dict[str, Any] = None,
        metric_value: float = None
    ) -> None:
        """
        Record an event with timestamp.
        
        Args:
            event_type: Type of event (rate_limit, block, judge_fail, etc)
            user_id: Optional user identifier
            details: Optional additional details
            metric_value: Optional numeric metric value
        """
        event = {
            "type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "details": details or {}
        }
        
        self.events.append(event)
        
        # Update counters
        if event_type == "rate_limit":
            self.rate_limit_hits += 1
        elif event_type == "block":
            self.blocks += 1
        elif event_type == "judge_fail":
            self.judge_fail += 1
        elif event_type == "llm_error":
            self.llm_errors += 1
        elif event_type == "success":
            self.successful_responses += 1
        
        # Log to database if enabled
        if self.db and metric_value is not None:
            self._save_metric(event_type, metric_value)

    def _save_metric(self, metric_name: str, value: float) -> None:
        """Save metric to database"""
        try:
            metric = SystemMetric(
                metric_name=metric_name,
                value=value,
                timestamp=datetime.utcnow()
            )
            self.db.add(metric)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error saving metric {metric_name}: {e}")
            self.db.rollback()

    def report(self, hours: int = 24) -> Dict[str, Any]:
        """
        Generate monitoring report for last N hours.
        
        Args:
            hours: How far back to look
            
        Returns:
            Dict with summary statistics
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent = [e for e in self.events if e["timestamp"] > cutoff]
        
        event_counts = defaultdict(int)
        for event in recent:
            event_counts[event["type"]] += 1
        
        return {
            "period_hours": hours,
            "total_events": len(recent),
            "rate_limit_hits": self.rate_limit_hits,
            "blocks": self.blocks,
            "judge_failures": self.judge_fail,
            "llm_errors": self.llm_errors,
            "successful_responses": self.successful_responses,
            "event_breakdown": dict(event_counts),
            "success_rate": (
                self.successful_responses / 
                (self.successful_responses + self.judge_fail + self.llm_errors)
                if (self.successful_responses + self.judge_fail + self.llm_errors) > 0
                else 0
            ),
            "timestamp": datetime.utcnow().isoformat()
        }

    def get_events_by_type(
        self,
        event_type: str,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get specific events for debugging.
        
        Args:
            event_type: Type of event to filter
            hours: How far back to look
            
        Returns:
            List of matching events
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            e for e in self.events
            if e["type"] == event_type and e["timestamp"] > cutoff
        ]

    def get_user_activity(
        self,
        user_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get activity summary for a specific user.
        
        Args:
            user_id: User identifier
            hours: How far back to look
            
        Returns:
            Dict with user activity stats
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        user_events = [
            e for e in self.events
            if e["user_id"] == user_id and e["timestamp"] > cutoff
        ]
        
        event_counts = defaultdict(int)
        for event in user_events:
            event_counts[event["type"]] += 1
        
        return {
            "user_id": user_id,
            "period_hours": hours,
            "total_events": len(user_events),
            "event_types": dict(event_counts),
            "first_event": user_events[0]["timestamp"].isoformat() if user_events else None,
            "last_event": user_events[-1]["timestamp"].isoformat() if user_events else None
        }

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get system health status.
        
        Returns:
            Dict indicating system health
        """
        # Calculate rates
        total_events = (
            self.rate_limit_hits + 
            self.blocks + 
            self.judge_fail +
            self.llm_errors +
            self.successful_responses
        )
        
        if total_events == 0:
            error_rate = 0
        else:
            error_rate = (
                (self.judge_fail + self.blocks) / total_events * 100
            )
        
        # Determine health
        if error_rate > 10:
            health = "CRITICAL"
        elif error_rate > 5:
            health = "WARNING"
        else:
            health = "HEALTHY"
        
        return {
            "status": health,
            "error_rate": f"{error_rate:.2f}%",
            "total_events": total_events,
            "events_in_memory": len(self.events),
            "timestamp": datetime.utcnow().isoformat()
        }

    def cleanup_old_events(self, hours: int = 24) -> int:
        """
        Remove old events from memory (doesn't affect DB).
        
        Args:
            hours: Remove events older than this many hours
            
        Returns:
            Number of events removed
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        initial_count = len(self.events)
        
        self.events = [e for e in self.events if e["timestamp"] > cutoff]
        
        removed = initial_count - len(self.events)
        if removed > 0:
            logger.info(f"Cleaned up {removed} old monitoring events")
        
        return removed
