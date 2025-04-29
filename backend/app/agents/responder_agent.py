"""
Responder Agent for sending messages back to WhatsApp.
This agent handles sending responses back to WhatsApp using the WhatsApp Business API.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.utils.message_generator import (
    generate_order_confirmation,
    # Import other message generators as needed
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResponderAgent:
    """Agent responsible for sending messages back to WhatsApp"""
    
    def __init__(self, user_id: Optional[int] = None, user_settings: Optional[Any] = None):
        """Initialize the responder agent with user settings"""
        self.user_id = user_id
        self.user_settings = user_settings
        # Get WhatsApp API credentials from user settings or environment
        if user_settings and hasattr(user_settings, 'whatsapp_api_key') and user_settings.whatsapp_api_key:
            try:
                from utils.encryption import decrypt_value
                self.api_key = decrypt_value(user_settings.whatsapp_api_key)
                logger.info(f"Successfully decrypted WhatsApp API key for user {user_id}")
            except Exception as e:
                logger.error(f"Error decrypting WhatsApp API key: {str(e)}")
                # Fall back to environment variables for API key
                self.api_key = os.environ.get('WHATSAPP_API_KEY')
                print(f"Using environment variable for API key")
        else:
            # Use environment variable for API key
            self.api_key = os.environ.get('WHATSAPP_API_KEY')
        
        if user_settings and hasattr(user_settings, 'whatsapp_phone_number_id'):
            if isinstance(user_settings.whatsapp_phone_number_id, str) and not user_settings.whatsapp_phone_number_id.startswith('gAAAAAB'):
                self.phone_number_id = user_settings.whatsapp_phone_number_id
            else:
                try:
                    self.phone_number_id = user_settings.whatsapp_phone_number_id
                except Exception as e:
                    logger.error(f"Error decrypting phone number ID: {str(e)}")
                    self.phone_number_id = user_settings.whatsapp_phone_number_id
                    print(f"Using phone number ID directly: {self.phone_number_id}")
        else:
            self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
            print(f"Using environment variable for phone number ID: {self.phone_number_id}")
        
        if self.api_key and self.phone_number_id:
            logger.info("WhatsApp credentials configured successfully")
        else:
            missing = []
            if not self.api_key:
                missing.append("API key")
            if not self.phone_number_id:
                missing.append("phone number ID")
            logger.error(f"WhatsApp credentials incomplete: missing {', '.join(missing)}")
        
        # WhatsApp API base URL
        self.api_base_url = "https://graph.facebook.com/v18.0"
    
    def send_message(self, to_phone: str, message_text: str) -> Dict[str, Any]:
        """
        Send a text message to a WhatsApp number
        
        Args:
            to_phone: The recipient's phone number in international format without +
            message_text: The text message to send
            
        Returns:
            Dict with status and response details
        """
        if not self.api_key or not self.phone_number_id:
            error_msg = "WhatsApp API credentials not configured"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Format the phone number (remove + if present)
        if to_phone.startswith('+'):
            to_phone = to_phone[1:]
        
        # Prepare the message payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {
                "body": message_text
            }
        }
        
        # API endpoint for sending messages
        url = f"{self.api_base_url}/{self.phone_number_id}/messages"
        
        try:
            # Send the request to WhatsApp API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            # Log the response for debugging
            logger.info(f"WhatsApp API response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get("messages", [{}])[0].get("id", "unknown")
                return {
                    "status": "success", 
                    "message": "Message sent successfully",
                    "message_id": message_id,
                    "response": response_data
                }
            else:
                error_msg = f"Failed to send WhatsApp message: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending WhatsApp message: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def send_order_confirmation(self, to_phone: str, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send an order confirmation message to a customer
        
        Args:
            to_phone: The customer's phone number
            order_data: Dictionary containing order details
            
        Returns:
            Dict with status and response details
        """
        # Generate the order confirmation message using the template
        message_text = generate_order_confirmation(order_data)
        
        # Send the message
        return self.send_message(to_phone, message_text)
    
    def send_template_message(self, to_phone: str, template_name: str, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a template message to a WhatsApp number
        
        Args:
            to_phone: The recipient's phone number in international format without +
            template_name: The name of the template to use
            components: List of template components (header, body, buttons)
            
        Returns:
            Dict with status and response details
        """
        if not self.api_key or not self.phone_number_id:
            error_msg = "WhatsApp API credentials not configured"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Format the phone number (remove + if present)
        if to_phone.startswith('+'):
            to_phone = to_phone[1:]
        
        # Prepare the template message payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": "en_US"
                },
                "components": components
            }
        }
        
        # API endpoint for sending messages
        url = f"{self.api_base_url}/{self.phone_number_id}/messages"
        
        try:
            # Send the request to WhatsApp API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            # Log the response for debugging
            logger.info(f"WhatsApp API template response: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data.get("messages", [{}])[0].get("id", "unknown")
                return {
                    "status": "success", 
                    "message": "Template message sent successfully",
                    "message_id": message_id,
                    "response": response_data
                }
            else:
                error_msg = f"Failed to send WhatsApp template message: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Error sending WhatsApp template message: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
