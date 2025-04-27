from sqlalchemy import Column, Integer, String, Numeric, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Order(Base):
    """Order model for storing order details"""
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(20), nullable=False)
    order_number = Column(String(50), nullable=False)
    item = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    notes = Column(String(200), nullable=True)
    order_status = Column(String(20), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
