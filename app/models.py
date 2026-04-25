"""
Database models for Smart Recruitment System
"""

from sqlalchemy import Column, String, Text, Integer, DateTime, Float, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Student(Base):
    """Student/User profile in CRM system"""
    __tablename__ = "students"

    user_id = Column(String(100), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True)
    
    # Application status: "thiếu học bạ", "hồ sơ đầy đủ", "đã nộp", "trúng tuyển", etc
    status = Column(String(50), default="mới tạo")
    
    # Intended major/program
    major = Column(String(255), nullable=True)
    
    # Additional metadata as JSON
    metadata_json = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_student_created', 'created_at'),
    )


class ConversationHistory(Base):
    """Conversation history for each user"""
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), index=True, nullable=False)
    
    # "user" or "assistant"
    role = Column(String(20), nullable=False)
    
    # The message content
    content = Column(Text, nullable=False)
    
    # Optional: which agent generated this (rag/crm/advisor)
    agent_type = Column(String(50), nullable=True)
    
    # Optional: user sentiment at this message
    sentiment_score = Column(Integer, nullable=True)  # 0-4 scale
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_conversation_user_timestamp', 'user_id', 'timestamp'),
    )


class AuditLog(Base):
    """Audit trail for all system actions"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), index=True, nullable=False)
    
    # Input from user
    input_text = Column(Text, nullable=False)
    
    # Output from system
    output_text = Column(Text, nullable=False)
    
    # Judge result as JSON
    judge_result = Column(JSON, nullable=True)
    
    # Any security flags
    flags = Column(JSON, default=[])  # List of flags: ["rate_limit", "prompt_injection", etc]
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_audit_user_timestamp', 'user_id', 'timestamp'),
    )


class RateLimitLog(Base):
    """Track rate limit violations for analysis"""
    __tablename__ = "rate_limit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), index=True, nullable=False)
    
    # Unix timestamp when request was made
    request_timestamp = Column(Float, nullable=False)
    
    # Whether request was allowed (True) or blocked (False)
    allowed = Column(Integer, default=1)  # 1 = allowed, 0 = blocked
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_ratelimit_user_timestamp', 'user_id', 'timestamp'),
    )


class SecurityEvent(Base):
    """Log security events: injections, anomalies, blocks"""
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(100), index=True, nullable=False)
    
    # Type of event: "prompt_injection", "anomaly", "blocked_topic", etc
    event_type = Column(String(100), nullable=False)
    
    # Details about the event
    details = Column(JSON, default={})
    
    # Severity: "info", "warning", "critical"
    severity = Column(String(20), default="warning")
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_security_event_type_timestamp', 'event_type', 'timestamp'),
        Index('idx_security_user_timestamp', 'user_id', 'timestamp'),
    )


class SystemMetric(Base):
    """System-wide metrics for monitoring"""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Metric name: "llm_call_count", "judge_fail_rate", etc
    metric_name = Column(String(100), nullable=False, index=True)
    
    # Metric value
    value = Column(Float, nullable=False)
    
    # Unit: "count", "ms", "USD", "%", etc
    unit = Column(String(20), default="count")
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_metric_name_timestamp', 'metric_name', 'timestamp'),
    )
