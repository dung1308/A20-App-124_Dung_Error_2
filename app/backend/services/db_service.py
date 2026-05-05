"""
services/db_service.py
----------------------
Responsibility: All PostgreSQL interactions via SQLAlchemy ORM.
Single point of DB access — no other file runs raw SQL or uses sessions directly.

Tables managed here:
  - ConversationHistory  (chat messages per user)
  - Student              (CRM profiles)
  - AuditLog             (compliance trail)
  - SecurityEvent        (guardrail events)
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from collections import defaultdict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import get_database_url, USE_MOCK
from models.schemas import User, ChatMessage, ChatSession
from utils.logger import get_logger

logger = get_logger(__name__)

# TODO: Import SQLAlchemy Session and ORM models once models/schemas.py is complete
# from sqlalchemy.orm import Session
# from models.schemas import ConversationHistory, Student, AuditLog, SecurityEvent
# from database import get_db_session


class DBService:
    """
    Provides high-level data access methods for all pipeline components.
    All methods accept and return plain Python dicts — no ORM objects leak out.
    """

    def __init__(self):
        self.use_mock = USE_MOCK
        if self.use_mock:
            # user_id -> list of message dicts
            self._history: Dict[str, List[Dict]] = defaultdict(list)
            # user_id -> profile dict
            self._profiles: Dict[str, Dict[str, Any]] = {}
            logger.info("DBService initialised in MOCK mode (in-memory)")
        else:
            engine = create_engine(get_database_url())
            # Ensure tables exist
            from models.schemas import Base
            Base.metadata.create_all(bind=engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            # TODO: Accept a SQLAlchemy Session factory or use dependency injection
            #       via FastAPI's Depends(get_db) pattern.
            logger.info("DBService initialised with PostgreSQL engine")

    # ------------------------------------------------------------------
    # Conversation history
    # ------------------------------------------------------------------

    def save_message(self, user_id: str, role: str, content: str, agent_type: str = "") -> None:
        """
        Persist one conversation turn to ConversationHistory.

        Args:
            user_id:    Student identifier.
            role:       "user" or "assistant".
            content:    Message text.
            agent_type: Which agent generated this (rag/crm/advisor/judge).

        TODO: 1. Create a ConversationHistory ORM object with all fields + timestamp.
        TODO: 2. Add to DB session and commit.
        TODO: 3. Log at DEBUG level (do NOT log content — may contain PII).
        """
        if self.use_mock:
            self._history[user_id].append({
                "role": role,
                "content": content,
                "agent_type": agent_type,
                "timestamp": datetime.utcnow()
            })
            logger.debug(f"DBService.save_message(MOCK) — user={user_id}, role={role}")
            return

        with self.SessionLocal() as session:
            new_msg = ChatMessage(
                user_id=user_id,
                role=role,
                content=content,
                agent_type=agent_type
            )
            session.add(new_msg)
            session.commit()
        logger.debug(f"DBService.save_message() — user={user_id}, role={role}")
        # TODO: Implement DB write

    def get_history(self, user_id: str, limit: int = 20) -> List[Dict[str, str]]:
        """
        Fetch the most recent N conversation turns for a user.

        Args:
            user_id: Student identifier.
            limit:   Max number of turns to return (default 20).

        Returns:
            List of dicts: [{"role": "user"|"assistant", "content": "..."}]
            Ordered oldest → newest.

        TODO: 1. Query ConversationHistory filtered by user_id, ordered by timestamp DESC, limit N.
        TODO: 2. Reverse to get oldest → newest order.
        TODO: 3. Map ORM objects to plain dicts.
        TODO: 4. Return empty list (not raise) if user has no history.
        """
        if self.use_mock:
            msgs = self._history.get(user_id, [])
            # Return last N turns, mapped to standard role/content format
            history = [{"role": m["role"], "content": m["content"]} for m in msgs[-limit:]]
            logger.debug(f"DBService.get_history(MOCK) — user={user_id}, found {len(history)} turns")
            return history

        with self.SessionLocal() as session:
            msgs = session.query(ChatMessage)\
                .filter(ChatMessage.user_id == user_id)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(limit)\
                .all()
            history = [{"role": m.role, "content": m.content} for m in reversed(msgs)]
            logger.debug(f"DBService.get_history() — user={user_id}, found {len(history)} turns")
            return history
        # TODO: Implement DB read

    # ------------------------------------------------------------------
    # Student profiles (CRM)
    # ------------------------------------------------------------------

    def get_student_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch student profile from the Student table.

        Args:
            user_id: Student identifier.

        Returns:
            Profile dict or None if user not found.

        TODO: 1. Query Student table by user_id.
        TODO: 2. Return profile_data JSON field as a Python dict.
        TODO: 3. Return None (do NOT raise) if not found.
        """
        if self.use_mock:
            profile = self._profiles.get(user_id)
            logger.debug(f"DBService.get_student_profile(MOCK) — user={user_id}, found={profile is not None}")
            return profile

        # TODO: Implement DB read for production
        return None

    def upsert_student_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """
        Insert or update a student's profile.

        Args:
            user_id:      Student identifier.
            profile_data: Dict of profile fields (gpa, ielts, interests, etc.).

        TODO: 1. Check if Student with user_id exists.
        TODO: 2. If yes → update profile_data and updated_at.
        TODO: 3. If no  → insert new Student row.
        TODO: 4. Commit session.
        """
        if self.use_mock:
            self._profiles[user_id] = profile_data
            logger.debug(f"DBService.upsert_student_profile(MOCK) — user={user_id}")
            return

        # TODO: Implement DB upsert for production
        return None

    def create_user_if_not_exists(self, user_id: str) -> None:
        """
        Ensure a user record exists in the users table.

        Args:
            user_id: Student identifier.
        """
        if self.use_mock:
            logger.debug(f"DBService.create_user_if_not_exists(MOCK) — user={user_id}")
            return

        with self.SessionLocal() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                new_user = User(user_id=user_id)
                session.add(new_user)
                session.commit()
                logger.info(f"DBService: Created new user record for {user_id}")

    # ------------------------------------------------------------------
    # Audit logging
    # ------------------------------------------------------------------

    def save_audit_log(
        self,
        user_id: str,
        input_text: str,
        output_text: str,
        judge_result: Dict[str, Any],
    ) -> None:
        """
        Persist an audit record for compliance and debugging.

        Args:
            user_id:      Student identifier.
            input_text:   Sanitised user input.
            output_text:  Final agent response (post-redaction).
            judge_result: Dict from JudgeAgent.evaluate().

        TODO: 1. Create AuditLog ORM object with all fields + datetime.utcnow().
        TODO: 2. Store judge_result as JSON in the judge_result column.
        TODO: 3. Commit session.
        TODO: 4. Also append a line to audit_log.json for file-based compliance trail.
        """
        logger.info(f"DBService.save_audit_log() — user={user_id}, pass={judge_result.get('pass')} [NOT PERSISTED]")
        # TODO: Implement DB write + JSON file append
