import os
import json
import csv
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import requests
import pandas as pd
from dotenv import load_dotenv
import traceback
from app.state import MessageState
from utils.encryption import decrypt_value

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

# Database setup - reuse the same Base and engine
from setup_db import engine, Base
from database import SessionLocal

# Import all models from app.models
from app.models import User, UserSettings, Customer, Business, BusinessTag, Interaction, Order, Issue, Feedback, Enquiry, Category
from app.models import ErrorLog

class LoggerAgent:
    def __init__(self, user_id: str):
        """Initialize the logger agent for a specific user"""
        self.user_id = user_id
        self.db = SessionLocal()
        self.user_settings = self._get_user_settings()
        
        # Check if HubSpot integration is enabled
        self.hubspot_enabled = False
        self.hubspot_access_token = None
        print("ABBBBBBBB")
        # Check for HubSpot configuration
        print("User settings found", self.user_settings)
        if self.user_settings and self.user_settings.hubspot_access_token:
            print("User settings found")
            # Enable HubSpot if crm_type is set to hubspot
            if self.user_settings.crm_type == "hubspot":
                self.hubspot_enabled = True
                # Use the provided HubSpot Private App Access Token and decrypt it
                try:
                    # Try to decrypt the token
                    self.hubspot_access_token = decrypt_value(self.user_settings.hubspot_access_token)
                    
                    if self.hubspot_access_token:
                        self.hubspot_enabled = True
                        logger.info("Successfully decrypted HubSpot access token")
                    else:
                        logger.warning("Decryption returned None or empty string")
                        self.hubspot_enabled = False
                except Exception as e:
                    logger.error(f"Error decrypting HubSpot access token: {str(e)}")
                    self.hubspot_enabled = False
                        
        # Check if consolidated data view is enabled
        self.view_consolidated_data = False
        if self.user_settings and hasattr(self.user_settings, 'view_consolidated_data'):
            self.view_consolidated_data = self.user_settings.view_consolidated_data
        
        # Always store in DB if view_consolidated_data is enabled or for Excel integration
        self.store_in_db = self.view_consolidated_data
        
        # For Excel integration, always enable database storage regardless of view_consolidated_data setting
        if self.user_settings and self.user_settings.crm_type == 'excel':
            self.store_in_db = True
            self.view_consolidated_data = True

    def __del__(self):
        """Close the database session when the object is destroyed"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def _get_user_settings(self):
        """Get user settings from the database"""
        try:
            # First, try to parse the user_id as an integer (database ID)
            try:
                user_id_int = int(self.user_id)
                # If it's a numeric ID, try to get settings directly
                logger.info(f"Looking for user settings with user_id {user_id_int}")
                user_settings = self.db.query(UserSettings).filter(UserSettings.user_id == user_id_int).first()
                if user_settings:
                    logger.info(f"Found user settings for user_id {user_id_int}")
                    return user_settings
            except ValueError:
                # Not a numeric ID, continue with clerk_id lookup
                pass
                
            # If we get here, either the ID wasn't numeric or no settings were found
            # Try to find by clerk_id
            logger.info(f"Looking for user with clerk_id {self.user_id}")
            user = self.db.query(User).filter(User.clerk_id == self.user_id).first()
            if user:
                logger.info(f"Found user with clerk_id {self.user_id}, looking for settings with user_id {user.id}")
                return self.db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
                
            logger.warning(f"No user or settings found for ID {self.user_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user settings: {e}")
            self._log_error("Database Error", f"Error getting user settings: {e}", None)
            return None
            
    def _log_error(self, error_type: str, error_message: str, user_id: Optional[int] = None):
        """Log errors to the error_logs table"""
        try:
            error_log = ErrorLog(
                user_id=user_id,
                error_type=error_type,
                error_message=error_message,
                stack_trace=traceback.format_exc(),
                source="logger_agent"
            )
            self.db.add(error_log)
            self.db.commit()
            logger.info(f"Error logged to database: {error_type} - {error_message}")
        except Exception as e:
            logger.error(f"Failed to log error to database: {e}")
    
    def process_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process incoming messages and route to appropriate handler"""
        if not messages:
            return {"status": "error", "message": "No messages provided"}
        
        try:
            results = []
            for message_data in messages:
                # Convert dict to MessageState if needed
                if not isinstance(message_data, MessageState):
                    message_state = MessageState(**message_data)
                else:
                    message_state = message_data
                    
                result = self.process_message_state(message_state)
                results.append(result)
                
            return {
                "status": "success",
                "message": f"Processed {len(results)} messages",
                "results": results
            }
        except Exception as e:
            error_msg = f"Error processing messages: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Batch Processing Error", error_msg, user_id)
            return {"status": "error", "message": error_msg}
    
    def process_message_state(self, message_state: MessageState) -> Dict[str, Any]:
        """Process a single message in MessageState format"""
        try:
            # Store the message_state in the instance for use by other methods
            self.message_state = message_state
            interaction = None
            
            # Always store in the database if view_consolidated_data is enabled or if HubSpot is enabled
            if self.store_in_db:
                # Log the interaction first
                interaction = self._store_interaction(message_state)
                
                # Store in appropriate table based on table_name if specified
                if message_state.table_name:
                    self._store_in_specific_table(message_state)
                
            # If HubSpot integration is enabled, send to HubSpot
            if self.hubspot_enabled:
                self._send_to_hubspot(message_state)
                
            return {
                "status": "success",
                "message": f"Message processed successfully",
                "interaction_id": interaction.interaction_id if interaction else None,
                "stored_in_db": self.store_in_db,
                "sent_to_hubspot": self.hubspot_enabled
            }
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Message Processing Error", error_msg, user_id)
            return {"status": "error", "message": error_msg}
            
    def _get_or_create_customer(self, message_state: MessageState) -> Customer:
        """Get or create a customer record"""
        try:
            # Check if customer exists
            customer = self.db.query(Customer).filter(Customer.customer_id == message_state.customer_id).first()
            
            if not customer:
                # Ensure user_id is set correctly
                user_id = int(self.user_id) if self.user_id else None
                if self.user_settings and self.user_settings.user_id:
                    user_id = self.user_settings.user_id
                
                # If we still don't have a user_id, we can't create a customer
                if user_id is None:
                    raise ValueError("Cannot create customer without a valid user_id")
                    
                # Create new customer
                customer = Customer(
                    customer_id=message_state.customer_id,
                    user_id=user_id,
                    customer_name=message_state.customer_name if hasattr(message_state, 'customer_name') else "",
                    email="",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(customer)
                self.db.commit()
                self.db.refresh(customer)
                logger.info(f"Created new customer: {customer.customer_id}")
            
            return customer
            
        except Exception as e:
            error_msg = f"Error getting/creating customer: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            self.db.rollback()
            raise
    
    def _store_interaction(self, message_state: MessageState) -> Optional[Interaction]:
        """Store message in the interactions table"""
        try:
            # Get or create customer
            customer = self._get_or_create_customer(message_state)
            
            # Ensure valid status values - check constraint issue
            valid_statuses = ["pending", "processed", "responded", "closed", "archived"]
            status = "pending"  # Default to pending as a safe value
            
            # Ensure valid message_type values
            valid_message_types = ["text", "image", "audio", "video", "document", "location"]
            message_type = message_state.message_type if hasattr(message_state, 'message_type') and message_state.message_type in valid_message_types else "text"
            
            # Extract whatsapp_message_id if available
            whatsapp_message_id = message_state.message_id if hasattr(message_state, 'message_id') else ""
            
            # Check if an interaction with this message ID already exists
            if whatsapp_message_id:
                existing_interaction = self.db.query(Interaction).filter(Interaction.whatsapp_message_id == whatsapp_message_id).first()
                if existing_interaction:
                    logger.info(f"Interaction with message ID {whatsapp_message_id} already exists, updating it")
                    # Update existing interaction
                    existing_interaction.category = message_state.predicted_category
                    existing_interaction.priority = message_state.priority
                    existing_interaction.status = status
                    existing_interaction.message_summary = message_state.message[:200] if message_state.message else ""
                    existing_interaction.updated_at = datetime.utcnow()
                    
                    self.db.commit()
                    self.db.refresh(existing_interaction)
                    
                    logger.info(f"Updated interaction: {existing_interaction.interaction_id}")
                    return existing_interaction
            
            # Ensure user_id is set correctly
            user_id = int(self.user_id) if self.user_id else None
            if self.user_settings and self.user_settings.user_id:
                user_id = self.user_settings.user_id
                
            # If user_id is still None, we can't create an interaction
            if user_id is None:
                raise ValueError("Cannot create interaction without a valid user_id")
            
            # Create new interaction record if no existing one found
            interaction = Interaction(
                user_id=user_id,
                whatsapp_message_id=whatsapp_message_id,
                customer_id=message_state.customer_id,
                timestamp=datetime.fromisoformat(message_state.timestamp) if hasattr(message_state, 'timestamp') and message_state.timestamp else datetime.utcnow(),
                message_type=message_type,
                category=message_state.predicted_category,
                priority=message_state.priority,
                status=status,
                message_summary=message_state.message[:200] if message_state.message else "",
                sentiment="neutral"  # Default sentiment
            )
            
            self.db.add(interaction)
            self.db.commit()
            self.db.refresh(interaction)
            
            logger.info(f"Stored new interaction: {interaction.interaction_id}")
            return interaction
            
        except Exception as e:
            error_msg = f"Error storing interaction: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            self.db.rollback()
            return None
            
    def _get_interaction_by_message_id(self, message_id: str) -> Optional[Interaction]:
        """Get an interaction by WhatsApp message ID"""
        try:
            interaction = self.db.query(Interaction).filter(Interaction.whatsapp_message_id == message_id).first()
            return interaction
        except Exception as e:
            logger.error(f"Error getting interaction by message ID: {str(e)}")
            return None
            
    def _store_in_specific_table(self, message_state: MessageState) -> None:
        """Store data in specific table based on table_name"""
        try:
            # Get table name
            table_name = message_state.table_name
            
            # Extract data from the message state
            data = {
                "customer_id": message_state.customer_id,
                "message": message_state.message,
                "category": message_state.predicted_category,
                "priority": message_state.priority,
                "extracted_info": message_state.extracted_info  # Pass extracted_info as a separate field
            }
            
            # Store in table
            if table_name == "orders":
                self._store_order(data)
            elif table_name == "issues":
                self._store_issue(data)
            elif table_name == "enquiries":
                self._store_enquiry(data)
            elif table_name == "feedback":
                self._store_feedback(data)
            else:
                logger.error(f"Unsupported table name: {table_name}")
                
        except Exception as e:
            error_msg = f"Error storing data in specific table: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            
    def _send_to_hubspot(self, message_state: MessageState) -> None:
        """Send data to HubSpot"""
        try:
            # Get access token
            access_token = self.hubspot_access_token
            
            # Create or update contact in HubSpot
            contact_data = {
                "customer_id": message_state.customer_id,
                "phone": message_state.customer_id
            }
            
            # Add customer name if available
            if hasattr(message_state, 'customer_name') and message_state.customer_name:
                contact_data["customer_name"] = message_state.customer_name
            
            self._create_hubspot_contact(access_token, contact_data)
            
            # Create ticket for high priority messages
            if hasattr(message_state, 'priority') and message_state.priority == "high":
                ticket_data = {
                    "customer_id": message_state.customer_id,
                    "subject": f"High Priority: {message_state.predicted_category}",
                    "description": message_state.message,
                    "priority": "high",
                    "category": message_state.predicted_category
                }
                self._create_hubspot_ticket(access_token, ticket_data)
            
            # Determine if this is an order based on category
            is_order = False
            if hasattr(message_state, 'predicted_category') and message_state.predicted_category:
                is_order = message_state.predicted_category.lower() in ["new_order", "new order", "order_modification", "order modification"]
            
            # Check if table_name is available and indicates an order
            table_name = "unknown"
            if hasattr(message_state, 'table_name') and message_state.table_name:
                table_name = message_state.table_name
                is_order = is_order or table_name.lower() == "orders"
            
            # Common data for both tickets and deals
            common_data = {
                "customer_id": message_state.customer_id,
                "message": message_state.message
            }
            
            # Add priority if available
            if hasattr(message_state, 'priority') and message_state.priority:
                common_data["priority"] = message_state.priority
            
            # Add category if available
            if hasattr(message_state, 'predicted_category') and message_state.predicted_category:
                common_data["category"] = message_state.predicted_category
            
            # Add extracted info if available
            extracted_info = {}
            if hasattr(message_state, 'extracted_info') and message_state.extracted_info:
                if isinstance(message_state.extracted_info, dict):
                    extracted_info = message_state.extracted_info
                    common_data["extracted_info"] = extracted_info
            
            # Create order for orders
            if is_order:
                order_data = common_data.copy()
                # Add order-specific fields from extracted_info
                for key, value in extracted_info.items():
                    order_data[key] = value
            
                # Check if the Order object type exists in HubSpot
                order_object_exists = self._check_hubspot_object_exists(access_token, "order")
            
                if order_object_exists:
                    logger.info("HubSpot Order object type exists, creating order using Orders API")
                    # Get available properties for the Order object
                    available_properties = self._get_hubspot_order_properties(access_token)
                    logger.info(f"Available HubSpot Order properties: {available_properties}")
                
                    # Create order in HubSpot using the Orders API with dynamic properties
                    contact_id = self._get_hubspot_contact_id(access_token, message_state.customer_id)
                    if contact_id:
                        # Extract items from the order data
                        items = []
                        if "products" in order_data and isinstance(order_data["products"], list):
                            for product in order_data["products"]:
                                items.append({
                                    "name": product.get("item", ""),
                                    "quantity": product.get("quantity", 1),
                                    "notes": product.get("notes", ""),
                                    "price": product.get("price", 0)
                                })
                    
                        # Create the order with dynamic properties
                        self._create_hubspot_order(access_token, items, order_data.get("message", ""), contact_id, order_data)
                    else:
                        logger.warning(f"Could not find HubSpot contact for {message_state.customer_id}, falling back to note creation")
                        self._create_hubspot_deal(access_token, order_data)
                else:
                    logger.info("HubSpot Order object type does not exist, creating order as note")
                    self._create_hubspot_deal(access_token, order_data)
            
            # Create ticket for issues
            elif table_name == "issues" or (hasattr(message_state, 'predicted_category') and 
                  message_state.predicted_category in ["issue", "complaint"]):
                ticket_data = common_data.copy()
                ticket_data["subject"] = f"Issue: {message_state.predicted_category if hasattr(message_state, 'predicted_category') else 'Unknown'}"
                ticket_data["description"] = message_state.message
                self._create_hubspot_ticket(access_token, ticket_data)
            
            # Create ticket for other table data (feedback, enquiries, etc.)
            else:
                ticket_data = common_data.copy()
                category = message_state.predicted_category if hasattr(message_state, 'predicted_category') else "Unknown"
                ticket_data["subject"] = f"{table_name.capitalize()}: {category}"
                ticket_data["description"] = message_state.message
                self._create_hubspot_ticket(access_token, ticket_data)
                
        except Exception as e:
            error_msg = f"Error sending data to HubSpot: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("HubSpot Error", error_msg, user_id)
            
    def _create_hubspot_contact(self, access_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update a contact in HubSpot"""
        try:
            # HubSpot API endpoint for contacts
            url = "https://api.hubapi.com/crm/v3/objects/contacts"
            
            # Prepare headers with access token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare contact properties
            properties = {
                "phone": data.get("customer_id") or data.get("phone", ""),
                "firstname": data.get("customer_name", "").split(" ")[0] if data.get("customer_name") else "",
                "lastname": " ".join(data.get("customer_name", "").split(" ")[1:]) if data.get("customer_name") and len(data.get("customer_name", "").split(" ")) > 1 else "(No Last Name)",
                "email": data.get("email", ""),
                "whatsapp_id": data.get("customer_id", "")
            }
            
            # Check if contact exists by searching for the phone number
            search_url = f"{url}/search"
            search_payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "phone",
                        "operator": "EQ",
                        "value": properties["phone"]
                    }]
                }]
            }
            
            search_response = requests.post(search_url, headers=headers, json=search_payload)
            search_data = search_response.json()
            
            # If contact exists, update it
            if search_data.get("total", 0) > 0 and search_data.get("results"):
                contact_id = search_data["results"][0]["id"]
                update_url = f"{url}/{contact_id}"
                
                update_payload = {
                    "properties": properties
                }
                
                response = requests.patch(update_url, headers=headers, json=update_payload)
                response_data = response.json()
                
                logger.info(f"Updated HubSpot contact: {contact_id}")
                return response_data
            
            # If contact doesn't exist, create it
            create_payload = {
                "properties": properties
            }
            
            response = requests.post(url, headers=headers, json=create_payload)
            response_data = response.json()
            
            logger.info(f"Created HubSpot contact: {response_data.get('id')}")
            return response_data
            
        except Exception as e:
            error_msg = f"Error creating/updating HubSpot contact: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("HubSpot Error", error_msg, user_id)
            raise
            
    def _create_hubspot_ticket(self, access_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a ticket in HubSpot"""
        try:
            # HubSpot API endpoint for tickets
            url = "https://api.hubapi.com/crm/v3/objects/tickets"
            
            # Prepare headers with access token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Get contact ID
            contact_id = self._get_hubspot_contact_id(access_token, data.get("customer_id"))
            
            # Prepare ticket properties
            properties = {
                "subject": data.get("subject", "WhatsApp Interaction"),
                "content": data.get("description", "") or data.get("message", ""),
                "hs_pipeline": "0",  # Default pipeline
                "hs_pipeline_stage": "1"  # Default stage (New)
            }
            
            # If priority is high, set to high priority
            if data.get("priority") == "high":
                properties["hs_ticket_priority"] = "HIGH"
            
            # Create ticket
            create_payload = {
                "properties": properties
            }
            
            response = requests.post(url, headers=headers, json=create_payload)
            response_data = response.json()
            
            # If contact ID is available, associate ticket with contact
            if contact_id:
                ticket_id = response_data.get("id")
                self._associate_ticket_with_contact(access_token, ticket_id, contact_id)
            
            logger.info(f"Created HubSpot ticket: {response_data.get('id')}")
            return response_data
            
        except Exception as e:
            error_msg = f"Error creating HubSpot ticket: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("HubSpot Error", error_msg, user_id)
            raise
            
    def _get_hubspot_contact_id(self, access_token: str, phone: str) -> Optional[str]:
        """Get HubSpot contact ID by phone number"""
        try:
            # Log token information (safely)
            if access_token:
                token_preview = access_token[:5] + "..." if len(access_token) > 5 else "[empty]"
                logger.info(f"Using HubSpot token: {token_preview}")
            else:
                logger.error("HubSpot access token is empty or None")
                return None
            
            # HubSpot API endpoint for contacts search
            url = "https://api.hubapi.com/crm/v3/objects/contacts/search"
            logger.info(f"Making HubSpot API request to: {url}")
            
            # Prepare headers with access token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Search for contact by phone
            search_payload = {
                "filterGroups": [{
                    "filters": [{
                        "propertyName": "phone",
                        "operator": "EQ",
                        "value": phone
                    }]
                }]
            }
            
            logger.info(f"Searching for contact with phone: {phone}")
            response = requests.post(url, headers=headers, json=search_payload)
            
            # Log response status
            logger.info(f"HubSpot API response status: {response.status_code}")
            
            # Check if response is successful
            if response.status_code == 200:
                data = response.json()
                
                # If contact exists, return ID
                if data.get("total", 0) > 0 and data.get("results"):
                    contact_id = data["results"][0]["id"]
                    logger.info(f"Found HubSpot contact ID: {contact_id}")
                    return contact_id
                else:
                    logger.info(f"No contact found for phone: {phone}")
            else:
                logger.error(f"HubSpot API error: {response.status_code} - {response.text}")
            
            return None
            
        except Exception as e:
            error_msg = f"Error getting HubSpot contact ID: {str(e)}"
            logger.error(error_msg)
            return None
            
    def _associate_ticket_with_contact(self, access_token: str, ticket_id: str, contact_id: str) -> Dict[str, Any]:
        """Associate a ticket with a contact in HubSpot"""
        try:
            # API endpoint for ticket associations
            url = f"https://api.hubapi.com/crm/v3/objects/tickets/{ticket_id}/associations/contacts/{contact_id}/ticket_to_contact"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make the request
            response = requests.put(url, headers=headers)
            
            # Check response
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"Successfully associated ticket {ticket_id} with contact {contact_id}")
                return {"status": "success", "message": "Ticket associated with contact"}
            else:
                error_message = f"Failed to associate ticket with contact: {response.status_code}"
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error associating ticket with contact: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
            
    def _create_hubspot_deal(self, access_token: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in HubSpot as a note on the contact"""
        try:
            # Get contact ID by phone number
            contact_id = self._get_hubspot_contact_id(access_token, data.get("customer_id"))
            
            # If no contact ID was found, log an error and return
            if not contact_id:
                logger.error(f"Contact not found for phone: {data.get('customer_id')}")
                return {"status": "error", "message": "Contact not found"}
                
            # Extract order details
            # Try to get item from products array first
            items = []
            total_quantity = 0
            total_price = 0  # Default price if not specified
            
            if "products" in data and isinstance(data["products"], list) and len(data["products"]) > 0:
                for product in data["products"]:
                    item_name = product.get("item", "")
                    item_quantity = product.get("quantity", 1)
                    item_notes = product.get("notes", "")
                    item_price = product.get("price", 0)  # Default price if not specified
                    
                    if item_name:
                        items.append({
                            "name": item_name,
                            "quantity": item_quantity,
                            "notes": item_notes,
                            "price": item_price
                        })
                        total_quantity += item_quantity
                        total_price += (item_price * item_quantity)
            else:
                # Fall back to other fields
                item_name = data.get("item", data.get("product_type", ""))
                item_quantity = data.get("quantity", 1)
                item_price = data.get("price", 0)  # Default price if not specified
                
                if item_name:
                    items.append({
                        "name": item_name,
                        "quantity": item_quantity,
                        "notes": "",
                        "price": item_price
                    })
                    total_quantity += item_quantity
                    total_price += (item_price * item_quantity)
            
            # Generate a unique order number
            order_number = data.get("order_number", f"ORD-{contact_id}-{int(time.time())}")
            
            # Create order title
            order_title = f"Order #{order_number}: {total_quantity} item(s)"
            
            # Create a formatted list of items for the order description
            items_list = "\n".join([f"- {item['quantity']} x {item['name']}" + 
                                  (f" (Notes: {item['notes']})" if item.get('notes') else "") 
                                  for item in items])
            
            # Create a comprehensive description including all order details
            order_notes = f"Order Details:\n{items_list}\n\n"
            if data.get("delivery_time"):
                order_notes += f"Delivery Time: {data.get('delivery_time')}\n\n"
            if data.get("message"):
                order_notes += f"Original Message:\n{data.get('message')}"
            
            # Create a note on the contact with the order details
            logger.info(f"Creating order note for contact {contact_id}")
            
            # API endpoint for creating notes
            url = "https://api.hubapi.com/crm/v3/objects/notes"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Request body for the note
            note_properties = {
                "hs_note_body": order_notes,
                "hs_timestamp": int(time.time() * 1000)  # Current time in milliseconds
            }
            
            # Create the note
            note_body = {
                "properties": note_properties
            }
            
            # Make the request to create the note
            note_response = requests.post(url, headers=headers, json=note_body)
            
            # Check response
            if note_response.status_code == 201:
                note_data = note_response.json()
                note_id = note_data.get("id")
                logger.info(f"Created note in HubSpot: {note_id}")
                
                # Now associate the note with the contact
                try:
                    # API endpoint for note associations
                    assoc_url = f"https://api.hubapi.com/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/note_to_contact"
                    
                    # Make the request to associate note with contact
                    assoc_response = requests.put(assoc_url, headers=headers)
                    
                    # Check association response
                    if assoc_response.status_code == 200 or assoc_response.status_code == 201:
                        logger.info(f"Successfully associated note {note_id} with contact {contact_id}")
                    else:
                        assoc_error = f"Failed to associate note with contact: {assoc_response.status_code} - {assoc_response.text}"
                        logger.error(assoc_error)
                except Exception as assoc_e:
                    logger.error(f"Error associating note with contact: {str(assoc_e)}")
                
                # Create an engagement for the order (this will show up in the timeline)
                try:
                    # Create an engagement for the order
                    engagement_url = "https://api.hubapi.com/engagements/v1/engagements"
                    
                    engagement_body = {
                        "engagement": {
                            "type": "NOTE",
                            "timestamp": int(time.time() * 1000)
                        },
                        "associations": {
                            "contactIds": [int(contact_id)]
                        },
                        "metadata": {
                            "body": order_notes,
                            "subject": order_title,
                            "status": "COMPLETED"
                        }
                    }
                    
                    # Make the request to create the engagement
                    engagement_response = requests.post(engagement_url, headers=headers, json=engagement_body)
                    
                    # Check engagement response
                    if engagement_response.status_code == 200:
                        engagement_data = engagement_response.json()
                        engagement_id = engagement_data.get("engagement", {}).get("id")
                        logger.info(f"Created engagement in HubSpot: {engagement_id}")
                    else:
                        engagement_error = f"Failed to create engagement: {engagement_response.status_code} - {engagement_response.text}"
                        logger.error(engagement_error)
                except Exception as eng_e:
                    logger.error(f"Error creating engagement: {str(eng_e)}")
                
                return {"status": "success", "message": "Order created in HubSpot as a note", "note_id": note_id}
            else:
                error_message = f"Failed to create note in HubSpot: {note_response.status_code} - {note_response.text}"
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error creating order in HubSpot: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
    
    def _check_hubspot_object_exists(self, access_token: str, object_type: str) -> bool:
        """Check if a specific object type exists in HubSpot"""
        try:
            logger.info(f"Checking if object type '{object_type}' exists in HubSpot...")
            # API endpoint for checking object types
            url = f"https://api.hubapi.com/crm/v3/objects/{object_type}"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make the request to check if the object type exists
            logger.info(f"Making request to: {url}")
            response = requests.get(url, headers=headers, params={"limit": 1})
            
            # Log the response details
            logger.info(f"Response status code: {response.status_code}")
            logger.info(f"Response content: {response.text[:200]}..." if len(response.text) > 200 else f"Response content: {response.text}")
            
            # If we get a 200 response, the object type exists
            if response.status_code == 200:
                logger.info(f"Object type '{object_type}' exists in HubSpot")
                return True
            elif response.status_code == 404 or response.status_code == 400:
                logger.warning(f"Object type '{object_type}' does not exist in HubSpot")
                return False
            elif response.status_code == 403:
                logger.warning(f"No permission to access object type '{object_type}' in HubSpot. Check if the token has the required scopes.")
                return False
            else:
                logger.error(f"Error checking object type '{object_type}': {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking HubSpot object type '{object_type}': {str(e)}")
            return False
    
    def _get_hubspot_order_properties(self, access_token: str) -> List[str]:
        """Get available properties for the Order object in HubSpot"""
        try:
            # API endpoint for getting order properties
            url = "https://api.hubapi.com/crm/v3/properties/order"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make the request to get order properties
            response = requests.get(url, headers=headers)
            
            # Check response
            if response.status_code == 200:
                properties_data = response.json()
                properties = [prop.get("name") for prop in properties_data.get("results", [])]
                logger.info(f"Found {len(properties)} properties for Order object in HubSpot")
                return properties
            else:
                logger.error(f"Failed to get order properties from HubSpot: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting HubSpot order properties: {str(e)}")
            return []
    
    def _create_hubspot_order(self, access_token: str, items: List[Dict[str, Any]], description: str, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in HubSpot using the Orders API with dynamically fetched properties"""
        try:
            # Generate a unique order ID if not provided
            order_number = data.get("order_number", f"ORD-{contact_id}-{int(time.time())}")
            total_quantity = sum(item.get("quantity", 1) for item in items)
            total_price = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
            
            # Create a formatted list of items for the order description
            items_list = "\n".join([f"- {item['quantity']} x {item['name']}" + 
                                  (f" (Notes: {item['notes']})" if item.get('notes') else "") 
                                  for item in items])
            
            # Create a comprehensive description including all order details
            order_notes = f"Order Details:\n{items_list}\n\n"
            if data.get("delivery_time"):
                order_notes += f"Delivery Time: {data.get('delivery_time')}\n\n"
            if data.get("message"):
                order_notes += f"Original Message:\n{data.get('message')}"
            
            logger.info(f"Creating HubSpot order with number: {order_number}")
            
            # First check if the Order object type exists in HubSpot
            order_object_exists = self._check_hubspot_object_exists(access_token, "order")
            
            # If the Order object doesn't exist, fall back to creating a note
            if not order_object_exists:
                logger.warning("Order object type does not exist in HubSpot, falling back to creating a note")
                order_title = f"Order #{order_number}: {total_quantity} item(s)"
                return self._create_hubspot_order_note(access_token, order_title, order_notes, contact_id)
            
            # Get available properties for the Order object
            available_properties = self._get_hubspot_order_properties(access_token)
            
            # If no properties are available, fall back to creating a note
            if not available_properties:
                logger.warning("No properties available for Order object in HubSpot, falling back to creating a note")
                order_title = f"Order #{order_number}: {total_quantity} item(s)"
                return self._create_hubspot_order_note(access_token, order_title, order_notes, contact_id)
            
            # API endpoint for creating orders - use singular 'order' not plural 'orders'
            url = "https://api.hubapi.com/crm/v3/objects/order"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare order properties based on available properties
            properties = {}
            
            # Common property names to try
            property_mappings = {
                "name": ["name", "hs_name", "dealname", "hs_title"],
                "description": ["description", "hs_description", "notes", "hs_notes"],
                "amount": ["amount", "hs_amount", "hs_total_amount", "total_amount"],
                "status": ["status", "hs_status", "hs_order_status", "order_status"],
                "order_number": ["order_number", "hs_order_number", "hs_order_id"],
                "delivery_date": ["delivery_date", "hs_delivery_date", "hs_delivery_time"],
                "created_date": ["createdate", "hs_createdate", "created_at"]
            }
            
            # List of known read-only properties to avoid
            read_only_properties = [
                "hs_createdate", "hs_lastmodifieddate", "hs_object_id", 
                "hs_all_owner_ids", "hs_all_team_ids", "hs_all_accessible_team_ids"
            ]
            
            # Map our data to available properties
            for key, possible_names in property_mappings.items():
                for prop_name in possible_names:
                    # Skip read-only properties
                    if prop_name in read_only_properties:
                        continue
                        
                    if prop_name in available_properties:
                        if key == "name":
                            properties[prop_name] = f"Order #{order_number}"
                        elif key == "description":
                            properties[prop_name] = order_notes
                        elif key == "amount":
                            properties[prop_name] = str(total_price)
                        elif key == "status":
                            properties[prop_name] = "NEW"
                        elif key == "order_number":
                            properties[prop_name] = order_number
                        elif key == "delivery_date" and data.get("delivery_time"):
                            properties[prop_name] = data.get("delivery_time")
                        break
            
            # If we couldn't map any properties, try using known common writable properties
            if not properties:
                # Try using hs_order_name which is often writable
                if "hs_order_name" in available_properties:
                    properties["hs_order_name"] = f"Order #{order_number}: {total_quantity} items"
                # Try using hs_order_note which is often writable
                if "hs_order_note" in available_properties:
                    properties["hs_order_note"] = order_notes
            
            logger.info(f"Using properties for order: {properties}")
                
            # Request body
            body = {
                "properties": properties
            }
            
            # Make the request to create the order
            response = requests.post(url, headers=headers, json=body)
            
            # Check response
            if response.status_code == 201:
                order_data = response.json()
                order_id = order_data.get("id")
                logger.info(f"Created order in HubSpot: {order_id}")
                
                # Now associate the order with the contact
                try:
                    # API endpoint for order associations
                    assoc_url = f"https://api.hubapi.com/crm/v3/objects/order/{order_id}/associations/contacts/{contact_id}/order_to_contact"
                    
                    # Make the request to associate order with contact
                    assoc_response = requests.put(assoc_url, headers=headers)
                    
                    # Check association response
                    if assoc_response.status_code == 200 or assoc_response.status_code == 201:
                        logger.info(f"Successfully associated order {order_id} with contact {contact_id}")
                    else:
                        assoc_error = f"Failed to associate order with contact: {assoc_response.status_code} - {assoc_response.text}"
                        logger.error(assoc_error)
                except Exception as assoc_e:
                    logger.error(f"Error associating order with contact: {str(assoc_e)}")
                
                # Create line items for each product in the order
                line_item_ids = []
                for item in items:
                    line_item_result = self._create_hubspot_order_line_item(access_token, item, order_id, is_order=True)
                    if line_item_result.get("status") == "success":
                        line_item_ids.append(line_item_result.get("line_item_id"))
                
                if line_item_ids:
                    logger.info(f"Created {len(line_item_ids)} line items for order {order_id}")
                else:
                    logger.warning(f"No line items were created for order {order_id}")
                
                return {"status": "success", "message": "Order created in HubSpot", "order_id": order_id, "line_item_ids": line_item_ids}
            else:
                error_message = f"Failed to create order in HubSpot: {response.status_code} - {response.text}"
                logger.error(error_message)
                # Fall back to creating a note
                order_title = f"Order #{order_number}: {total_quantity} item(s)"
                return self._create_hubspot_order_note(access_token, order_title, order_notes, contact_id)
                
        except Exception as e:
            error_message = f"Error creating HubSpot order: {str(e)}"
            logger.error(error_message)
            # Fall back to creating a note
            order_title = f"Order #{order_number}: {total_quantity} item(s)"
            return self._create_hubspot_order_note(access_token, order_title, order_notes, contact_id)
    
    def _create_hubspot_order_as_deal(self, access_token: str, items: List[Dict[str, Any]], description: str, contact_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in HubSpot using a deal with custom properties (fallback method)"""
        try:
            # Generate a unique order ID if not provided
            order_number = data.get("order_number", f"ORD-{contact_id}-{int(time.time())}")
            total_quantity = sum(item.get("quantity", 1) for item in items)
            total_price = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
            
            # Create a formatted list of items for the deal description
            items_list = "\n".join([f"- {item['quantity']} x {item['name']}" + 
                                  (f" (Notes: {item['notes']})" if item.get('notes') else "") 
                                  for item in items])
            
            # Create a comprehensive description including all order details
            full_description = f"Order Number: {order_number}\n\n"
            full_description += f"Items:\n{items_list}\n\n"
            if data.get("delivery_time"):
                full_description += f"Delivery Time: {data.get('delivery_time')}\n\n"
            if data.get("message"):
                full_description += f"Original Message:\n{data.get('message')}"
            
            # Create a deal name that clearly identifies it as an order
            deal_name = f"Order #{order_number}: {total_quantity} items"
            
            logger.info(f"Creating HubSpot order as deal: {deal_name}")
            
            # API endpoint for creating deals
            url = "https://api.hubapi.com/crm/v3/objects/deals"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare deal properties
            properties = {
                "dealname": deal_name,
                "description": full_description,
                "dealstage": "presentationscheduled",  # Initial stage - can be customized
                "pipeline": "default",  # Using default pipeline
                "amount": str(total_price) if total_price > 0 else "0",
                "closedate": str(int(time.time() * 1000))  # Current time in milliseconds
            }
            
            # Request body
            body = {
                "properties": properties
            }
            
            # Make the request to create the deal
            response = requests.post(url, headers=headers, json=body)
            
            # Check response
            if response.status_code == 201:
                deal_data = response.json()
                deal_id = deal_data.get("id")
                logger.info(f"Created order as deal in HubSpot: {deal_id}")
                
                # Now associate the deal with the contact
                try:
                    # API endpoint for deal associations
                    assoc_url = f"https://api.hubapi.com/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/deal_to_contact"
                    
                    # Make the request to associate deal with contact
                    assoc_response = requests.put(assoc_url, headers=headers)
                    
                    # Check association response
                    if assoc_response.status_code == 200 or assoc_response.status_code == 201:
                        logger.info(f"Successfully associated deal {deal_id} with contact {contact_id}")
                    else:
                        assoc_error = f"Failed to associate deal with contact: {assoc_response.status_code} - {assoc_response.text}"
                        logger.error(assoc_error)
                except Exception as assoc_e:
                    logger.error(f"Error associating deal with contact: {str(assoc_e)}")
                
                # Create line items for each product in the order
                line_item_ids = []
                for item in items:
                    line_item_result = self._create_hubspot_order_line_item(access_token, item, deal_id, is_order=False)
                    if line_item_result.get("status") == "success":
                        line_item_ids.append(line_item_result.get("line_item_id"))
                
                if line_item_ids:
                    logger.info(f"Created {len(line_item_ids)} line items for deal {deal_id}")
                else:
                    logger.warning(f"No line items were created for deal {deal_id}")
                
                return {"status": "success", "message": "Order created in HubSpot as a deal", "deal_id": deal_id, "line_item_ids": line_item_ids}
            else:
                error_message = f"Failed to create order as deal in HubSpot: {response.status_code} - {response.text}"
                logger.error(error_message)
                # Final fallback to note
                return self._create_hubspot_order_note(access_token, f"Order #{order_number}", full_description, contact_id)
                
        except Exception as e:
            error_message = f"Error creating HubSpot order as deal: {str(e)}"
            logger.error(error_message)
            # Final fallback to note
            return self._create_hubspot_order_note(access_token, "New Order", description, contact_id)
    
    def _create_hubspot_order_line_item(self, access_token: str, item: Dict[str, Any], parent_id: str, is_order: bool = False) -> Dict[str, Any]:
        """Create a line item in HubSpot and associate it with an order or deal"""
        try:
            item_name = item.get("name", "")
            item_quantity = item.get("quantity", 1)
            item_notes = item.get("notes", "")
            item_price = item.get("price", 0)
            
            parent_type = "order" if is_order else "deal"
            logger.info(f"Creating HubSpot line item for {parent_type}: {item_quantity} x {item_name}")
            
            # API endpoint for creating line items
            url = "https://api.hubapi.com/crm/v3/objects/line_items"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare line item properties
            properties = {
                "name": f"{item_quantity} x {item_name}",
                "quantity": str(item_quantity),
                "price": str(item_price),
                "description": item_notes if item_notes else f"{item_quantity} x {item_name}"
            }
            
            # Request body
            body = {
                "properties": properties
            }
            
            # Make the request to create the line item
            response = requests.post(url, headers=headers, json=body)
            
            # Check response
            if response.status_code == 201:
                line_item_data = response.json()
                line_item_id = line_item_data.get("id")
                logger.info(f"Created line item in HubSpot: {line_item_id}")
                
                # Now associate the line item with the parent (order or deal)
                try:
                    # API endpoint for line item associations - different based on parent type
                    if is_order:
                        assoc_url = f"https://api.hubapi.com/crm/v3/objects/line_items/{line_item_id}/associations/order/{parent_id}/line_item_to_order"
                    else:
                        assoc_url = f"https://api.hubapi.com/crm/v3/objects/line_items/{line_item_id}/associations/deals/{parent_id}/line_item_to_deal"
                    
                    # Make the request to associate line item with parent
                    assoc_response = requests.put(assoc_url, headers=headers)
                    
                    # Check association response
                    if assoc_response.status_code == 200 or assoc_response.status_code == 201:
                        logger.info(f"Successfully associated line item {line_item_id} with {parent_type} {parent_id}")
                    else:
                        assoc_error = f"Failed to associate line item with {parent_type}: {assoc_response.status_code} - {assoc_response.text}"
                        logger.error(assoc_error)
                except Exception as assoc_e:
                    logger.error(f"Error associating line item with {parent_type}: {str(assoc_e)}")
                
                return {"status": "success", "message": "Line item created in HubSpot", "line_item_id": line_item_id}
            else:
                error_message = f"Failed to create line item in HubSpot: {response.status_code} - {response.text}"
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error creating HubSpot line item: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
    
    def _create_hubspot_order_note(self, access_token: str, order_title: str, order_details: str, contact_id: str) -> Dict[str, Any]:
        """Create a note in HubSpot for an order (fallback method)"""
        try:
            # Create a note on the contact with the order details
            logger.info(f"Creating order note for contact {contact_id}")
            
            # API endpoint for creating notes
            url = "https://api.hubapi.com/crm/v3/objects/notes"
            
            # Headers
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Request body for the note
            note_properties = {
                "hs_note_body": order_details,
                "hs_timestamp": int(time.time() * 1000)  # Current time in milliseconds
            }
            
            # Create the note
            note_body = {
                "properties": note_properties
            }
            
            # Make the request to create the note
            note_response = requests.post(url, headers=headers, json=note_body)
            
            # Check response
            if note_response.status_code == 201:
                note_data = note_response.json()
                note_id = note_data.get("id")
                logger.info(f"Created note in HubSpot: {note_id}")
                
                # Now associate the note with the contact
                try:
                    # API endpoint for note associations
                    assoc_url = f"https://api.hubapi.com/crm/v3/objects/notes/{note_id}/associations/contacts/{contact_id}/note_to_contact"
                    
                    # Make the request to associate note with contact
                    assoc_response = requests.put(assoc_url, headers=headers)
                    
                    # Check association response
                    if assoc_response.status_code == 200 or assoc_response.status_code == 201:
                        logger.info(f"Successfully associated note {note_id} with contact {contact_id}")
                    else:
                        assoc_error = f"Failed to associate note with contact: {assoc_response.status_code} - {assoc_response.text}"
                        logger.error(assoc_error)
                except Exception as assoc_e:
                    logger.error(f"Error associating note with contact: {str(assoc_e)}")
                
                # Create an engagement for the order (this will show up in the timeline)
                try:
                    # Create an engagement for the order
                    engagement_url = "https://api.hubapi.com/engagements/v1/engagements"
                    
                    engagement_body = {
                        "engagement": {
                            "type": "NOTE",
                            "timestamp": int(time.time() * 1000)
                        },
                        "associations": {
                            "contactIds": [int(contact_id)]
                        },
                        "metadata": {
                            "body": order_details,
                            "subject": order_title,
                            "status": "COMPLETED"
                        }
                    }
                    
                    # Make the request to create the engagement
                    engagement_response = requests.post(engagement_url, headers=headers, json=engagement_body)
                    
                    # Check engagement response
                    if engagement_response.status_code == 200:
                        engagement_data = engagement_response.json()
                        engagement_id = engagement_data.get("engagement", {}).get("id")
                        logger.info(f"Created engagement in HubSpot: {engagement_id}")
                    else:
                        engagement_error = f"Failed to create engagement: {engagement_response.status_code} - {engagement_response.text}"
                        logger.error(engagement_error)
                except Exception as eng_e:
                    logger.error(f"Error creating engagement: {str(eng_e)}")
                
                return {"status": "success", "message": "Order created in HubSpot as a note", "note_id": note_id}
            else:
                error_message = f"Failed to create note in HubSpot: {note_response.status_code} - {note_response.text}"
                logger.error(error_message)
                return {"status": "error", "message": error_message}
                
        except Exception as e:
            error_message = f"Error creating order note in HubSpot: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
            
    def _store_order(self, data: Dict[str, Any]) -> List[Optional[Order]]:
        """Store order data in the orders table
        
        If multiple products are found, creates separate order entries with the same order number.
        Returns a list of created orders.
        """
        try:
            # Ensure user_id is set correctly
            user_id = int(self.user_id) if self.user_id else None
            if self.user_settings and self.user_settings.user_id:
                user_id = self.user_settings.user_id
            
            # Debug log to see what's in the data
            logger.info(f"Order data: {json.dumps(data, default=str)}")
            
            # Generate a unique order number if not provided
            order_number = data.get("order_number", "")
            if not order_number:
                # Create a timestamp-based order ID with customer prefix
                customer_prefix = data.get("customer_id", "")[:4]
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                order_number = f"ORD-{customer_prefix}-{timestamp}"
            
            # Ensure order_status is a valid value (check constraint issue)
            valid_statuses = ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled"]
            order_status = data.get("status", "pending")
            if order_status not in valid_statuses:
                order_status = "pending"  # Default to pending if invalid status
                
            # Get interaction_id from the message_state if available
            interaction_id = None
            if hasattr(self, 'message_state') and self.message_state:
                # If we have a stored interaction for this message, use its ID
                interaction = self._get_interaction_by_message_id(self.message_state.message_id)
                if interaction:
                    interaction_id = interaction.interaction_id
                    logger.info(f"Linking order to interaction_id: {interaction_id}")
            
            # Find product information
            products = []
            
            # Check for products array directly in the data object
            if "products" in data and isinstance(data["products"], list) and len(data["products"]) > 0:
                logger.info(f"Found products array in data: {json.dumps(data['products'], default=str)}")
                products = data["products"]
            # Check in extracted_info if not found directly
            elif data.get("extracted_info"):
                extracted_info = data.get("extracted_info")
                logger.info(f"Checking extracted info: {json.dumps(extracted_info, default=str)}")
                
                if isinstance(extracted_info, dict):
                    # Check for products array in extracted_info
                    if "products" in extracted_info and isinstance(extracted_info["products"], list) and len(extracted_info["products"]) > 0:
                        logger.info(f"Found products array in extracted_info: {json.dumps(extracted_info['products'], default=str)}")
                        products = extracted_info["products"]
                    else:
                        # Try direct keys in extracted_info
                        logger.info("No products array found in extracted_info, trying direct keys")
                        # Create a single product from direct keys
                        products = [{
                            "item": extracted_info.get("product_type", extracted_info.get("item", "")),
                            "quantity": extracted_info.get("quantity", 1),
                            "notes": extracted_info.get("notes", ""),
                            "unit": extracted_info.get("unit", "")
                        }]
            
            # If no products found, create a default one
            if not products:
                products = [{
                    "item": "",
                    "quantity": 1,
                    "notes": "",
                    "unit": ""
                }]
            
            # Create an order for each product
            created_orders = []
            for product in products:
                # Extract values with detailed logging
                item = product.get("item", "")
                logger.info(f"Extracted item: {item}")
                
                quantity = product.get("quantity", 1)
                logger.info(f"Extracted quantity: {quantity}")
                
                unit = product.get("unit", "")
                logger.info(f"Extracted unit: {unit}")
                
                # Check for details or notes
                notes = product.get("details", product.get("notes", ""))
                logger.info(f"Extracted notes: {notes}")
                
                # Extract delivery information from extracted_info if available
                delivery_address = None
                delivery_time = None
                delivery_method = None
                
                # Check for delivery info in extracted_info
                if data.get("extracted_info") and isinstance(data.get("extracted_info"), dict):
                    extracted_info = data.get("extracted_info")
                    
                    # Extract delivery address
                    if "delivery_address" in extracted_info:
                        delivery_address = extracted_info["delivery_address"]
                        logger.info(f"Extracted delivery address: {delivery_address}")
                    
                    # Extract delivery time
                    if "delivery_time" in extracted_info:
                        delivery_time_str = extracted_info["delivery_time"]
                        # Convert relative time to actual date if needed
                        if delivery_time_str == "tomorrow":
                            tomorrow = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=1)
                            delivery_time = tomorrow.strftime("%Y-%m-%d %H:%M")
                        elif delivery_time_str == "today":
                            today = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
                            delivery_time = today.strftime("%Y-%m-%d %H:%M")
                        else:
                            delivery_time = delivery_time_str
                        logger.info(f"Extracted delivery time: {delivery_time}")
                    
                    # Extract delivery method
                    if "delivery_method" in extracted_info:
                        delivery_method = extracted_info["delivery_method"]
                        logger.info(f"Extracted delivery method: {delivery_method}")
                    elif "delivery_type" in extracted_info:
                        delivery_method = extracted_info["delivery_type"]
                        logger.info(f"Extracted delivery method from type: {delivery_method}")
                    elif delivery_address:  # Default to home delivery if address is provided
                        delivery_method = "home delivery"
                        logger.info(f"Set default delivery method to 'home delivery'")
                
                # Create order with delivery information
                order = Order(
                    user_id=user_id,
                    customer_id=data.get("customer_id"),
                    interaction_id=interaction_id,
                    order_number=order_number,  # Same order number for all products
                    item=item,
                    quantity=quantity,
                    unit=unit,  # Add the unit field
                    notes=notes,
                    order_status=order_status,
                    total_amount=data.get("total_amount", "0"),
                    # Add delivery information
                    delivery_address=delivery_address,
                    delivery_time=delivery_time,
                    delivery_method=delivery_method
                )
            
                self.db.add(order)
                self.db.commit()
                self.db.refresh(order)
                logger.info(f"Stored order {order.order_id} for customer {data.get('customer_id')}")
                created_orders.append(order)
            
            logger.info(f"Created {len(created_orders)} orders with order number {order_number}")
            return created_orders
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error storing order: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            return []  # Return empty list instead of None
            
    def _store_issue(self, data: Dict[str, Any]) -> Optional[Issue]:
        """Store issue data in the issues table"""
        try:
            # Ensure user_id is set correctly
            user_id = int(self.user_id) if self.user_id else None
            if self.user_settings and self.user_settings.user_id:
                user_id = self.user_settings.user_id
                
            # If user_id is still None, we can't create an issue
            if user_id is None:
                raise ValueError("Cannot create issue without a valid user_id")
            
            # Extract issue and request from extracted_info if available
            description = data.get("description", "")
            extracted_info = data.get("extracted_info", {})
            
            if isinstance(extracted_info, dict):
                issue_text = extracted_info.get("issue", "")
                request_text = extracted_info.get("request", "")
                
                if issue_text or request_text:
                    description = f"Issue: {issue_text}\nRequest: {request_text}"
                    logger.info(f"Using extracted issue and request for description: {description}")
            
            # Try to get order_id from interaction if available
            order_id = data.get("order_id")
            if not order_id and hasattr(self, 'message_state') and self.message_state:
                # Get interaction for this message
                interaction = self._get_interaction_by_message_id(self.message_state.message_id)
                if interaction:
                    # Check if there's an order linked to this interaction
                    order = self.db.query(Order).filter(Order.interaction_id == interaction.interaction_id).first()
                    if order:
                        order_id = order.order_id
                        logger.info(f"Found order_id {order_id} from interaction_id {interaction.interaction_id}")
            
            # Try different status values that might be valid based on common patterns
            issue = Issue(
                user_id=user_id,
                customer_id=data.get("customer_id"),
                order_id=order_id,
                description=description,
                issue_type=data.get("category", "other"),
                status="open",  # Use 'open' as a valid status
                priority=data.get("priority", "moderate"),
                resolution_notes=data.get("resolution_notes", "")
            )
            
            self.db.add(issue)
            self.db.commit()
            logger.info(f"Stored issue for customer {data.get('customer_id')}")
            return issue
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error storing issue: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            return None
            
    def _store_enquiry(self, data: Dict[str, Any]) -> Optional[Enquiry]:
        """Store enquiry data in the enquiries table"""
        try:
            # Ensure user_id is set correctly
            user_id = int(self.user_id) if self.user_id else None
            if self.user_settings and self.user_settings.user_id:
                user_id = self.user_settings.user_id
                
            # If user_id is still None, we can't create an enquiry
            if user_id is None:
                raise ValueError("Cannot create enquiry without a valid user_id")
            
            # Extract message from data to use as description if description is not provided
            description = data.get("description", "")
            if not description and data.get("message"):
                description = data.get("message")
            
            # Map priority values to valid ones (high, medium, low)
            priority = data.get("priority", "medium")
            if priority == "moderate":
                priority = "medium"
            elif priority not in ["high", "medium", "low"]:
                priority = "medium"  # Default to medium if not valid
                
            logger.info(f"Using priority '{priority}' for enquiry")
            
            # Use a valid status value based on the check constraint
            # Valid values are: 'open', 'responded', 'converted', 'closed'
            status = "open"  # Default to 'open' as the initial status
            logger.info(f"Using status '{status}' for enquiry")
                
            enquiry = Enquiry(
                user_id=user_id,
                customer_id=data.get("customer_id"),
                description=description,
                category=data.get("category", "other"),
                priority=priority,
                status=status,
                follow_up_date=datetime.fromisoformat(data.get("follow_up_date")) if data.get("follow_up_date") else None
            )
            
            self.db.add(enquiry)
            self.db.commit()
            logger.info(f"Stored enquiry for customer {data.get('customer_id')}")
            return enquiry
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error storing enquiry: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            return None
            
    def _store_feedback(self, data: Dict[str, Any]) -> Optional[Feedback]:
        """Store feedback data in the feedback table"""
        try:
            # Ensure user_id is set correctly
            user_id = int(self.user_id) if self.user_id else None
            if self.user_settings and self.user_settings.user_id:
                user_id = self.user_settings.user_id
                
            # If user_id is still None, we can't create feedback
            if user_id is None:
                raise ValueError("Cannot create feedback without a valid user_id")
            
            # Extract message from data to use as comments if comments is not provided
            comments = data.get("comments", "")
            if not comments and data.get("message"):
                comments = data.get("message")
            
            # Try to get order_id from interaction if available
            order_id = data.get("order_id")
            if not order_id and hasattr(self, 'message_state') and self.message_state:
                # Get interaction for this message
                interaction = self._get_interaction_by_message_id(self.message_state.message_id)
                if interaction:
                    # Check if there's an order linked to this interaction
                    order = self.db.query(Order).filter(Order.interaction_id == interaction.interaction_id).first()
                    if order:
                        order_id = order.order_id
                        logger.info(f"Found order_id {order_id} from interaction_id {interaction.interaction_id}")
                
            feedback = Feedback(
                user_id=user_id,
                customer_id=data.get("customer_id"),
                order_id=order_id,
                rating=data.get("rating", 5),  # Default to 5 stars if not provided
                comments=comments
            )
            
            self.db.add(feedback)
            self.db.commit()
            logger.info(f"Stored feedback for customer {data.get('customer_id')}")
            return feedback
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error storing feedback: {str(e)}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("Database Error", error_msg, user_id)
            return None
            
    # This was a duplicate method that has been removed
            
    def _store_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Store messages in the database"""
        try:
            for msg in messages:
                # Only process messages with required fields
                if "message" not in msg:
                    continue
                
                customer_id = msg.get("customer_id", msg.get("sender"))
                if not customer_id:
                    continue
                
                customer = self._get_or_create_customer(msg)
                
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
            
            return {
                "status": "success",
                "message": f"Processed {processed_count} messages with HubSpot integration",
                "processed_count": processed_count
            }
            
        except Exception as e:
            error_msg = f"Error processing HubSpot integration: {e}"
            logger.error(error_msg)
            user_id = None
            if self.user_settings:
                user_id = self.user_settings.user_id
            self._log_error("HubSpot Error", error_msg, user_id)
            return {"status": "error", "message": error_msg}
    
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

# Static method to get user_id from business_phone_id
def get_user_id_from_business_phone_id(business_phone_id: str) -> Optional[int]:
    """Get the user_id associated with a business_phone_id"""
    try:
        # Create a new database session
        db = SessionLocal()
        
        # Query the UserSettings table to find a user with the matching whatsapp_phone_number_id
        user_settings = db.query(UserSettings).filter(UserSettings.whatsapp_phone_number_id == business_phone_id).first()
        
        if user_settings:
            logger.info(f"Found user_id {user_settings.user_id} for business_phone_id {business_phone_id}")
            return user_settings.user_id
        else:
            logger.warning(f"No user found for business_phone_id {business_phone_id}")
            return None
    except Exception as e:
        logger.error(f"Error getting user_id from business_phone_id: {str(e)}")
        return None
    finally:
        db.close()

# Function to handle incoming messages
def process_whatsapp_messages(user_id: str, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Process WhatsApp messages for a specific user"""
    # If user_id is not provided, try to get it from the first message's business_phone_id
    if not user_id and messages and len(messages) > 0 and "business_phone_id" in messages[0]:
        business_phone_id = messages[0].get("business_phone_id")
        user_id = get_user_id_from_business_phone_id(business_phone_id)
        
        if not user_id:
            return {"status": "error", "message": f"No user found for business_phone_id {business_phone_id}"}
    
    agent = LoggerAgent(user_id)
    result = agent.process_messages(messages)
    return result

# Example usage (for testing)
if __name__ == "__main__":
    # Use the exact message structure provided by the user
    test_message =   {
  "timestamp": "2025-04-27 16:15:03",
  "raw_timestamp_utc": 1745770503,
  "message_id": "wamid.HBgMOTE5NDU0MjAxODk0FQIAEhgUM0E4M0JCMzcxRDgwOTM0NzgzMEYA",
  "message_type": "text",
  "customer_id": "919454201894",
  "sender": "919454201894",
  "customer_name": "Divyansh Nanda",
  "message": "I placed an order but forgot to add a second item. Can you combine them?",
  "predicted_category": "order_status",
  "priority": "moderate",
  "extracted_info": {
    "request": "combine order"
  },
  "conversation_status": "continue",
  "context": [
    "It would be great if you could offer more size options.",
    "I’m extremely happy with the fast service — thank you!",
    "I’ve been charged twice for my order. Can you process a refund?",
    "Is there a physical store where I can try the product before buying?",
    "I’m extremely happy with the fast service — thank you!",
    "I’d like to place an order for 5 additional units. How should I proceed?",
    "Can I modify my order after it’s been placed?",
    "Could you help me apply a discount code retroactively to my order?",
    "Can I pre-order the upcoming product that’s listed on your site?",
    "I placed an order but forgot to add a second item. Can you combine them?"
  ],
  "business_phone_number": "15556454320",
  "business_phone_id": "574048935800997",
  "table_name": "orders"
}

    
    # Get user_id from business_phone_id
    business_phone_id = test_message.get("business_phone_id")
    user_id = get_user_id_from_business_phone_id(business_phone_id)
    
    if user_id:
        logger.info(f"Found user_id {user_id} for business_phone_id {business_phone_id}")
        # Create logger agent with the found user_id
        logger_agent = LoggerAgent(str(user_id))
    else:
        logger.warning(f"No user found for business_phone_id {business_phone_id}")
        # We can't proceed without a valid user_id
        print(json.dumps({"status": "error", "message": f"No user found for business_phone_id {business_phone_id}"}), indent=2)
        # Exit the script instead of using return outside a function
        import sys
        sys.exit(1)
    
    # Process the message
    result = logger_agent.process_messages([test_message])
    
    # Print the result
    print(json.dumps(result, indent=2))
