import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable not set")

# Ensure the URL uses postgresql:// instead of postgres://
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Create engine
engine = create_engine(db_url)

def migrate_database():
    """Add new columns to user_settings table for WhatsApp Cloud API"""
    try:
        # Connect to the database
        with engine.connect() as connection:
            # Check if columns exist before adding them
            # Add whatsapp_app_id column if it doesn't exist
            connection.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'user_settings' AND column_name = 'whatsapp_app_id'
                    ) THEN
                        ALTER TABLE user_settings ADD COLUMN whatsapp_app_id VARCHAR;
                    END IF;
                END $$;
            """))
            
            # Add whatsapp_app_secret column if it doesn't exist
            connection.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'user_settings' AND column_name = 'whatsapp_app_secret'
                    ) THEN
                        ALTER TABLE user_settings ADD COLUMN whatsapp_app_secret VARCHAR;
                    END IF;
                END $$;
            """))
            
            # Add whatsapp_verify_token column if it doesn't exist
            connection.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'user_settings' AND column_name = 'whatsapp_verify_token'
                    ) THEN
                        ALTER TABLE user_settings ADD COLUMN whatsapp_verify_token VARCHAR;
                    END IF;
                END $$;
            """))
            
            # Commit the transaction
            connection.commit()
            
            logger.info("Database migration completed successfully")
    except Exception as e:
        logger.error(f"Error during database migration: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
