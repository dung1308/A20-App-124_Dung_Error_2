#!/usr/bin/env python
"""
db_init.py
----------
Initialize the backend database. Run this script once to create all tables.

Usage:
    python db_init.py [--recreate]
    
Options:
    --recreate: Drop all existing tables and recreate them (development only)
"""

import sys
import os
import logging
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from database import init_database, recreate_database, get_engine
from config import USE_MOCK, DATABASE_URL


def main():
    """Main initialization function."""
    
    if USE_MOCK:
        logger.warning("USE_MOCK=True — skipping database initialization")
        return
    
    logger.info(f"Database URL: {DATABASE_URL}")
    
    # Check for --recreate flag
    recreate = "--recreate" in sys.argv
    
    if recreate:
        logger.warning("Recreating database (--recreate flag detected)")
        try:
            recreate_database()
            logger.info("✓ Database recreated successfully")
        except Exception as e:
            logger.error(f"✗ Failed to recreate database: {e}")
            sys.exit(1)
    else:
        try:
            init_database()
            logger.info("✓ Database initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize database: {e}")
            sys.exit(1)
    
    # Verify tables were created
    try:
        engine = get_engine()
        if engine:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"✓ Tables created: {', '.join(tables)}")
    except Exception as e:
        logger.error(f"Failed to verify tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
