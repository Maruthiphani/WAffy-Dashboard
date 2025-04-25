"""
Database setup script for WAffy Dashboard
"""
import os
import urllib.parse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")

# If the URL starts with 'postgres://', replace it with 'postgresql://' for SQLAlchemy compatibility
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database: {DATABASE_URL}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def setup_database():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    setup_database()
