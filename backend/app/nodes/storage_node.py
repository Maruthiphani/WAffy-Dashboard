# app/nodes/storage_node.py

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re

from app.agents.logger_agent import LoggerAgent, get_user_id_from_business_phone_id
from app.state import MessageState
from pydantic import BaseModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_relative_time_to_date(time_str):
    """
    Convert relative time expressions like 'tomorrow', 'next week', etc. to actual dates
    
    Args:
        time_str: String containing relative time expression
        
    Returns:
        Formatted date string in the format 'YYYY-MM-DD HH:MM' or the original string if no conversion possible
    """
    now = datetime.now()
    time_str = time_str.lower().strip()
    
    # Handle common relative time expressions
    if time_str == 'today':
        return now.strftime('%Y-%m-%d %H:%M')
    elif time_str == 'tomorrow':
        return (now + timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
    elif time_str == 'day after tomorrow':
        return (now + timedelta(days=2)).strftime('%Y-%m-%d %H:%M')
    elif 'next week' in time_str:
        return (now + timedelta(days=7)).strftime('%Y-%m-%d %H:%M')
    elif 'next month' in time_str:
        # Approximate next month as 30 days
        return (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M')
    
    # Handle 'in X days/hours/minutes'
    in_match = re.search(r'in (\d+) (day|days|hour|hours|minute|minutes)', time_str)
    if in_match:
        amount = int(in_match.group(1))
        unit = in_match.group(2)
        
        if 'day' in unit:
            return (now + timedelta(days=amount)).strftime('%Y-%m-%d %H:%M')
        elif 'hour' in unit:
            return (now + timedelta(hours=amount)).strftime('%Y-%m-%d %H:%M')
        elif 'minute' in unit:
            return (now + timedelta(minutes=amount)).strftime('%Y-%m-%d %H:%M')
    
    # Handle specific time today (e.g., '5pm', '17:00')
    time_match = re.search(r'(\d{1,2})(:|\s)?(\d{2})?(\s)?(am|pm)?', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(3) or 0)
        ampm = time_match.group(5)
        
        if ampm == 'pm' and hour < 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0
            
        today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        return today.strftime('%Y-%m-%d %H:%M')
    
    # If no conversion was possible, return the original string
    return time_str

def storage_node(state: MessageState) -> MessageState:
    try:
        business_phone_id = state.business_phone_id

        user_id = get_user_id_from_business_phone_id(business_phone_id)
        
        if user_id:
            logger_agent = LoggerAgent(str(user_id))
        else:
            logger_agent = LoggerAgent("4")  # Default user ID

        result = logger_agent.process_messages([state.dict()])
        logger.info(f"Logger agent result: {json.dumps(result, default=str)}")
        
        # Get message type and data
        message_type = state.message_type if hasattr(state, 'message_type') else state.get('message_type', '')
        message_data = state.dict() if hasattr(state, 'dict') else state
        
        # Always respond for now
        # We need to modify the state but can't add attributes to MessageState
        # So we'll return a dictionary with all the original state plus our additions
        try:
            # Convert state to dictionary if it's a MessageState object
            if hasattr(state, 'dict'):
                state_dict = state.dict()
                logger.info(f"Converted MessageState to dictionary with keys: {list(state_dict.keys())}")
            else:
                # If it's already a dictionary or something else, use it directly
                state_dict = dict(state) if isinstance(state, dict) else {}
                
            # Set should_respond flag
            state_dict["should_respond"] = True
            
            # Add user_id to the state if we have it
            if user_id:
                state_dict["user_id"] = user_id
                logger.info(f"Added user_id {user_id} to state")
            
            if business_phone_id and "business_phone_id" not in state_dict:
                state_dict["business_phone_id"] = business_phone_id
                state_dict["whatsapp_phone_number_id"] = business_phone_id
                logger.info(f"Added business_phone_id {business_phone_id} to state")
            

            state = state_dict
        except Exception as e:
            logger.error(f"Error setting should_respond: {str(e)}")
            if hasattr(state, 'sender'):
                state = {"sender": state.sender, "should_respond": True}
                if user_id:
                    state["user_id"] = user_id
                if business_phone_id:
                    state["business_phone_id"] = business_phone_id
                    state["whatsapp_phone_number_id"] = business_phone_id
            else:
                state = {"should_respond": True}
        
        # Check if extracted_info exists in the state
        extracted_info = None
        if hasattr(state, 'extracted_info'):
            extracted_info = state.extracted_info
        elif isinstance(state, dict) and 'extracted_info' in state:
            extracted_info = state['extracted_info']
        
        # Process delivery information if it exists in extracted_info
        delivery_info = {}
        if extracted_info and isinstance(extracted_info, dict):
            # Extract delivery address
            if 'delivery_address' in extracted_info:
                delivery_info['delivery_address'] = extracted_info['delivery_address']
                logger.info(f"Extracted delivery address: {delivery_info['delivery_address']}")
            
            # Extract and process delivery time
            if 'delivery_time' in extracted_info:
                delivery_time_str = extracted_info['delivery_time']
                delivery_date = convert_relative_time_to_date(delivery_time_str)
                delivery_info['delivery_time'] = delivery_date
                logger.info(f"Converted delivery time '{delivery_time_str}' to: {delivery_date}")
            
            # Extract delivery method if available
            if 'delivery_method' in extracted_info:
                delivery_info['delivery_method'] = extracted_info['delivery_method']
                logger.info(f"Extracted delivery method: {delivery_info['delivery_method']}")
            elif 'delivery_type' in extracted_info:
                delivery_info['delivery_method'] = extracted_info['delivery_type']
                logger.info(f"Extracted delivery method from type: {delivery_info['delivery_method']}")
            else:
                # Default to home delivery if address is provided
                if 'delivery_address' in delivery_info:
                    delivery_info['delivery_method'] = 'home delivery'
                    logger.info("Set default delivery method to 'home delivery'")
            
            # Store delivery info in state for later use
            state['delivery_info'] = delivery_info
        
        # Check if this is an order message
        if message_type == "order" and result and isinstance(result, list) and len(result) > 0:
            # Get the first result (there might be multiple for batch processing)
            first_result = result[0]
            logger.info(f"Order processing result: {json.dumps(first_result, default=str)}")
            
            # If we successfully processed an order, send a confirmation
            if first_result.get("status") == "success" and first_result.get("type") == "order":
                order_data = first_result.get("data", {})
                logger.info(f"Extracted order_data: {json.dumps(order_data, default=str)}")
                
                if order_data:
                    # Add delivery information to order data if available
                    if delivery_info:
                        for key, value in delivery_info.items():
                            order_data[key] = value
                        logger.info(f"Added delivery info to order data: {json.dumps(delivery_info, default=str)}")
                    
                    # Extract product information if available in extracted_info
                    if extracted_info and 'products' in extracted_info and extracted_info['products']:
                        products = extracted_info['products']
                        if isinstance(products, list) and len(products) > 0:
                            first_product = products[0]
                            if 'item' in first_product:
                                order_data['item'] = first_product['item']
                            if 'quantity' in first_product:
                                order_data['quantity'] = first_product['quantity']
                            if 'unit' in first_product:
                                order_data['unit'] = first_product['unit']
                            if 'details' in first_product and first_product['details']:
                                order_data['notes'] = first_product['details']
                            logger.info(f"Added product info to order data: {json.dumps(first_product, default=str)}")
                    
                    # Set up the response
                    state["should_respond"] = True
                    state["response_type"] = "order_confirmation"
                    state["order_data"] = order_data
                    
                    # Include customer name if available
                    if "customer" in first_result and "customer_name" in first_result["customer"]:
                        state["order_data"]["customer_name"] = first_result["customer"]["customer_name"]
                        logger.info(f"Added customer_name to order_data: {first_result['customer']['customer_name']}")
                    
                    logger.info(f"Will send order confirmation for order: {order_data.get('order_number')}")
                    logger.info(f"Final state for responder: response_type={state.get('response_type')}, order_data={json.dumps(state.get('order_data'), default=str)}")
        
        # Check if this is an issue message
        elif message_type == "issue" and result and isinstance(result, list) and len(result) > 0:
            first_result = result[0]
            
            # If we successfully processed an issue, send an acknowledgement
            if first_result.get("status") == "success" and first_result.get("type") == "issue":
                issue_data = first_result.get("data", {})
                
                if issue_data:
                    # Set up the response
                    state["should_respond"] = True
                    state["response_type"] = "custom_message"
                    
                    # Generate the issue acknowledgement message
                    from app.utils.message_generator import generate_issue_acknowledgement
                    state["response_message"] = generate_issue_acknowledgement(issue_data)
                    
                    logger.info(f"Will send issue acknowledgement for issue: {issue_data.get('issue_id')}")
        
        # Check if this is a first-time message from a new customer
        elif message_type == "enquiry" and "is_new_customer" in message_data and message_data["is_new_customer"]:
            # Send a welcome message to new customers
            customer_data = {}
            
            if "customer" in message_data:
                customer_data = message_data["customer"]
            
            # Set up the response
            state["should_respond"] = True
            state["response_type"] = "custom_message"
            
            # Generate the welcome message
            from app.utils.message_generator import generate_welcome_message
            state["response_message"] = generate_welcome_message(customer_data)
            
            logger.info(f"Will send welcome message to new customer: {customer_data.get('customer_name')}")
            
    except Exception as e:
        logger.error(f"[StorageNode] Failed to process message: {str(e)}")
        # Don't set should_respond in case of errors
        state["should_respond"] = False
    
    return state
