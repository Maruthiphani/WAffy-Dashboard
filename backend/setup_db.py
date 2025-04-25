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
# Use a hardcoded default connection string for local development
DEFAULT_DB_URL = "postgresql://avnadmin:{}@pg-waffy-waffy.g.aivencloud.com:26140/waffy_db?sslmode=require".format(
    urllib.parse.quote_plus("AVNS_8qhqmlqzPGBFt4YTjQA")
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

# If the URL starts with 'postgres://', replace it with 'postgresql://' for SQLAlchemy compatibility
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database: {DATABASE_URL}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model for database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with UserSettings
    settings = relationship("UserSettings", back_populates="user", uselist=False)

# User Settings model for database
class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic user info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Business info
    business_name = Column(String, nullable=True)
    business_description = Column(Text, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    business_address = Column(String, nullable=True)
    business_website = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    founded_year = Column(String, nullable=True)
    
    # Categories for message classification
    categories = Column(String, nullable=True)  # Stored as JSON string
    
    # WhatsApp Cloud API settings (encrypted)
    whatsapp_api_key = Column(String, nullable=True)
    whatsapp_phone_number_id = Column(String, nullable=True)
    whatsapp_business_account_id = Column(String, nullable=True)
    
    # CRM Integration settings
    crm_type = Column(String, nullable=True)
    hubspot_api_key = Column(String, nullable=True)
    other_crm_details = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User model
    user = relationship("User", back_populates="settings")

def setup_database():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")

if __name__ == "__main__":
    setup_database()
