from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from datetime import datetime
import os
import urllib.parse
from dotenv import load_dotenv
import json
from typing import Optional

# Load environment variables
load_dotenv()

# Database connection
# Use a hardcoded default connection string for local development
DEFAULT_DB_URL = "postgresql://nagajyothiprakash:{}@localhost/waffy_db".format(
    urllib.parse.quote_plus("Login@123")
)
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)

print(f"Connecting to database: {DATABASE_URL}")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model for database
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

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
        from_attributes = True  # Updated from orm_mode=True for Pydantic v2

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

# Clerk webhook verification (basic implementation)
def verify_clerk_webhook(request: Request):
    # In production, implement proper signature verification
    # https://clerk.com/docs/integration/webhooks#securing-your-webhook-endpoint
    return True

# Routes
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
    user = db.query(User).filter(User.clerk_id == clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/webhook/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook endpoint for Clerk events"""
    # Verify webhook (implement proper verification in production)
    if not verify_clerk_webhook(request):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)