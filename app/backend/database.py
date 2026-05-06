"""
database.py
-----------
Responsibility: Database connection and session management.
Provides database engine, session factory, and initialization utilities.
"""

import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from config import DATABASE_URL, USE_MOCK
from models.schemas import Base

logger = logging.getLogger(__name__)

# Global engine and session factory
engine = None
SessionLocal = None


def init_database() -> None:
    """
    Initialize the database engine and create all tables.
    Called once at application startup.
    """
    global engine, SessionLocal
    
    if USE_MOCK:
        logger.info("Database initialization skipped (USE_MOCK=True)")
        return
    
    try:
        # For SQLite in development, use StaticPool to avoid threading issues
        if DATABASE_URL.startswith("sqlite"):
            engine = create_engine(
                DATABASE_URL,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            # For PostgreSQL or other databases
            engine = create_engine(DATABASE_URL, echo=False)
        
        # Create all tables defined in Base metadata
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        logger.info(f"Database initialized successfully: {DATABASE_URL}")
        
        # Log existing tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Tables in database: {tables}")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db_session() -> Session:
    """
    Dependency injection function for FastAPI.
    Yields a SQLAlchemy session for request handling.
    
    Usage in FastAPI:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db_session)):
            ...
    """
    if USE_MOCK or SessionLocal is None:
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    """Returns the SQLAlchemy engine."""
    return engine


def drop_all_tables() -> None:
    """
    Drop all tables from the database.
    WARNING: Use only for testing/development!
    """
    if USE_MOCK or engine is None:
        logger.warning("Cannot drop tables in mock mode or without engine")
        return
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise


def recreate_database() -> None:
    """
    Drop all tables and recreate them.
    Useful for resetting the database during development.
    """
    if USE_MOCK:
        logger.warning("Cannot recreate database in mock mode")
        return
    
    try:
        drop_all_tables()
        Base.metadata.create_all(bind=engine)
        logger.info("Database recreated successfully")
    except Exception as e:
        logger.error(f"Failed to recreate database: {e}")
        raise
