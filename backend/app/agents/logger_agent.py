import os
import json
import csv
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import requests
import pandas as pd
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("waffy_logger.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("waffy_logger")

# Load environment variables
load_dotenv()

# Database setup - reuse the same Base and engine from main.py
from setup_db import engine, Base, SessionLocal
from main import User, UserSettings

from app.models import Customer, Business, BusinessTag, Interaction, Order, Issue, Feedback, Enquiry, Category
# Removed old Customer model. Will add new model based on tables.sql.
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="customer")
    orders = relationship("Order", back_populates="customer")

class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String(20), primary_key=True)
    customer_name = Column(String(100))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    orders = relationship("Order", back_populates="customer")
    feedbacks = relationship("Feedback", back_populates="customer")
    enquiries = relationship("Enquiry", back_populates="customer")
    interactions = relationship("Interaction", back_populates="customer")

class Business(Base):
    __tablename__ = "businesses"
    business_phone_number = Column(String(20), primary_key=True)
    business_phone_id = Column(String(50))
    business_name = Column(String(100))
    business_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BusinessTag(Base):
    __tablename__ = "business_tags"
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    business_phone_number = Column(String(20), ForeignKey('businesses.business_phone_number'))
    tag = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Interaction(Base):
    __tablename__ = "interactions"
    interaction_id = Column(Integer, primary_key=True, autoincrement=True)
    whatsapp_message_id = Column(String(100), unique=True)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    timestamp = Column(DateTime)
    message_type = Column(String(20))
    category = Column(String(20))
    priority = Column(String(10))
    status = Column(String(20))
    sentiment = Column(String(10))
    message_summary = Column(String(200))
    response_time = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    customer = relationship("Customer", back_populates="interactions")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    order_number = Column(String(50))
    item = Column(String(100))
    quantity = Column(Integer)
    notes = Column(String(200))
    order_status = Column(String(20))
    total_amount = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    customer = relationship("Customer", back_populates="orders")
    feedbacks = relationship("Feedback", back_populates="order")

class Issue(Base):
    __tablename__ = "issues"
    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    description = Column(String(200))
    category = Column(String(20))
    priority = Column(String(10))
    resolution_notes = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    rating = Column(Integer)
    comments = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    customer = relationship("Customer", back_populates="feedbacks")
    order = relationship("Order", back_populates="feedbacks")

class Enquiry(Base):
    __tablename__ = "enquiries"
    enquiry_id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    description = Column(String(200))
    category = Column(String(20))
    priority = Column(String(10))
    status = Column(String(20))
    follow_up_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relationships
    customer = relationship("Customer", back_populates="enquiries")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, nullable=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    business_phone_id = Column(String, nullable=True)
    message_type = Column(String, nullable=True)
    content = Column(Text)
    predicted_category = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    extracted_info = Column(Text, nullable=True)  # JSON string
    context = Column(Text, nullable=True)  # JSON string
    timestamp = Column(DateTime, default=datetime.utcnow)
    raw_timestamp_utc = Column(Integer, nullable=True)
    
    # Relationships
    customer = relationship("Customer", back_populates="messages")

# Removed old Order model. Will add new model based on tables.sql.
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"))
    order_details = Column(Text, nullable=True)  # JSON string
    status = Column(String, default="new")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    customer = relationship("Customer", back_populates="orders")

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

class LoggerAgent:
    def __init__(self, user_id: str):
        """Initialize the logger agent for a specific user"""
        self.user_id = user_id
        self.db = SessionLocal()
        self.user_settings = self._get_user_settings()
        self.excel_directory = os.path.join(os.getcwd(), "excel_exports")
        
        # Create excel directory if it doesn't exist
        if not os.path.exists(self.excel_directory):
            os.makedirs(self.excel_directory)
    
    def __del__(self):
        """Close the database session when the object is destroyed"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def _get_user_settings(self) -> Optional[Dict]:
        """Get user settings from the database"""
        try:
            user = self.db.query(User).filter(User.clerk_id == self.user_id).first()
            if user and user.settings:
                return {
                    "crm_type": user.settings.crm_type,
                    "hubspot_access_token": user.settings.hubspot_access_token,
                    "business_name": user.settings.business_name,
                    "business_phone": user.settings.contact_phone,
                    "business_email": user.settings.contact_email,
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching user settings: {e}")
            return None
    
    def process_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process incoming messages and route to appropriate handler"""
        if not messages:
            return {"status": "error", "message": "No messages provided"}
        
        try:
            # Store messages in database
            self._store_messages(messages)
            
            # Process based on CRM type
            if not self.user_settings:
                return {"status": "error", "message": "User settings not found"}
            
            crm_type = self.user_settings.get("crm_type", "").lower()
            
            if crm_type == "hubspot" and self.user_settings.get("hubspot_access_token"):
                return self._process_hubspot(messages)
            elif crm_type == "excel":
                return self._process_excel(messages)
            else:
                return {"status": "error", "message": f"Unsupported CRM type: {crm_type}"}
        
        except Exception as e:
            logger.error(f"Error processing messages: {e}")
            return {"status": "error", "message": str(e)}
    
    def _store_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Store messages in the database"""
        try:
            for msg in messages:
                # Only process messages with required fields
                if "message" not in msg:
                    continue
                
                # Get or create customer
                customer_id = msg.get("customer_id", msg.get("sender"))
                if not customer_id:
                    continue
                
                customer = self.db.query(Customer).filter(Customer.customer_id == customer_id).first()
                if not customer:
                    customer = Customer(
                        customer_id=customer_id,
                        phone_number=customer_id,
                        name=msg.get("customer_name", "")
                    )
                    self.db.add(customer)
                    self.db.commit()
                
                # Create message record
                message = Message(
                    message_id=msg.get("message_id"),
                    customer_id=customer_id,
                    business_phone_id=msg.get("business_phone_id"),
                    message_type=msg.get("message_type", "text"),
                    content=msg.get("message", ""),
                    predicted_category=msg.get("predicted_category"),
                    priority=msg.get("priority"),
                    extracted_info=json.dumps(msg.get("extracted_info", {})),
                    context=json.dumps(msg.get("context", [])),
                    timestamp=datetime.strptime(msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S") if "timestamp" in msg else datetime.utcnow(),
                    raw_timestamp_utc=msg.get("raw_timestamp_utc")
                )
                self.db.add(message)
                
                # Check if this is an order-related message
                if msg.get("predicted_category") in ["new order", "order modification"]:
                    # Check if there's an existing order for this customer
                    order = self.db.query(Order).filter(
                        Order.customer_id == customer_id,
                        Order.status.in_(["new", "in_progress"])
                    ).first()
                    
                    if not order:
                        # Create a new order
                        order = Order(
                            customer_id=customer_id,
                            order_details=json.dumps({
                                "initial_message": msg.get("message"),
                                "extracted_info": msg.get("extracted_info", {})
                            }),
                            status="new"
                        )
                        self.db.add(order)
                    else:
                        # Update existing order
                        order_details = json.loads(order.order_details) if order.order_details else {}
                        
                        # Append new extracted info
                        if "extracted_info" in msg and msg["extracted_info"]:
                            if "extracted_info" not in order_details:
                                order_details["extracted_info"] = {}
                            
                            order_details["extracted_info"].update(msg["extracted_info"])
                        
                        # Update order details
                        order.order_details = json.dumps(order_details)
                        order.updated_at = datetime.utcnow()
            
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing messages: {e}")
            raise
    
    def _process_hubspot(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process messages for Hubspot CRM integration"""
        try:
            access_token = self.user_settings.get("hubspot_access_token")
            if not access_token:
                return {"status": "error", "message": "HubSpot Access Token not found"}
            
            # Validate the token with a simple API call
            validation_result = self._validate_hubspot_token(access_token)
            if validation_result.get("status") == "error":
                return validation_result
            
            # Process each message for unique customers
            processed_customers = set()
            for msg in messages:
                customer_id = msg.get("customer_id", msg.get("sender"))
                if not customer_id or customer_id in processed_customers:
                    continue
                
                # Create or update contact in HubSpot
                contact_result = self._create_hubspot_contact(access_token, msg)
                if contact_result.get("status") == "error":
                    logger.error(f"Error creating HubSpot contact: {contact_result.get('message')}")
                    continue
                
                processed_customers.add(customer_id)
                
                # Create ticket for high priority messages
                if msg.get("priority") == "high":
                    ticket_result = self._create_hubspot_ticket(access_token, msg)
                    if ticket_result.get("status") == "error":
                        logger.error(f"Error creating HubSpot ticket: {ticket_result.get('message')}")
            
            return {"status": "success", "message": f"Processed {len(processed_customers)} customers in HubSpot"}
            
        except Exception as e:
            logger.error(f"Error processing HubSpot integration: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_hubspot_token(self, access_token: str) -> Dict[str, Any]:
        """Validate the HubSpot access token with a simple API call"""
        try:
            # Try to get the account info to validate the token
            url = "https://api.hubapi.com/account-info/v3/details"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                account_info = response.json()
                logger.info(f"Successfully connected to HubSpot account: {account_info.get('portalId')}")
                return {"status": "success", "account_info": account_info}
            else:
                error_message = f"Failed to validate HubSpot token: {response.status_code}"
                try:
                    error_details = response.json()
                    error_message = f"{error_message} - {error_details.get('message', '')}"
                except:
                    error_message = f"{error_message} - {response.text}"
                
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error validating HubSpot token: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
    
    def _create_hubspot_contact(self, access_token: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a contact in HubSpot"""
        try:
            customer_id = message.get("customer_id", message.get("sender"))
            customer_name = message.get("customer_name", "")
            
            # Prepare contact properties using only standard HubSpot properties
            contact_properties = {
                "phone": customer_id
                # We don't use custom properties like "whatsapp_id" since they need to be created first
            }
            
            # Add name if available
            if customer_name:
                name_parts = customer_name.split()
                if len(name_parts) > 1:
                    contact_properties["firstname"] = name_parts[0]
                    contact_properties["lastname"] = " ".join(name_parts[1:])
                else:
                    contact_properties["firstname"] = customer_name
            
            # Check if contact exists
            search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "phone",
                                "operator": "EQ",
                                "value": customer_id
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(search_url, headers=headers, json=search_payload)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if results:
                    # Update existing contact
                    contact_id = results[0]["id"]
                    update_url = f"https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}"
                    
                    update_payload = {
                        "properties": contact_properties
                    }
                    
                    update_response = requests.patch(update_url, headers=headers, json=update_payload)
                    
                    if update_response.status_code == 200:
                        logger.info(f"Updated HubSpot contact: {contact_id}")
                        return {"status": "success", "contact_id": contact_id, "action": "updated"}
                    else:
                        error_message = f"Failed to update HubSpot contact: {update_response.status_code}"
                        try:
                            error_details = update_response.json()
                            error_message = f"{error_message} - {error_details.get('message', '')}"
                        except:
                            error_message = f"{error_message} - {update_response.text}"
                        
                        logger.error(error_message)
                        return {"status": "error", "message": error_message}
                else:
                    # Create new contact
                    create_url = "https://api.hubapi.com/crm/v3/objects/contacts"
                    
                    create_payload = {
                        "properties": contact_properties
                    }
                    
                    create_response = requests.post(create_url, headers=headers, json=create_payload)
                    
                    if create_response.status_code == 201:
                        contact_id = create_response.json().get('id')
                        logger.info(f"Created new HubSpot contact: {contact_id}")
                        
                        # Optionally create a note with WhatsApp info
                        note_result = self._create_hubspot_note(
                            access_token, 
                            contact_id, 
                            f"WhatsApp Contact: {customer_id}",
                            f"This contact was created from WhatsApp message. WhatsApp ID: {customer_id}"
                        )
                        
                        return {"status": "success", "contact_id": contact_id, "action": "created"}
                    else:
                        error_message = f"Failed to create HubSpot contact: {create_response.status_code}"
                        try:
                            error_details = create_response.json()
                            error_message = f"{error_message} - {error_details.get('message', '')}"
                        except:
                            error_message = f"{error_message} - {create_response.text}"
                        
                        logger.error(error_message)
                        return {"status": "error", "message": error_message}
            else:
                error_message = f"Failed to search HubSpot contacts: {response.status_code}"
                try:
                    error_details = response.json()
                    error_message = f"{error_message} - {error_details.get('message', '')}"
                except:
                    error_message = f"{error_message} - {response.text}"
                
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error creating/updating HubSpot contact: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
    
    def _create_hubspot_note(self, access_token: str, contact_id: str, title: str, content: str) -> Dict[str, Any]:
        """Create a note in HubSpot and associate it with a contact"""
        try:
            # Create note
            note_url = "https://api.hubapi.com/crm/v3/objects/notes"
            
            note_properties = {
                "hs_note_body": content,
                "hs_timestamp": str(int(datetime.utcnow().timestamp() * 1000))
            }
            
            note_payload = {
                "properties": note_properties
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            note_response = requests.post(note_url, headers=headers, json=note_payload)
            
            if note_response.status_code == 201:
                note_id = note_response.json().get("id")
                logger.info(f"Created HubSpot note: {note_id}")
                
                # Associate note with contact
                association_url = f"https://api.hubapi.com/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/note_to_contact"
                association_response = requests.put(association_url, headers=headers)
                
                if association_response.status_code == 200:
                    logger.info(f"Associated note {note_id} with contact {contact_id}")
                    return {"status": "success", "note_id": note_id, "contact_id": contact_id}
                else:
                    error_message = f"Failed to associate note with contact: {association_response.status_code}"
                    try:
                        error_details = association_response.json()
                        error_message = f"{error_message} - {error_details.get('message', '')}"
                    except:
                        error_message = f"{error_message} - {association_response.text}"
                    
                    logger.error(error_message)
                    return {"status": "error", "message": error_message}
            else:
                error_message = f"Failed to create HubSpot note: {note_response.status_code}"
                try:
                    error_details = note_response.json()
                    error_message = f"{error_message} - {error_details.get('message', '')}"
                except:
                    error_message = f"{error_message} - {note_response.text}"
                
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error creating HubSpot note: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
    
    def _create_hubspot_ticket(self, access_token: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Create a ticket in HubSpot for high priority messages"""
        try:
            customer_id = message.get("customer_id", message.get("sender"))
            
            # First, find the contact ID
            search_url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "phone",
                                "operator": "EQ",
                                "value": customer_id
                            }
                        ]
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(search_url, headers=headers, json=search_payload)
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                
                if results:
                    contact_id = results[0]["id"]
                    
                    # Create ticket
                    ticket_url = "https://api.hubapi.com/crm/v3/objects/tickets"
                    
                    # Prepare ticket properties
                    ticket_properties = {
                        "subject": f"High Priority: {message.get('predicted_category', 'WhatsApp Message')}",
                        "content": message.get("message", ""),
                        "hs_pipeline": "0",  # Default pipeline
                        "hs_pipeline_stage": "1"  # New stage
                    }
                    
                    ticket_payload = {
                        "properties": ticket_properties
                    }
                    
                    # Create the ticket
                    ticket_response = requests.post(ticket_url, headers=headers, json=ticket_payload)
                    
                    if ticket_response.status_code == 201:
                        ticket_id = ticket_response.json().get("id")
                        logger.info(f"Created HubSpot ticket: {ticket_id}")
                        
                        # Associate ticket with contact
                        association_url = f"https://api.hubapi.com/crm/v3/objects/tickets/{ticket_id}/associations/contacts/{contact_id}/ticket_to_contact"
                        association_response = requests.put(association_url, headers=headers)
                        
                        if association_response.status_code == 200:
                            logger.info(f"Associated ticket {ticket_id} with contact {contact_id}")
                            return {"status": "success", "ticket_id": ticket_id, "contact_id": contact_id}
                        else:
                            error_message = f"Failed to associate ticket with contact: {association_response.status_code}"
                            try:
                                error_details = association_response.json()
                                error_message = f"{error_message} - {error_details.get('message', '')}"
                            except:
                                error_message = f"{error_message} - {association_response.text}"
                            
                            logger.error(error_message)
                            return {"status": "error", "message": error_message}
                    else:
                        error_message = f"Failed to create HubSpot ticket: {ticket_response.status_code}"
                        try:
                            error_details = ticket_response.json()
                            error_message = f"{error_message} - {error_details.get('message', '')}"
                        except:
                            error_message = f"{error_message} - {ticket_response.text}"
                        
                        logger.error(error_message)
                        return {"status": "error", "message": error_message}
                else:
                    error_message = f"Contact not found for customer ID: {customer_id}"
                    logger.error(error_message)
                    return {"status": "error", "message": error_message}
            else:
                error_message = f"Failed to search HubSpot contacts: {response.status_code}"
                try:
                    error_details = response.json()
                    error_message = f"{error_message} - {error_details.get('message', '')}"
                except:
                    error_message = f"{error_message} - {response.text}"
                
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error creating HubSpot ticket: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
    
    def _process_excel(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process messages for Excel export"""
        try:
            # Create timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Process customers
            customers_data = []
            messages_data = []
            orders_data = []
            
            # Extract unique customers
            unique_customers = {}
            for msg in messages:
                customer_id = msg.get("customer_id", msg.get("sender"))
                if not customer_id or customer_id in unique_customers:
                    continue
                
                unique_customers[customer_id] = {
                    "customer_id": customer_id,
                    "name": msg.get("customer_name", ""),
                    "last_message_timestamp": msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
                }
            
            # Add customers to data
            customers_data.extend(unique_customers.values())
            
            # Process messages
            for msg in messages:
                if "message" not in msg:
                    continue
                
                messages_data.append({
                    "message_id": msg.get("message_id", ""),
                    "customer_id": msg.get("customer_id", msg.get("sender", "")),
                    "timestamp": msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                    "message": msg.get("message", ""),
                    "predicted_category": msg.get("predicted_category", ""),
                    "priority": msg.get("priority", ""),
                    "extracted_info": json.dumps(msg.get("extracted_info", {})),
                    "context": json.dumps(msg.get("context", []))
                })
                
                # Check if this is an order-related message
                if msg.get("predicted_category") in ["new order", "order modification"]:
                    orders_data.append({
                        "customer_id": msg.get("customer_id", msg.get("sender", "")),
                        "timestamp": msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                        "message": msg.get("message", ""),
                        "extracted_info": json.dumps(msg.get("extracted_info", {})),
                        "status": "new"
                    })
            
            # Save to Excel files
            if customers_data:
                self._save_to_excel(customers_data, "customers", timestamp)
            
            if messages_data:
                self._save_to_excel(messages_data, "messages", timestamp)
            
            if orders_data:
                self._save_to_excel(orders_data, "orders", timestamp)
            
            return {
                "status": "success", 
                "message": f"Exported data to Excel files",
                "files": {
                    "customers": f"customers_{timestamp}.xlsx" if customers_data else None,
                    "messages": f"messages_{timestamp}.xlsx" if messages_data else None,
                    "orders": f"orders_{timestamp}.xlsx" if orders_data else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing Excel export: {e}")
            return {"status": "error", "message": str(e)}
    
    def _save_to_excel(self, data: List[Dict[str, Any]], file_type: str, timestamp: str) -> None:
        """Save data to an Excel file"""
        if not data:
            return
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Define filename
        filename = os.path.join(self.excel_directory, f"{file_type}_{timestamp}.xlsx")
        
        # Save to Excel
        df.to_excel(filename, index=False)
        logger.info(f"Saved {len(data)} {file_type} records to {filename}")

# Function to handle incoming messages
def process_whatsapp_messages(user_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process WhatsApp messages for a specific user"""
    agent = LoggerAgent(user_id)
    result = agent.process_messages(messages)
    return result

# Example usage (for testing)
if __name__ == "__main__":
    # Test data
    test_messages = [
        {
            "timestamp": "2025-04-22 19:28:15",
            "raw_timestamp_utc": 1745350095,
            "message_id": "wamid.HBgMNDQ3Nzc4NTk2NzczFQIAEhgUM0EwMzBEQkUyNzZCQzdEMzYyRTAA",
            "message_type": "text",
            "customer_id": "447778596773",
            "sender": "447778596773",
            "customer_name": "Akanksha",
            "message": "hi",
            "predicted_category": "greeting",
            "priority": "low",
            "extracted_info": {},
            "context": [],
            "business_phone_number": "15556454320",
            "business_phone_id": "574048935800997"
        },
        {
            "message": "can i place an order",
            "predicted_category": "new order",
            "priority": "high",
            "extracted_info": {},
            "context": ["hi"],
            "customer_id": "447778596773",
            "sender": "447778596773",
            "timestamp": "2025-04-22 19:29:15",
        },
        {
            "message": "for 2 cakes",
            "predicted_category": "new order",
            "priority": "moderate",
            "extracted_info": {
                "quantity": "2",
                "product_type": "cakes"
            },
            "context": ["hi", "can i place an order"],
            "customer_id": "447778596773",
            "sender": "447778596773",
            "timestamp": "2025-04-22 19:30:15",
        },
        {
            "message": "nut-free please",
            "predicted_category": "order modification",
            "priority": "high",
            "extracted_info": {
                "allergy_info": "nut-free",
                "previous_order_details_needed": "true"
            },
            "context": ["hi", "can i place an order", "for 2 cakes"],
            "customer_id": "447778596773",
            "sender": "447778596773",
            "timestamp": "2025-04-22 19:31:15",
        }
    ]
    
    # Test with a sample user ID (replace with actual user ID for testing)
    test_user_id = "user_2NF8PqPsIFYYEEJiZZBQJTHDvZZ"
    result = process_whatsapp_messages(test_user_id, test_messages)
    print(json.dumps(result, indent=2))
