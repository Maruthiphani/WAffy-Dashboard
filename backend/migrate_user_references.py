"""
Migration script to add user_id foreign key to all tables except businesses, business_tags, and categories.
This script will:
1. Add user_id column to the necessary tables
2. Set a default user_id for existing records
3. Add foreign key constraints
"""
import os
import sys
from sqlalchemy import create_engine, text
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

def migrate_user_references():
    """Migrate the database to add user_id references to all necessary tables."""
    try:
        print("Starting migration to add user_id references...")
        
        # Get the first user as default (or create one if none exists)
        default_user = db.query(User).first()
        if not default_user:
            print("No users found. Creating a default user...")
            default_user = User(
                clerk_id="default_migration_user",
                email="default@waffy.com",
                first_name="Default",
                last_name="User"
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
        
        default_user_id = default_user.id
        print(f"Using default user ID: {default_user_id}")
        
        # Add user_id column to Customer table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS user_id INTEGER"))
            db.execute(text(f"UPDATE customers SET user_id = {default_user_id} WHERE user_id IS NULL"))
            db.execute(text("ALTER TABLE customers ALTER COLUMN user_id SET NOT NULL"))
            db.execute(text("ALTER TABLE customers ADD CONSTRAINT fk_customer_user FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Updated Customer table")
        except Exception as e:
            print(f"Error updating Customer table: {e}")
        
        # Add user_id column to Interaction table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE interaction_logs ADD COLUMN IF NOT EXISTS user_id INTEGER"))
            db.execute(text(f"UPDATE interaction_logs SET user_id = {default_user_id} WHERE user_id IS NULL"))
            db.execute(text("ALTER TABLE interaction_logs ALTER COLUMN user_id SET NOT NULL"))
            db.execute(text("ALTER TABLE interaction_logs ADD CONSTRAINT fk_interaction_user FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Updated Interaction table")
        except Exception as e:
            print(f"Error updating Interaction table: {e}")
        
        # Add user_id column to Order table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS user_id INTEGER"))
            db.execute(text(f"UPDATE orders SET user_id = {default_user_id} WHERE user_id IS NULL"))
            db.execute(text("ALTER TABLE orders ALTER COLUMN user_id SET NOT NULL"))
            db.execute(text("ALTER TABLE orders ADD CONSTRAINT fk_order_user FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Updated Order table")
        except Exception as e:
            print(f"Error updating Order table: {e}")
        
        # Add user_id column to Issue table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE issues ADD COLUMN IF NOT EXISTS user_id INTEGER"))
            db.execute(text(f"UPDATE issues SET user_id = {default_user_id} WHERE user_id IS NULL"))
            db.execute(text("ALTER TABLE issues ALTER COLUMN user_id SET NOT NULL"))
            db.execute(text("ALTER TABLE issues ADD CONSTRAINT fk_issue_user FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Updated Issue table")
        except Exception as e:
            print(f"Error updating Issue table: {e}")
        
        # Add user_id column to Feedback table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE feedback ADD COLUMN IF NOT EXISTS user_id INTEGER"))
            db.execute(text(f"UPDATE feedback SET user_id = {default_user_id} WHERE user_id IS NULL"))
            db.execute(text("ALTER TABLE feedback ALTER COLUMN user_id SET NOT NULL"))
            db.execute(text("ALTER TABLE feedback ADD CONSTRAINT fk_feedback_user FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Updated Feedback table")
        except Exception as e:
            print(f"Error updating Feedback table: {e}")
        
        # Add user_id column to Enquiry table if it doesn't exist
        try:
            db.execute(text("ALTER TABLE enquiries ADD COLUMN IF NOT EXISTS user_id INTEGER"))
            db.execute(text(f"UPDATE enquiries SET user_id = {default_user_id} WHERE user_id IS NULL"))
            db.execute(text("ALTER TABLE enquiries ALTER COLUMN user_id SET NOT NULL"))
            db.execute(text("ALTER TABLE enquiries ADD CONSTRAINT fk_enquiry_user FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Updated Enquiry table")
        except Exception as e:
            print(f"Error updating Enquiry table: {e}")
        
        db.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Migration failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_user_references()
