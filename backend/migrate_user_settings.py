"""
Migration script to clean up user_settings table and ensure business_tags field is properly set up
"""
import os
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database import engine, SessionLocal

# Load environment variables
load_dotenv()

# Create a database session
session = SessionLocal()

def cleanup_user_settings_table():
    """
    Clean up the user_settings table by:
    1. Ensuring business_tags field exists and is properly set up
    2. Removing any unnecessary columns
    """
    try:
        # Check if business_tags column already exists
        result = session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_settings' AND column_name='business_tags'"))
        if not result.fetchone():
            print("Adding business_tags column to user_settings table...")
            session.execute(text("ALTER TABLE user_settings ADD COLUMN business_tags TEXT"))
            session.commit()
            print("Successfully added business_tags column")
        else:
            print("business_tags column already exists")
        
        # List of columns to keep in the user_settings table
        columns_to_keep = [
            'id', 'user_id', 
            'first_name', 'last_name',
            'business_name', 'business_description', 
            'contact_phone', 'contact_email',
            'business_address', 'business_website',
            'business_type', 'business_tags', 'founded_year',
            'categories',
            'whatsapp_app_id', 'whatsapp_app_secret',
            'whatsapp_phone_number_id', 'whatsapp_verify_token',
            'crm_type', 'hubspot_access_token', 'other_crm_details',
            'created_at', 'updated_at'
        ]
        
        # Get all columns in the table
        result = session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='user_settings'"))
        all_columns = [row[0] for row in result.fetchall()]
        
        # Find columns to remove (columns in all_columns but not in columns_to_keep)
        columns_to_remove = [col for col in all_columns if col not in columns_to_keep]
        
        if columns_to_remove:
            print(f"Removing unnecessary columns: {', '.join(columns_to_remove)}")
            for column in columns_to_remove:
                session.execute(text(f"ALTER TABLE user_settings DROP COLUMN IF EXISTS {column}"))
            session.commit()
            print("Successfully removed unnecessary columns")
        else:
            print("No unnecessary columns to remove")
        
        print("User settings table cleanup completed successfully")
        
    except Exception as e:
        session.rollback()
        print(f"Error cleaning up user_settings table: {e}")

if __name__ == "__main__":
    cleanup_user_settings_table()
