"""
Database setup script for WAffy Dashboard
"""
from database import engine, Base


def setup_database():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    setup_database()
