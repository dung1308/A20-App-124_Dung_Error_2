"""
Database connection and session management
"""

import logging
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool
from config import get_database_url, ENVIRONMENT
from models import Base

logger = logging.getLogger(__name__)

# Create engine based on environment
db_url = get_database_url()

if "sqlite" in db_url:
    # SQLite for testing
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL for production
    engine = create_engine(
        db_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        echo=ENVIRONMENT == "development",
    )


# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db() -> Session:
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite"""
    if "sqlite" in db_url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def health_check():
    """Check database connection health"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.close()
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
