"""
WAffy Dashboard Backend API
"""
import os
import urllib.parse
import json
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import User, UserSettings, Order
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

# Get encryption key from environment or use a default for development
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "waffy_encryption_key_for_development_only")
# Ensure the key is properly formatted for Fernet (must be 32 url-safe base64-encoded bytes)
if len(ENCRYPTION_KEY) < 32:
    ENCRYPTION_KEY = ENCRYPTION_KEY.ljust(32)[:32]
fernet = Fernet(Fernet.generate_key())  # For encryption/decryption

DATABASE_URL = os.getenv("DATABASE_URL")

# If the URL starts with 'postgres://', replace it with 'postgresql://' for SQLAlchemy compatibility
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

print(f"Connecting to database: {DATABASE_URL}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Encryption/Decryption functions
def encrypt_value(value):
    """Encrypt a sensitive value"""
    if not value:
        return None
    return fernet.encrypt(value.encode()).decode()

def decrypt_value(encrypted_value):
    """Decrypt an encrypted value"""
    if not encrypted_value:
        return None
    return fernet.decrypt(encrypted_value.encode()).decode()

# Pydantic models for request/response
class UserCreate(BaseModel):
    clerk_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    clerk_id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

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
    whatsapp_app_id: Optional[str] = None
    whatsapp_app_secret: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    whatsapp_business_account_id: Optional[str] = None
    
    # CRM Integration settings
    crm_type: Optional[str] = "hubspot"
    hubspot_access_token: Optional[str] = None
    other_crm_details: Optional[str] = None

    class Config:
        orm_mode = True

class UserSettingsResponse(UserSettingsBase):
    """Model for user settings response"""
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FastAPI app
app = FastAPI(title="WAffy API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to get user by clerk_id
def get_user_by_clerk_id(db: Session, clerk_id: str):
    return db.query(User).filter(User.clerk_id == clerk_id).first()

# Routes
@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"status": "ok", "message": "WAffy API is running"}

@app.post("/api/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user in the database after Clerk signup"""
    db_user = User(
        clerk_id=user_data.clerk_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.clerk_id == user_data.clerk_id).first()
    if existing_user:
        return existing_user
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/api/users/{clerk_id}", response_model=UserResponse)
async def get_user(clerk_id: str, db: Session = Depends(get_db)):
    """Get user by Clerk ID"""
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{clerk_id}/settings")
async def update_user_settings(clerk_id: str, settings_data: dict, db: Session = Depends(get_db)):
    """Update user settings with encryption for sensitive data"""
    # Get user by clerk_id
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user already has settings
    if not user.settings:
        # Create new settings
        user_settings = UserSettings(user_id=user.id)
        db.add(user_settings)
    else:
        user_settings = user.settings
    
    # Update settings with encrypted sensitive data
    for key, value in settings_data.items():
        if key in ["whatsapp_api_key", "whatsapp_app_secret", "hubspot_access_token"] and value:
            # Encrypt sensitive values
            setattr(user_settings, key, encrypt_value(value))
        elif key == "categories" and isinstance(value, list):
            # Store categories as JSON string
            setattr(user_settings, key, json.dumps(value))
        else:
            # Store other values as is
            setattr(user_settings, key, value)
    
    db.commit()
    db.refresh(user_settings)
    
    # Prepare response (exclude sensitive data)
    response_data = {k: v for k, v in settings_data.items() if k not in ["whatsapp_api_key", "whatsapp_app_secret", "hubspot_access_token"]}
    response_data["id"] = user_settings.id
    response_data["user_id"] = user.id
    
    return response_data

@app.get("/api/users/{clerk_id}/settings")
async def get_user_settings(clerk_id: str, db: Session = Depends(get_db)):
    """Get user settings with decryption for sensitive data"""
    # Get user by clerk_id
    user = get_user_by_clerk_id(db, clerk_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user has settings
    if not user.settings:
        return {"message": "No settings found for this user"}
    
    # Prepare response
    settings = user.settings
    response_data = {
        "id": settings.id,
        "user_id": user.id,
        "first_name": settings.first_name,
        "last_name": settings.last_name,
        "business_name": settings.business_name,
        "business_description": settings.business_description,
        "contact_phone": settings.contact_phone,
        "contact_email": settings.contact_email,
        "business_address": settings.business_address,
        "business_website": settings.business_website,
        "business_type": settings.business_type,
        "founded_year": settings.founded_year,
        "categories": json.loads(settings.categories) if settings.categories else [],
        "whatsapp_phone_number_id": settings.whatsapp_phone_number_id,
        "whatsapp_business_account_id": settings.whatsapp_business_account_id,
        "whatsapp_app_id": settings.whatsapp_app_id,
        "whatsapp_verify_token": settings.whatsapp_verify_token,
        "crm_type": settings.crm_type,
        "other_crm_details": settings.other_crm_details,
    }
    
    # Include decrypted API keys if they exist
    if settings.whatsapp_api_key:
        response_data["whatsapp_api_key"] = decrypt_value(settings.whatsapp_api_key)
    
    if settings.whatsapp_app_secret:
        response_data["whatsapp_app_secret"] = decrypt_value(settings.whatsapp_app_secret)
    
    if settings.hubspot_access_token:
        response_data["hubspot_access_token"] = decrypt_value(settings.hubspot_access_token)
    
    return response_data

@app.post("/api/webhook/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook endpoint for Clerk events"""
    # Parse webhook payload
    payload = await request.json()
    event_type = payload.get("type")
    
    # Handle user.created event
    if event_type == "user.created":
        data = payload.get("data", {})
        user_data = UserCreate(
            clerk_id=data.get("id"),
            email=data.get("email_addresses", [{}])[0].get("email_address", ""),
            first_name=data.get("first_name"),
            last_name=data.get("last_name")
        )
        
        # Create user in database
        db_user = User(
            clerk_id=user_data.clerk_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.clerk_id == user_data.clerk_id).first()
        if existing_user:
            return {"status": "success", "message": "User already exists"}
        
        db.add(db_user)
        db.commit()
        
        return {"status": "success", "message": "User created"}
    
    return {"status": "success", "message": f"Event {event_type} received"}

@app.get("/api/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    """Verify webhook endpoint for WhatsApp Cloud API"""
    # Get query parameters
    params = dict(request.query_params)
    
    # Check if this is a verification request
    if "hub.mode" in params and "hub.verify_token" in params:
        mode = params["hub.mode"]
        token = params["hub.verify_token"]
        challenge = params["hub.challenge"] if "hub.challenge" in params else None
        
        # Find a user with this verify token
        users = db.query(User).join(UserSettings).filter(UserSettings.whatsapp_verify_token == token).all()
        
        if mode == "subscribe" and users and challenge:
            # Return the challenge to confirm the webhook
            return int(challenge)
    
    # If verification fails or this is not a verification request
    raise HTTPException(status_code=403, detail="Verification failed")

class OrderResponse(BaseModel):
    """Order response model"""
    order_id: int
    customer_id: str
    order_number: str
    item: str
    quantity: int
    notes: Optional[str] = None
    order_status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

@app.get("/api/orders", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db)):
    """Fetch all orders"""
    orders = db.query(Order).all()
    return orders

@app.get("/api/orders/{customer_id}", response_model=List[OrderResponse])
async def get_orders_by_customer(customer_id: str, db: Session = Depends(get_db)):
    """Fetch orders for a specific customer"""
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return orders


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)