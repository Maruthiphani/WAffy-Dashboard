"""
Pydantic models for user settings API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserSettingsBase(BaseModel):
    """Base model for user settings"""
    # Basic user info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Business info
    business_name: Optional[str] = None
    business_description: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    business_address: Optional[str] = None
    business_website: Optional[str] = None
    business_type: Optional[str] = None
    founded_year: Optional[str] = None
    
    # Categories for message classification
    categories: Optional[List[str]] = []
    
    # WhatsApp Cloud API settings
    whatsapp_api_key: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_business_account_id: Optional[str] = None
    
    # CRM Integration settings
    crm_type: Optional[str] = "hubspot"
    hubspot_api_key: Optional[str] = None
    other_crm_details: Optional[str] = None
    
    # Dashboard settings
    view_consolidated_data: Optional[bool] = False

    class Config:
        orm_mode = True  # For older Pydantic versions

class UserSettingsCreate(UserSettingsBase):
    """Model for creating user settings"""
    pass

class UserSettingsUpdate(UserSettingsBase):
    """Model for updating user settings"""
    pass

class UserSettingsResponse(UserSettingsBase):
    """Model for user settings response"""
    id: int
    user_id: int
    created_at: str
    updated_at: str
    
    # Exclude sensitive fields from response
    class Config:
        orm_mode = True  # For older Pydantic versions
        exclude = {"whatsapp_api_key", "hubspot_api_key"}
