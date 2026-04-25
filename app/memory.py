"""
Conversation memory management using PostgreSQL.
Persists conversation history for each user.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models import ConversationHistory

logger = logging.getLogger(__name__)


class Memory:
    """
    Manages conversation history for users.
    Stores all messages in database for persistence and analytics.
    """
    
    def __init__(self, db: Session, max_history_length: int = 10):
        """
        Initialize memory manager.
        
        Args:
            db: SQLAlchemy database session
            max_history_length: Maximum messages to keep in context (for LLM prompt)
        """
        self.db = db
        self.max_history_length = max_history_length

    def get(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get recent conversation history for a user.
        Returns last N messages for context in LLM.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of dicts with keys: role, content, timestamp
        """
        try:
            # Get last N messages
            messages = self.db.query(ConversationHistory)\
                .filter(ConversationHistory.user_id == user_id)\
                .order_by(desc(ConversationHistory.timestamp))\
                .limit(self.max_history_length)\
                .all()
            
            # Reverse to get chronological order
            messages.reverse()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error retrieving memory for user {user_id}: {e}")
            return []

    def add(
        self, 
        user_id: str, 
        message: str,
        role: str = "user",
        agent_type: Optional[str] = None,
        sentiment_score: Optional[int] = None
    ) -> bool:
        """
        Add a message to conversation history.
        
        Args:
            user_id: User identifier
            message: Message content
            role: "user" or "assistant"
            agent_type: Which agent generated this ("rag", "crm", "advisor")
            sentiment_score: Detected sentiment (0-4)
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            entry = ConversationHistory(
                user_id=user_id,
                message=message,
                role=role,
                agent_type=agent_type,
                sentiment_score=sentiment_score,
                timestamp=datetime.utcnow()
            )
            self.db.add(entry)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error adding memory for user {user_id}: {e}")
            self.db.rollback()
            return False

    def clear(self, user_id: str) -> bool:
        """
        Clear all history for a user (e.g., new session).
        
        Args:
            user_id: User identifier
            
        Returns:
            True if cleared successfully
        """
        try:
            self.db.query(ConversationHistory)\
                .filter(ConversationHistory.user_id == user_id)\
                .delete()
            self.db.commit()
            logger.info(f"Cleared history for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing memory for user {user_id}: {e}")
            self.db.rollback()
            return False

    def get_full_history(
        self, 
        user_id: str,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get full conversation history for a time period.
        Useful for analytics or debugging.
        
        Args:
            user_id: User identifier
            days: How many days back to retrieve
            
        Returns:
            List of all messages in the period
        """
        try:
            cutoff = datetime.utcnow() - timedelta(days=days)
            messages = self.db.query(ConversationHistory)\
                .filter(
                    ConversationHistory.user_id == user_id,
                    ConversationHistory.timestamp >= cutoff
                )\
                .order_by(ConversationHistory.timestamp)\
                .all()
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "agent_type": msg.agent_type,
                    "sentiment": msg.sentiment_score,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error retrieving full history for user {user_id}: {e}")
            return []

    def get_conversation_count(self, user_id: str) -> int:
        """
        Get total number of messages for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Total message count
        """
        try:
            count = self.db.query(ConversationHistory)\
                .filter(ConversationHistory.user_id == user_id)\
                .count()
            return count
        except Exception as e:
            logger.error(f"Error counting messages for user {user_id}: {e}")
            return 0
