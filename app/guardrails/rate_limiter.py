# guardrails/rate_limiter.py
"""
Rate limiter to prevent abuse.
Tracks per-user request counts and enforces limits.
"""

import time
import logging
from collections import defaultdict, deque
from typing import Tuple
from sqlalchemy.orm import Session
from models import RateLimitLog

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with memory leak prevention.
    
    Features:
    - Per-user request tracking
    - Automatic cleanup of old entries
    - Optional database persistence
    - Configurable window and max requests
    """
    
    def __init__(
        self,
        max_requests: int = 10,
        window_seconds: int = 60,
        max_tracked_users: int = 10000,
        db: Session = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Max requests allowed in window
            window_seconds: Time window in seconds
            max_tracked_users: Max users to track (prevents memory leak)
            db: Optional database session for persistence
        """
        self.max_requests = max_requests
        self.window = window_seconds
        self.max_tracked_users = max_tracked_users
        self.db = db
        
        # In-memory cache of request timestamps per user
        self.logs: dict[str, deque] = defaultdict(deque)
        self.last_cleanup = time.time()

    def allow(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if request is allowed for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple (allowed: bool, reason: str)
        """
        now = time.time()
        
        # Periodic cleanup to prevent memory leak
        if now - self.last_cleanup > 300:  # Every 5 minutes
            self._cleanup_old_entries(now)
            self.last_cleanup = now
        
        # Check if we're tracking too many users
        if len(self.logs) > self.max_tracked_users:
            logger.warning(
                f"Rate limiter tracking {len(self.logs)} users, "
                f"exceeds max {self.max_tracked_users}. Triggering cleanup."
            )
            self._cleanup_old_entries(now)
        
        q = self.logs[user_id]
        
        # Remove timestamps outside the window
        while q and now - q[0] > self.window:
            q.popleft()
        
        # Check if limit exceeded
        if len(q) >= self.max_requests:
            logger.debug(f"Rate limit exceeded for user {user_id}")
            self._log_to_db(user_id, now, allowed=False)
            return False, "rate_limit_exceeded"
        
        # Add current request
        q.append(now)
        self._log_to_db(user_id, now, allowed=True)
        return True, None

    def _cleanup_old_entries(self, now: float) -> None:
        """
        Remove users with no recent activity.
        Prevents unbounded growth of in-memory cache.
        
        Args:
            now: Current time
        """
        cleanup_threshold = now - (self.window * 5)  # Keep data for 5 windows
        
        # Find users to remove
        users_to_remove = []
        for user_id, timestamps in self.logs.items():
            # Remove old timestamps from queue
            while timestamps and now - timestamps[0] > self.window:
                timestamps.popleft()
            
            # If queue is empty and user inactive, remove from tracking
            if not timestamps:
                users_to_remove.append(user_id)
        
        # Remove inactive users
        for user_id in users_to_remove:
            del self.logs[user_id]
        
        if users_to_remove:
            logger.debug(f"Cleaned up {len(users_to_remove)} inactive users")

    def _log_to_db(self, user_id: str, timestamp: float, allowed: bool) -> None:
        """
        Optionally log to database for analytics.
        
        Args:
            user_id: User identifier
            timestamp: Request timestamp
            allowed: Whether request was allowed
        """
        if not self.db:
            return
        
        try:
            log_entry = RateLimitLog(
                user_id=user_id,
                request_timestamp=timestamp,
                allowed=1 if allowed else 0
            )
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            logger.error(f"Error logging rate limit to DB: {e}")
            self.db.rollback()

    def reset(self, user_id: str) -> None:
        """
        Reset rate limit for a user (e.g., new day).
        
        Args:
            user_id: User identifier
        """
        if user_id in self.logs:
            self.logs[user_id].clear()
            logger.info(f"Reset rate limit for user {user_id}")

    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dict with stats
        """
        return {
            "tracked_users": len(self.logs),
            "max_tracked_users": self.max_tracked_users,
            "max_requests_per_window": self.max_requests,
            "window_seconds": self.window
        }
