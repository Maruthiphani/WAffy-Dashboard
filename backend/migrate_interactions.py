"""
Migration script to create the integration_logs table in the database
"""
import os
import sys
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import text
from datetime import datetime
from database import engine, Base, SessionLocal

def run_migration():
    """Run the migration to create the integration_logs table"""
    try:
        # Create a connection
        with engine.connect() as connection:
            # Check if table exists
            check_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'integration_logs';
            """)
            
            result = connection.execute(check_query)
            table_exists = result.fetchone() is not None
            
            if not table_exists:
                # Create the integration_logs table
                create_table_query = text("""
                    CREATE TABLE integration_logs (
                        interaction_id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id),
                        whatsapp_message_id VARCHAR(100),
                        customer_id VARCHAR(20) REFERENCES customers(customer_id),
                        timestamp TIMESTAMP,
                        message_type VARCHAR(20),
                        category VARCHAR(20),
                        priority VARCHAR(10),
                        status VARCHAR(20),
                        sentiment VARCHAR(10),
                        message_summary VARCHAR(200),
                        response_time INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    COMMENT ON TABLE integration_logs 
                    IS 'Stores WhatsApp message interactions';
                    
                    COMMENT ON COLUMN integration_logs.message_type 
                    IS 'Type of message (e.g., text, image, audio)';
                    
                    COMMENT ON COLUMN integration_logs.category 
                    IS 'Category of message (e.g., greeting, order, inquiry)';
                    
                    COMMENT ON COLUMN integration_logs.priority 
                    IS 'Priority level (e.g., low, medium, high)';
                """)
                
                connection.execute(create_table_query)
                connection.commit()
                print("Successfully created integration_logs table")
            else:
                print("Table integration_logs already exists")
                
    except Exception as e:
        print(f"Error running migration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
