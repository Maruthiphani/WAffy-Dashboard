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

def migrate_hubspot_token():
    """Change hubspot_api_key to hubspot_access_token in user_settings table"""
    try:
        # Connect to the database
        with engine.connect() as connection:
            # Check if hubspot_access_token column exists, if not create it
            connection.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'user_settings' AND column_name = 'hubspot_access_token'
                    ) THEN
                        ALTER TABLE user_settings ADD COLUMN hubspot_access_token VARCHAR;
                    END IF;
                END $$;
            """))
            
            # Copy data from hubspot_api_key to hubspot_access_token if it exists
            connection.execute(text("""
                UPDATE user_settings 
                SET hubspot_access_token = hubspot_api_key 
                WHERE hubspot_api_key IS NOT NULL;
            """))
            
            # Commit the transaction
            connection.commit()
            
            logger.info("HubSpot token migration completed successfully")
    except Exception as e:
        logger.error(f"Error during HubSpot token migration: {e}")
        raise

if __name__ == "__main__":
    migrate_hubspot_token()
