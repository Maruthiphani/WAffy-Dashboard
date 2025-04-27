"""
Check the database schema to verify if the user_id column was added to the tables.
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from app.models import Base, User, Customer, Interaction, Order, Issue, Feedback, Enquiry

# Load environment variables
load_dotenv()

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    sys.exit(1)

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def check_table_schema(table_name):
    """Check if a table exists and print its columns."""
    inspector = inspect(engine)
    
    if table_name in inspector.get_table_names():
        print(f"Table '{table_name}' exists.")
        columns = inspector.get_columns(table_name)
        print(f"Columns in '{table_name}':")
        for column in columns:
            print(f"  - {column['name']} ({column['type']})")
        
        # Check if user_id column exists
        user_id_exists = any(column['name'] == 'user_id' for column in columns)
        if user_id_exists:
            print(f"  ✅ user_id column exists in '{table_name}'")
        else:
            print(f"  ❌ user_id column does NOT exist in '{table_name}'")
    else:
        print(f"Table '{table_name}' does not exist.")

def check_db_schema():
    """Check the database schema for all tables."""
    try:
        print("Checking database schema...")
        print(f"Connected to: {DATABASE_URL}")
        
        # Get all table names
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        # Check each table
        check_table_schema("users")
        check_table_schema("user_settings")
        check_table_schema("customers")
        check_table_schema("interaction_logs")
        check_table_schema("orders")
        check_table_schema("issues")
        check_table_schema("feedback")
        check_table_schema("enquiries")
        
        # Try to query customers table to see if user_id column exists
        try:
            result = db.execute(text("SELECT customer_id, user_id FROM customers LIMIT 5")).fetchall()
            print("\nSample data from customers table:")
            for row in result:
                print(f"  Customer ID: {row[0]}, User ID: {row[1]}")
        except Exception as e:
            print(f"\nError querying customers table: {e}")
        
    except Exception as e:
        print(f"Error checking database schema: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_db_schema()
