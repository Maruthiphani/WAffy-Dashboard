from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    """Customer model for storing customer details"""
    __tablename__ = "customer"

    customer_id = Column(String(20), primary_key=True, index=True)
    customer_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, nullable=True)  # assuming this links to User table
