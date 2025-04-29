"""
Migration script to add unit field to orders table
"""
import os
import sys
import logging
from sqlalchemy import create_engine, Column, String, MetaData, Table
from dotenv import load_dotenv

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
    """Add unit column to orders table"""
    try:
        # Create engine and connect to database
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        
        # Create metadata object
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Get orders table
        if 'orders' not in metadata.tables:
            logger.error("Orders table not found in database")
            return False
        
        orders = metadata.tables['orders']
        
        # Check if unit column already exists
        if 'unit' in orders.columns:
            logger.info("Unit column already exists in orders table")
            return True
        
        # Add unit column to orders table
        logger.info("Adding unit column to orders table")
        connection.execute('ALTER TABLE orders ADD COLUMN unit VARCHAR(50)')
        
        logger.info("Migration completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False
    finally:
        connection.close()
        engine.dispose()

if __name__ == "__main__":
    logger.info("Starting migration to add unit column to orders table")
    success = run_migration()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        sys.exit(1)
