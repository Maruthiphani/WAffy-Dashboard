"""
Database setup script for WAffy Dashboard
"""
import logging
from database import engine, Base

# Configure logging
logger = logging.getLogger(__name__)


def setup_database():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

if __name__ == "__main__":
    setup_database()
