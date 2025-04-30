from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class ErrorLog(Base):
    __tablename__ = "error_logs"

    error_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    error_type = Column(String, index=True)
    error_message = Column(Text)
    stack_trace = Column(Text, nullable=True)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
