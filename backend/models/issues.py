from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Issue(Base):
    """Issue model for storing customer issues"""
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), nullable=False)
    order_id = Column(Integer, nullable=True)
    issue_type = Column(String(20), nullable=True)
    description = Column(String(200), nullable=True)
    status = Column(String(20), nullable=True)
    priority = Column(String(10), nullable=True)
    resolution_notes = Column(String(200), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
