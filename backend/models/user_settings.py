"""
Database models for user settings
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserSettings(Base):
    """User settings model for storing configuration data"""
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
    categories = Column(JSON, nullable=True, default=list)
    
    # WhatsApp Cloud API settings (encrypted)
    whatsapp_api_key = Column(String, nullable=True)
    whatsapp_phone_number_id = Column(String, nullable=True)
    whatsapp_business_account_id = Column(String, nullable=True)
    
    # CRM Integration settings
    crm_type = Column(String, nullable=True)
    hubspot_api_key = Column(String, nullable=True)
    other_crm_details = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationship with User model
    user = relationship("User", back_populates="settings")
