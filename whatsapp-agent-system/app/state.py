from pydantic import BaseModel
from typing import Optional, Dict, List

class MessageState(BaseModel):
    timestamp: Optional[str]
    raw_timestamp_utc: Optional[int]
    message_id: Optional[str]
    message_type: Optional[str] = "text"

    customer_id: Optional[str] = None
    sender: str
    customer_name: Optional[str]
    message: str

    predicted_category: Optional[str] = None
    priority: Optional[str] = None
    extracted_info: Optional[Dict] = {}
    context: Optional[List[str]] = []
    conversation_status: Optional[str] = "continue"

    business_phone_number: Optional[str] = None
    business_phone_id: Optional[str] = None
