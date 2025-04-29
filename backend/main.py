"""
WAffy Dashboard Backend API
"""
import os
import urllib.parse
import json
import logging
from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from app.agents.update_webhook import run_auto_update_webhook
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from database import get_db
from app.models import User, UserSettings, Order, Customer, Enquiry, Issue, ResponseMetrics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import graph builder and listener agent here, but don't create app instance yet
from app.graph_builder import build_graph
from app.agents.listener_agent import get_listener_router

# Build the graph for message processing
graph = build_graph()

# Get encryption key from environment or use a default for development
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "waffy_encryption_key_for_development_only")

# Properly format the key for Fernet (must be 32 url-safe base64-encoded bytes)
import base64
from cryptography.hazmat.primitives import hashes

# Generate a consistent key using SHA-256 hash (which produces 32 bytes)
digest = hashes.Hash(hashes.SHA256())
digest.update(ENCRYPTION_KEY.encode())
key_bytes = digest.finalize()

# Convert to URL-safe base64-encoded format as required by Fernet
fernet_key = base64.urlsafe_b64encode(key_bytes)
fernet = Fernet(fernet_key)  # Use consistent key for encryption/decryption


# Encryption/Decryption functions
def encrypt_value(value):
    """Encrypt a sensitive value"""
    if not value:
        return None
    try:
        return fernet.encrypt(value.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return None

def decrypt_value(encrypted_value):
    """Decrypt an encrypted value"""
    if not encrypted_value:
        return None
    try:
        return fernet.decrypt(encrypted_value.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return None

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
    business_tags: Optional[List[int]] = []
    founded_year: Optional[str] = None
    
    # Categories for message classification
    categories: Optional[List[str]] = []
    
    # WhatsApp Cloud API settings
    whatsapp_app_id: Optional[str] = None
    whatsapp_app_secret: Optional[str] = None
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_verify_token: Optional[str] = None
    whatsapp_api_key: Optional[str] = None
    
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

# Helper function to get user by clerk_id
def get_user_by_clerk_id(db: Session, clerk_id: str):
    return db.query(User).filter(User.clerk_id == clerk_id).first()

# Initialize FastAPI app
app = FastAPI(title="WAffy API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include business routes
from routes.business_routes import router as business_router
app.include_router(business_router)

# Include the listener agent router with the graph
# This adds the webhook endpoints to the main application
app.include_router(get_listener_router(graph))

# Log available routes for debugging
for route in app.routes:
    logger.info(f"Route: {route.path}, Methods: {route.methods}")

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
    print("inside")
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
async def update_user_settings(clerk_id: str, settings_data: dict, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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
    
    # Track if WhatsApp API credentials are being updated
    whatsapp_credentials_updated = False
    phone_number_id_updated = False
    app_id = None
    app_secret = None
    phone_number_id = None
    verify_token = None
    
    # Update settings with encrypted sensitive data
    for key, value in settings_data.items():
        try:
            if key in ["whatsapp_app_id", "whatsapp_app_secret", "whatsapp_verify_token", "whatsapp_api_key"] and value:
                # Encrypt sensitive values
                encrypted_value = encrypt_value(value)
                setattr(user_settings, key, encrypted_value)
                logger.info(f"Successfully encrypted {key}")
                whatsapp_credentials_updated = True
                
                # Track WhatsApp app credentials for webhook update
                if key == "whatsapp_app_id":
                    app_id = value
                    whatsapp_credentials_updated = True
                elif key == "whatsapp_app_secret":
                    app_secret = value
                    whatsapp_credentials_updated = True
                elif key == "whatsapp_verify_token":
                    verify_token = value
                    whatsapp_credentials_updated = True
                elif key == "whatsapp_phone_number_id":
                    phone_number_id = value
                    phone_number_id_updated = True
            elif key == "hubspot_access_token" and value:
                # Encrypt sensitive values
                encrypted_value = encrypt_value(value)
                setattr(user_settings, key, encrypted_value)
                logger.info(f"Successfully encrypted {key}")
            elif key in ["categories", "business_tags"] and isinstance(value, list):
                # Store categories and business_tags as JSON string
                setattr(user_settings, key, json.dumps(value))
            else:
                # Store other values as is
                setattr(user_settings, key, value)
        except Exception as e:
            logger.error(f"Error processing field {key}: {e}")
            # Continue with other fields even if one fails
    
    db.commit()
    db.refresh(user_settings)
    
    # Check if we should update the webhook
    if whatsapp_credentials_updated and phone_number_id_updated and phone_number_id:
        logger.info(f"WhatsApp credentials updated, triggering webhook update for phone number ID: {phone_number_id}")
        # Run webhook update in the background
        try:
            # Decrypt the verify token if it was encrypted
            decrypted_verify_token = None
            if verify_token:
                try:
                    decrypted_verify_token = decrypt_value(verify_token)
                    logger.info("Successfully decrypted verify token for webhook update")
                except Exception as decrypt_error:
                    logger.error(f"Error decrypting verify token: {decrypt_error}")
                    # Fall back to encrypted token if decryption fails
                    decrypted_verify_token = verify_token
            
            background_tasks.add_task(run_auto_update_webhook, phone_number_id, app_id, app_secret, decrypted_verify_token)
            logger.info("Webhook update task added to background")
        except Exception as e:
            logger.error(f"Error scheduling webhook update: {e}")
    
    # Prepare response (exclude sensitive data)
    response_data = {k: v for k, v in settings_data.items() if k not in ["whatsapp_app_id", "whatsapp_app_secret", "whatsapp_verify_token", "whatsapp_api_key", "hubspot_access_token"]}
    response_data["id"] = user_settings.id
    response_data["user_id"] = user.id
    
    # Add webhook update status to response if applicable
    if whatsapp_credentials_updated and phone_number_id_updated and phone_number_id:
        response_data["webhook_update"] = "Webhook update scheduled in background"
    
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
        "business_tags": json.loads(settings.business_tags) if settings.business_tags else [],
        "founded_year": settings.founded_year,
        "categories": json.loads(settings.categories) if settings.categories else [],
        "whatsapp_phone_number_id": settings.whatsapp_phone_number_id,
        "crm_type": settings.crm_type,
        "other_crm_details": settings.other_crm_details,
        "view_consolidated_data": settings.view_consolidated_data
    }
    
    # Log the encryption key hash for debugging
    key_hash = hash(fernet_key)
    logger.info(f"Using encryption key hash: {key_hash}")
    
    # Include decrypted API keys if they exist, with improved error handling
    sensitive_fields = [
        "whatsapp_app_id", 
        "whatsapp_app_secret", 
        "whatsapp_api_key",
        "hubspot_access_token"
    ]
    
    for field in sensitive_fields:
        field_value = getattr(settings, field, None)
        if field_value:
            logger.info(f"Attempting to decrypt {field}")
            try:
                decrypted_value = decrypt_value(field_value)
                if decrypted_value:
                    response_data[field] = decrypted_value
                    logger.info(f"Successfully decrypted {field}")
                else:
                    logger.error(f"Decryption returned None for {field}")
                    response_data[field] = ""
            except Exception as e:
                logger.error(f"Error decrypting {field}: {str(e)}")
                response_data[field] = ""
        else:
            response_data[field] = ""
    
    return response_data

@app.get("/api/test-encryption")
async def test_encryption():
    """Test endpoint to verify encryption/decryption functionality"""
    test_value = "test-value-123"
    try:
        # Test encryption
        encrypted = encrypt_value(test_value)
        if not encrypted:
            return {"status": "error", "message": "Encryption failed"}
        
        # Test decryption
        decrypted = decrypt_value(encrypted)
        if not decrypted:
            return {"status": "error", "message": "Decryption failed"}
        
        # Verify the decrypted value matches the original
        if decrypted != test_value:
            return {
                "status": "error", 
                "message": f"Value mismatch: expected '{test_value}', got '{decrypted}'"
            }
        
        # Log the encryption key hash for debugging
        key_hash = hash(fernet_key)
        
        return {
            "status": "success", 
            "message": "Encryption and decryption working correctly",
            "original": test_value,
            "encrypted": encrypted,
            "decrypted": decrypted,
            "key_hash": key_hash
        }
    except Exception as e:
        logger.error(f"Error in test-encryption endpoint: {str(e)}")
        return {"status": "error", "message": f"Exception: {str(e)}"}

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
    customer_name: Optional[str] = None
    order_number: str
    item: str
    quantity: int
    unit: Optional[str] = None
    notes: Optional[str] = None
    order_status: str
    total_amount: float
    delivery_address: Optional[str] = None
    delivery_time: Optional[str] = None
    delivery_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

##@app.get("/api/orders", response_model=List[OrderResponse])
##async def get_orders(db: Session = Depends(get_db)):
  ##  """Fetch all orders"""
    ##orders = db.query(Order).all()
    ##return orders

@app.get("/api/orders", response_model=List[dict])
async def get_orders(clerk_id: str = None, db: Session = Depends(get_db)):
    # Get user by clerk_id if provided
    user = None
    if clerk_id:
        user = get_user_by_clerk_id(db, clerk_id)
    
    # Filter by user_id if clerk_id was provided and user was found
    if user:
        # Order by created_at in descending order to get latest first
        orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.created_at.desc()).all()
    else:
        # If no clerk_id or user not found, return all orders (for backward compatibility)
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
    
    enriched_orders = []
    for order in orders:
        enriched_orders.append({
            "customer_id": order.customer_id,
            "CustomerName": order.customer.customer_name if order.customer else None,
            "OrderNumber": order.order_number,
            "Item": order.item,
            "Quantity": order.quantity,
            "Unit": order.unit if hasattr(order, 'unit') and order.unit else "",  # Include unit field
            "Notes": order.notes,
            "Status": order.order_status,
            "Amount": float(order.total_amount) if order.total_amount else 0.0,
            "DeliveryDate": order.created_at.isoformat() if order.created_at else None,
            # Include delivery information
            "DeliveryAddress": order.delivery_address if hasattr(order, 'delivery_address') and order.delivery_address else None,
            "DeliveryTime": order.delivery_time if hasattr(order, 'delivery_time') and order.delivery_time else None,
            "DeliveryMethod": order.delivery_method if hasattr(order, 'delivery_method') and order.delivery_method else None,
        })
    
    return enriched_orders



@app.get("/api/orders/{customer_id}", response_model=List[OrderResponse])
async def get_orders_by_customer(customer_id: str, db: Session = Depends(get_db)):
    """Fetch orders for a specific customer"""
    orders = db.query(Order).filter(Order.customer_id == customer_id).all()
    return orders



class CustomerResponse(BaseModel):
    customer_id: str
    customer_name: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int] = None 


    class Config:
        orm_mode = True


@app.get("/api/customers", response_model=List[dict])
async def get_customers(clerk_id: str = None, db: Session = Depends(get_db)):
    # Get user by clerk_id if provided
    user = None
    if clerk_id:
        user = get_user_by_clerk_id(db, clerk_id)
    
    # Filter by user_id if clerk_id was provided and user was found
    if user:
        # Order by created_at in descending order to get latest first
        customers = db.query(Customer).filter(Customer.user_id == user.id).order_by(Customer.created_at.desc()).all()
    else:
        # If no clerk_id or user not found, return all customers (for backward compatibility)
        customers = db.query(Customer).order_by(Customer.created_at.desc()).all()

    enriched_customers = []
    for customer in customers:
        enriched_customers.append({
            "CustomerId": customer.customer_id,
            "CustomerName": customer.customer_name,
            "Email": customer.email,
            "DeliveryDate": customer.created_at.isoformat() if customer.created_at else None,
            "UpdatedDate": customer.updated_at.isoformat() if customer.updated_at else None,
        })
    
    return enriched_customers


# @app.get("/api/customers", response_model=List[CustomerResponse])
# async def get_customers(db: Session = Depends(get_db)):
#     """Fetch all customers"""
#     customers = db.query(Customer).all()
#     return customers

# class IssueResponse(BaseModel):
#     """Issue response model"""
#     issue_id: int
#     customer_id: str
#     order_id: int
#     issue_type: str
#     description: str
#     status: str
#     priority: str
#     resolution_notes: str
#     created_at: datetime
#     updated_at: datetime
#     user_id: int

#     class Config:
#         orm_mode = True

# @app.get("/api/issues", response_model=List[IssueResponse])
# async def get_issues(db: Session = Depends(get_db)):
#     """Fetch all issues"""
#     issues = db.query(Issue).all()
#     return issues

# from pydantic import BaseModel
# from typing import List

# class IssueResponse(BaseModel):
#     issue_id: int
#     customer_id: str
#     order_id: int
#     issue_type: str
#     description: str
#     status: str
#     priority: str
#     resolution_notes: str
#     created_at: datetime
#     updated_at: datetime
#     user_id: int

#     class Config:
#         orm_mode = True

# @app.get("/api/issues", response_model=List[IssueResponse])
# async def get_issues(db: Session = Depends(get_db)):
#     """Fetch all issues"""
#     issues = db.query(Issue).all()
#     return issues

# from typing import List
# from pydantic import BaseModel
# from datetime import datetime

class IssueResponse(BaseModel):
    issue_id: int
    customer_id: str
    order_id: int
    issue_type: str
    description: str
    status: str
    priority: str
    resolution_notes: str
    created_at: datetime
    updated_at: datetime
    user_id: int

    class Config:
        orm_mode = True

@app.get("/api/issues", response_model=List[dict])
async def get_issues(clerk_id: str = None, db: Session = Depends(get_db)):
    """Fetch all issues ordered by latest first, filtered by user if clerk_id provided"""
    # Get user by clerk_id if provided
    user = None
    if clerk_id:
        user = get_user_by_clerk_id(db, clerk_id)
    
    # Filter by user_id if clerk_id was provided and user was found
    if user:
        # Order by created_at in descending order to get latest first
        issues = db.query(Issue).filter(Issue.user_id == user.id).order_by(Issue.created_at.desc()).all()
    else:
        # If no clerk_id or user not found, return all issues (for backward compatibility)
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    
    enriched_issues = []
    for issue in issues:
        enriched_issues.append({
            "IssueId": issue.issue_id,
            "CustomerId": issue.customer_id,
            "OrderId": issue.order_id,
            "IssueType": issue.issue_type,
            "Description": issue.description,
            "Status": issue.status,
            "Priority": issue.priority,
            "ResolutionNotes": issue.resolution_notes,
            "DeliveryDate": issue.created_at.isoformat() if issue.created_at else None,
            "UpdatedDate": issue.updated_at.isoformat() if issue.updated_at else None,
            "UserId": issue.user_id,
        })
    
    return enriched_issues





# from pydantic import BaseModel

# class EnquiryResponse(BaseModel):
#     enquiry_id: int
#     customer_id: str
#     description: str
#     category: str
#     priority: str
#     status: str
#     follow_up_date: datetime
#     created_at: datetime
#     updated_at: datetime
#     user_id: int

#     class Config:
#         orm_mode = True

# @app.get("/api/enquiries", response_model=List[EnquiryResponse])
# async def get_enquiries(db: Session = Depends(get_db)):
#     """Fetch all enquiries"""
#     enquiries = db.query(Enquiry).all()
#     return enquiries




class EnquiryResponse(BaseModel):
    enquiry_id: int
    customer_id: str
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # previously called orm_mode = True



@app.get("/api/enquiries", response_model=List[dict])
async def get_enquiries(clerk_id: str = None, db: Session = Depends(get_db)):
    """Fetch all enquiries with updated column names, ordered by latest first, filtered by user if clerk_id provided"""
    # Get user by clerk_id if provided
    user = None
    if clerk_id:
        user = get_user_by_clerk_id(db, clerk_id)
    
    # Filter by user_id if clerk_id was provided and user was found
    if user:
        # Order by created_at in descending order to get latest first
        enquiries = db.query(Enquiry).filter(Enquiry.user_id == user.id).order_by(Enquiry.created_at.desc()).all()
    else:
        # If no clerk_id or user not found, return all enquiries (for backward compatibility)
        enquiries = db.query(Enquiry).order_by(Enquiry.created_at.desc()).all()

    enriched_enquiries = []
    for enquiry in enquiries:
        enriched_enquiries.append({
            "EnquiryId": enquiry.enquiry_id,
            "CustomerId": enquiry.customer_id,
            "Description": enquiry.description,
            "Category": enquiry.category,
            "Priority": enquiry.priority,
            "Status": enquiry.status,
            "FollowUpDate": enquiry.follow_up_date.isoformat() if enquiry.follow_up_date else None,
            "DeliveryDate": enquiry.created_at.isoformat() if enquiry.created_at else None,
            "UpdatedDate": enquiry.updated_at.isoformat() if enquiry.updated_at else None,
            
        })

    return enriched_enquiries




@app.get("/api/response-metrics", response_model=List[dict])
async def get_response_metrics(clerk_id: str = None, days: int = 30, db: Session = Depends(get_db)):
    """Fetch response metrics for the dashboard"""
    # Get user by clerk_id if provided
    user = None
    if clerk_id:
        user = get_user_by_clerk_id(db, clerk_id)
    
    # Calculate the date range (last X days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Filter by user_id if clerk_id was provided and user was found
    if user:
        metrics = db.query(ResponseMetrics).filter(
            ResponseMetrics.user_id == user.id,
            ResponseMetrics.message_received_at >= start_date,
            ResponseMetrics.message_received_at <= end_date
        ).order_by(ResponseMetrics.message_received_at.desc()).all()
    else:
        # If no clerk_id or user not found, return all metrics within date range
        metrics = db.query(ResponseMetrics).filter(
            ResponseMetrics.message_received_at >= start_date,
            ResponseMetrics.message_received_at <= end_date
        ).order_by(ResponseMetrics.message_received_at.desc()).all()
    
    # Format the metrics for the response
    formatted_metrics = []
    for metric in metrics:
        formatted_metrics.append({
            "MetricId": metric.metric_id,
            "UserId": metric.user_id,
            "MessageId": metric.message_id,
            "CustomerId": metric.customer_id,
            "MessageType": metric.message_type,
            "ResponseType": metric.response_type,
            "ResponseTimeSeconds": round(metric.response_time_seconds, 2),
            "MessageReceivedAt": metric.message_received_at.isoformat() if metric.message_received_at else None,
            "ResponseSentAt": metric.response_sent_at.isoformat() if metric.response_sent_at else None,
            "CreatedAt": metric.created_at.isoformat() if metric.created_at else None
        })
    
    return formatted_metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)