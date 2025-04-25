from typing import Optional, Dict, List
from pydantic import BaseModel

class MessageState(BaseModel):
    timestamp: Optional[str] = None
    raw_timestamp_utc: Optional[int] = None
    message_id: Optional[str] = None
    message_type: Optional[str] = "text"

    customer_id: str
    sender: str
    customer_name: Optional[str] = None
    message: str

    predicted_category: Optional[str] = None
    priority: Optional[str] = None
    extracted_info: Optional[dict] = {}
    conversation_status: Optional[str] = "continue"
    context: Optional[List[str]] = []

    business_phone_number: Optional[str] = None
    business_phone_id: Optional[str] = None
