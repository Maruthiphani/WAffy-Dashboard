from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Enquiry(Base):
    """Enquiry model for storing customer enquiries"""
    __tablename__ = "enquiries"

    enquiry_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), nullable=False)
    description = Column(String(200), nullable=True)
    category = Column(String(20), nullable=True)
    priority = Column(String(10), nullable=True)
    status = Column(String(20), nullable=True)
    follow_up_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
   
