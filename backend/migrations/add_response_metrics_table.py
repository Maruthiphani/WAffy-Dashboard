"""
Migration script to add response_metrics table to track WAffy's response times
"""
import os
import sys
import logging
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, DateTime, Float, ForeignKey
from sqlalchemy.sql import text
from dotenv import load_dotenv
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.error("DATABASE_URL environment variable not set")
    sys.exit(1)

def run_migration():
    """Create response_metrics table to track WAffy's response times"""
    try:
        # Create engine and connect to database
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        
        # Start a transaction
        trans = connection.begin()
        
        # Create metadata object
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if response_metrics table already exists
        if 'response_metrics' in metadata.tables:
            logger.info("response_metrics table already exists")
            trans.commit()
            return True
        
        # Create response_metrics table
        logger.info("Creating response_metrics table")
        
        # Define the SQL for creating the table
        create_table_sql = text("""
        CREATE TABLE response_metrics (
            metric_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            message_id VARCHAR(100),
            customer_id VARCHAR(20),
            message_type VARCHAR(50),
            response_type VARCHAR(50),
            response_time_seconds FLOAT,
            message_received_at TIMESTAMP,
            response_sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Execute the SQL
        connection.execute(create_table_sql)
        
        # Create index on user_id for faster queries
        logger.info("Creating index on user_id")
        connection.execute(text("CREATE INDEX idx_response_metrics_user_id ON response_metrics(user_id)"))
        
        # Create index on message_received_at for date range queries
        logger.info("Creating index on message_received_at")
        connection.execute(text("CREATE INDEX idx_response_metrics_received_at ON response_metrics(message_received_at)"))
        
        # Commit the transaction
        trans.commit()
        logger.info("Migration completed successfully")
        return True
    
    except Exception as e:
        # Rollback the transaction in case of error
        if trans and trans.is_active:
            trans.rollback()
        logger.error(f"Error during migration: {e}")
        return False
    finally:
        if connection:
            connection.close()
        if engine:
            engine.dispose()

if __name__ == "__main__":
    logger.info("Starting migration to create response_metrics table")
    success = run_migration()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        sys.exit(1)
