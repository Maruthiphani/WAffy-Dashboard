"""
Migration script to create the error_logs table in the database
"""
import os
import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import text
from datetime import datetime
from database import engine, Base, SessionLocal

def run_migration():
    """Run the migration to create the error_logs table"""
    try:
        # Create a connection
        with engine.connect() as connection:
            # Check if table exists
            check_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'error_logs';
            """)
            
            result = connection.execute(check_query)
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                # Create the error_logs table
                create_table_query = text("""
                    CREATE TABLE error_logs (
                        error_id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        error_type VARCHAR(100) NOT NULL,
                        error_message TEXT NOT NULL,
                        stack_trace TEXT,
                        source VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    COMMENT ON TABLE error_logs 
                    IS 'Stores error logs from the application';
                    
                    COMMENT ON COLUMN error_logs.error_type 
                    IS 'Type of error (e.g., Database Error, HubSpot Error)';
                    
                    COMMENT ON COLUMN error_logs.source 
                    IS 'Source of the error (e.g., logger_agent)';
                """)
                
                connection.execute(create_table_query)
                connection.commit()
                print("Successfully created error_logs table")
            else:
                print("Table error_logs already exists")
                
    except Exception as e:
        print(f"Error running migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
