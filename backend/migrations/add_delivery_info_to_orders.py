"""
Migration script to add delivery address, time, and method fields to orders table
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, MetaData
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
    """Add delivery address, time, and method columns to orders table"""
    connection = None
    try:
        # Create engine and connect to database
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        
        # Start a transaction
        trans = connection.begin()
        
        # Create metadata object
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Get orders table
        if 'orders' not in metadata.tables:
            logger.error("Orders table not found in database")
            return False
        
        orders = metadata.tables['orders']
        
        # Check if columns already exist
        columns_to_add = []
        if 'delivery_address' not in orders.columns:
            columns_to_add.append('delivery_address VARCHAR(255)')
        else:
            logger.info("delivery_address column already exists in orders table")
            
        if 'delivery_time' not in orders.columns:
            columns_to_add.append('delivery_time VARCHAR(100)')
        else:
            logger.info("delivery_time column already exists in orders table")
            
        if 'delivery_method' not in orders.columns:
            columns_to_add.append('delivery_method VARCHAR(50)')
        else:
            logger.info("delivery_method column already exists in orders table")
        
        # Add columns to orders table
        if columns_to_add:
            for column_def in columns_to_add:
                column_name = column_def.split()[0]
                logger.info(f"Adding {column_name} column to orders table")
                sql = text(f'ALTER TABLE orders ADD COLUMN {column_def}')
                connection.execute(sql)
            
            # Commit the transaction
            trans.commit()
            logger.info("Migration completed successfully")
            return True
        else:
            # No changes needed, still commit the transaction
            trans.commit()
            logger.info("No columns to add, all already exist")
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
    logger.info("Starting migration to add delivery information columns to orders table")
    success = run_migration()
    if success:
        logger.info("Migration completed successfully")
    else:
        logger.error("Migration failed")
        sys.exit(1)
