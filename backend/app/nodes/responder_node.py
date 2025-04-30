"""
Responder Node for the message processing graph.
This node is responsible for sending responses back to WhatsApp.
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.utils.time_utils import convert_relative_time_to_date

from app.agents.responder_agent import ResponderAgent
from database import SessionLocal
from app.models import ResponseMetrics

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store responder agents by user_id
_responder_agents = {}

def get_responder_agent(user_id: Optional[int] = None, user_settings: Optional[Any] = None) -> ResponderAgent:
    """Get or create a responder agent instance
    
    Args:
        user_id: Optional user ID to associate with the agent
        user_settings: Optional user settings to use for the agent
        
    Returns:
        ResponderAgent instance
    """
    global _responder_agents
    
    # Use a default key for None user_id
    key = str(user_id) if user_id is not None else "default"
    
    # Print debug information
    print(f"Getting responder agent for user_id: {user_id}, user_settings: {user_settings}")
    
    # Create a new responder agent if needed for this user
    if key not in _responder_agents:
        print(f"Creating new responder agent for user_id: {user_id}")
        _responder_agents[key] = ResponderAgent(user_id=user_id, user_settings=user_settings)
    
    return _responder_agents[key]

def responder_node(state) -> Dict[str, Any]:
    """
    Process the state and send responses if needed
    
    Args:
        state: The current state of the message processing (MessageState or dict)
        
    Returns:
        Updated state with response information
    """
    logger.info("Processing in responder_node")    
    # Extract information from the state
    sender = None
    business_phone_id = None
    
    try:
        # If it's a MessageState object
        if hasattr(state, 'sender'):
            sender = state.sender
            logger.info(f"Got sender from MessageState attribute: {sender}")
            
            # Try to get business_phone_id
            if hasattr(state, 'business_phone_id'):
                business_phone_id = state.business_phone_id
            elif hasattr(state, 'whatsapp_phone_number_id'):
                business_phone_id = state.whatsapp_phone_number_id
                
        # If it has a dict method (Pydantic model)
        elif hasattr(state, 'dict'):
            state_dict = state.dict()
            sender = state_dict.get('sender')
            
            # Try to get business_phone_id
            business_phone_id = state_dict.get('business_phone_id')
            if not business_phone_id:
                business_phone_id = state_dict.get('whatsapp_phone_number_id')
                
            logger.info(f"Got sender from state.dict(): {sender}")
            sender = state.get('sender')
            
            # Try to get business_phone_id
            business_phone_id = state.get('business_phone_id')
            if not business_phone_id:
                business_phone_id = state.get('whatsapp_phone_number_id')
                
            logger.info(f"Got sender from dictionary: {sender}")
        else:
            logger.warning("Could not find sender in state")
    except Exception as e:
        logger.error(f"Error extracting information from state: {str(e)}")
    
    # If we couldn't get a sender, we can't send a response
    if not sender:
        logger.error("No sender found, cannot send WhatsApp response")
        return state
    
    # Log the extracted information
    logger.info(f"Extracted business_phone_id: {business_phone_id}")
    
    # Get user_id from business_phone_id
    user_id = None
    whatsapp_phone_number_id = business_phone_id
    
    if business_phone_id:
        try:
            # Import the function from storage_node
            from app.nodes.storage_node import get_user_id_from_business_phone_id
            
            # Get user_id
            user_id = get_user_id_from_business_phone_id(business_phone_id)
            logger.info(f"Got user_id {user_id} from business_phone_id {business_phone_id}")
        except Exception as e:
            logger.error(f"Error getting user_id from business_phone_id: {str(e)}")
    
    # Get user settings from database if we have a user_id
    user_settings = None
    if user_id:
        try:
            # Import the correct database module
            from database import SessionLocal
            from app.models import UserSettings
            
            # Get database session
            db = SessionLocal()
            
            # Get user settings from UserSettings table
            settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
            if settings:
                user_settings = settings
                logger.info(f"Found user settings for user_id: {user_id}")
            else:
                logger.warning(f"No user settings found for user_id: {user_id}")
            
            # Close the session
            db.close()
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
    
    # If we have a phone_number_id but no user_id, create a minimal user_settings object
    if not user_settings and whatsapp_phone_number_id:
        # Create a simple object with just the phone_number_id
        from types import SimpleNamespace
        user_settings = SimpleNamespace()
        user_settings.whatsapp_phone_number_id = whatsapp_phone_number_id
        logger.info(f"Created minimal user_settings with phone_number_id: {whatsapp_phone_number_id}")
    
    # Send an appropriate response based on the message type and content
    try:
        # Initialize a responder agent with the user_id and user_settings
        responder_agent = ResponderAgent(user_id=user_id, user_settings=user_settings)
        
        # Get message_id and message_received_at for metrics
        message_id = None
        message_received_at = None
        message_type = None
        customer_id = None
        
        if hasattr(state, 'message_id'):
            message_id = state.message_id
        elif isinstance(state, dict) and 'message_id' in state:
            message_id = state['message_id']
            
        if hasattr(state, 'timestamp'):
            message_received_at = state.timestamp
        elif isinstance(state, dict) and 'timestamp' in state:
            message_received_at = state['timestamp']
            
        if hasattr(state, 'message_type'):
            message_type = state.message_type
        elif isinstance(state, dict) and 'message_type' in state:
            message_type = state['message_type']
            
        if hasattr(state, 'customer_id'):
            customer_id = state.customer_id
        elif isinstance(state, dict) and 'customer_id' in state:
            customer_id = state['customer_id']
            
        # Convert timestamp to datetime if it's a string
        if message_received_at and isinstance(message_received_at, str):
            try:
                message_received_at = datetime.strptime(message_received_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    # Try another common format
                    message_received_at = datetime.strptime(message_received_at, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    # If we can't parse it, use current time
                    message_received_at = datetime.now()
        
        # Start timing the response
        response_start_time = time.time()
        
        # Check for table_name which can also indicate message type
        table_name = None
        if hasattr(state, 'table_name'):
            table_name = state.table_name
        elif hasattr(state, 'dict') and 'table_name' in state.dict():
            table_name = state.dict()['table_name']
        elif isinstance(state, dict) and 'table_name' in state:
            table_name = state['table_name']
            
        # Check if we should respond - only respond when table_name is present
        should_respond = table_name is not None
        
        # Override with explicit should_respond flag if present
        if hasattr(state, 'should_respond'):
            should_respond = state.should_respond
        elif isinstance(state, dict) and 'should_respond' in state:
            should_respond = state['should_respond']
        
        # If we shouldn't respond, return early
        if not should_respond:
            logger.info("should_respond is False, skipping response")
            return state
        
        # Extract response information from the state
        order_data = None
        response_type = None
        response_message = None
        # Note: table_name was already extracted above when determining should_respond, don't reset it
        
        # Determine the appropriate response based on the response_type, message_type, or table_name
        if table_name == "orders":
            # If message_type is order or table_name is orders but we don't have order_data or response_type,
            # create a simple order confirmation
            logger.info(f"Message type is order or table_name is orders, sending simple order confirmation. Message type: {message_type}, Table name: {table_name}")
            
            # Create a basic order data structure
            simple_order_data = {
                "order_number": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "customer_name": "Valued Customer",
                "item": "your order",
                "quantity": 1,
                "unit": "",  # Add unit field for measurements
                "total_amount": "as quoted",
                # Initialize delivery fields
                "delivery_address": None,
                "delivery_time": None,
                "delivery_method": None
            }
            
            # Try to extract customer name if available
            if hasattr(state, 'customer_name'):
                simple_order_data['customer_name'] = state.customer_name
            elif hasattr(state, 'dict') and 'customer_name' in state.dict():
                simple_order_data['customer_name'] = state.dict()['customer_name']
            elif isinstance(state, dict) and 'customer_name' in state:
                simple_order_data['customer_name'] = state['customer_name']
                
            # Extract delivery information from extracted_info if available
            extracted_info = None
            if hasattr(state, 'extracted_info'):
                extracted_info = state.extracted_info
            elif hasattr(state, 'dict') and 'extracted_info' in state.dict():
                extracted_info = state.dict()['extracted_info']
            elif isinstance(state, dict) and 'extracted_info' in state:
                extracted_info = state['extracted_info']
                
            if extracted_info and isinstance(extracted_info, dict):
                # Extract delivery address
                if 'delivery_address' in extracted_info:
                    simple_order_data['delivery_address'] = extracted_info['delivery_address']
                    logger.info(f"Added delivery address to order data: {extracted_info['delivery_address']}")
                
                # Extract delivery time
                if 'delivery_time' in extracted_info:
                    delivery_time_str = extracted_info['delivery_time']
                    # Convert relative time to actual date using shared utility function
                    simple_order_data['delivery_time'] = convert_relative_time_to_date(delivery_time_str)
                    logger.info(f"Added delivery time to order data: {simple_order_data['delivery_time']}")
                
                # Extract delivery method
                if 'delivery_method' in extracted_info:
                    simple_order_data['delivery_method'] = extracted_info['delivery_method']
                    logger.info(f"Added delivery method to order data: {extracted_info['delivery_method']}")
                elif 'delivery_type' in extracted_info:
                    simple_order_data['delivery_method'] = extracted_info['delivery_type']
                    logger.info(f"Added delivery method from type to order data: {extracted_info['delivery_type']}")
                elif simple_order_data['delivery_address']:  # Default to home delivery if address is provided
                    simple_order_data['delivery_method'] = "home delivery"
                    logger.info("Set default delivery method to 'home delivery'")
            
            # Try to extract item details from the message
            if hasattr(state, 'message'):
                message_text = state.message
                logger.info(f"Extracting item from message: {message_text}")
                
                # Look for common item indicators in the message
                item_indicators = ['order', 'buy', 'purchase', 'get', 'need', 'want']
                for indicator in item_indicators:
                    if indicator in message_text.lower():
                        # Extract text after the indicator
                        parts = message_text.lower().split(indicator, 1)
                        if len(parts) > 1 and parts[1].strip():
                            # Take the first 30 chars after the indicator as the item
                            item_text = parts[1].strip()[:30]
                            if item_text:
                                simple_order_data['item'] = item_text
                                logger.info(f"Extracted item from message: {item_text}")
                                break
            
            # Try to extract more details from extracted_info if available
            if hasattr(state, 'extracted_info'):
                extracted_info = state.extracted_info
                if extracted_info and isinstance(extracted_info, dict):
                    # Check for various possible field names for product/item
                    for field in ['product_type', 'item', 'product', 'order_item']:
                        if field in extracted_info and extracted_info[field]:
                            simple_order_data['item'] = extracted_info[field]
                            logger.info(f"Extracted item from extracted_info.{field}: {extracted_info[field]}")
                            break
                    
                    # Check for quantity
                    if 'quantity' in extracted_info and extracted_info['quantity']:
                        simple_order_data['quantity'] = extracted_info['quantity']
                        logger.info(f"Extracted quantity: {extracted_info['quantity']}")
                    
                    # Check for unit
                    if 'unit' in extracted_info and extracted_info['unit']:
                        simple_order_data['unit'] = extracted_info['unit']
                        logger.info(f"Extracted unit: {extracted_info['unit']}")
            
            response = responder_agent.send_order_confirmation(sender, simple_order_data)
            logger.info(f"Sent simple order confirmation to {sender}: {response}")
        elif table_name == "issues":
            # Send an issue acknowledgement
            logger.info("Table name is issues, sending issue acknowledgement")
            
            # Create basic issue data
            issue_data = {
                "issue_id": f"ISS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "customer_name": "Valued Customer",
                "issue_type": "customer issue",
                "priority": "normal"
            }
            
            # Try to extract more details if available
            if hasattr(state, 'extracted_info'):
                extracted_info = state.extracted_info
                if extracted_info and isinstance(extracted_info, dict):
                    if 'issue_type' in extracted_info:
                        issue_data['issue_type'] = extracted_info['issue_type']
                    if 'priority' in extracted_info:
                        issue_data['priority'] = extracted_info['priority']
            
            # Generate the issue acknowledgement message
            from app.utils.message_generator import generate_issue_acknowledgement
            issue_message = generate_issue_acknowledgement(issue_data)
            
            response = responder_agent.send_message(sender, issue_message)
            logger.info(f"Sent issue acknowledgement to {sender}: {response}")
        elif table_name == "enquiries":
            # Send an enquiry response
            logger.info("Table name is enquiries, sending enquiry response")
            
            # Create basic enquiry data
            enquiry_data = {
                "customer_name": "Valued Customer",
                "category": "general"
            }
            
            # Generate the enquiry response message
            from app.utils.message_generator import generate_enquiry_response
            enquiry_message = generate_enquiry_response(enquiry_data)
            
            response = responder_agent.send_message(sender, enquiry_message)
            logger.info(f"Sent enquiry response to {sender}: {response}")
        elif table_name == "feedback":
            # Send a feedback acknowledgement
            logger.info("Table name is feedback, sending feedback acknowledgement")
            
            # Create basic feedback acknowledgement message
            feedback_message = "Thank you for your feedback! We appreciate your input and will use it to improve our services."
            
            response = responder_agent.send_message(sender, feedback_message)
            logger.info(f"Sent feedback acknowledgement to {sender}: {response}")
        elif table_name is None:
            # Only send a generic message if table_name is None (not a recognized message type)
            message = "Thank you for your message! We've received it and will process it shortly."
            logger.info(f"No specific table_name, sending generic confirmation to {sender}")
            response = responder_agent.send_message(sender, message)
            logger.info(f"Sent WhatsApp response to {sender}: {response}")
        else:
            # For any other table_name, don't send a response
            logger.info(f"Unhandled table_name: {table_name}, not sending a generic response")
            response = {"status": "skipped", "reason": f"Unhandled table_name: {table_name}"}
        
        # Calculate response time
        response_end_time = time.time()
        response_time_seconds = response_end_time - response_start_time
        response_sent_at = datetime.now()
        
        # Create a response status dictionary
        if isinstance(response, dict) and response.get("status") == "skipped":
            response_status = {
                "status": "skipped",
                "message": "Response skipped",
                "reason": response.get("reason", "Unknown reason"),
                "response_time_seconds": response_time_seconds
            }
        else:
            response_status = {
                "status": "success",
                "message": "Sent WhatsApp response",
                "details": response,
                "response_time_seconds": response_time_seconds
            }
        
        # Try to update the state with the response status
        try:
            if isinstance(state, dict):
                state["response_status"] = response_status
            elif hasattr(state, '__dict__'):
                state.__dict__["response_status"] = response_status
        except Exception as e:
            logger.error(f"Could not update state with response status: {str(e)}")
            
        # Store response metrics in the database
        try:
            # Determine response type
            response_type = "generic"
            if table_name == "orders":
                response_type = "order_confirmation"
            elif table_name == "issues":
                response_type = "issue_acknowledgement"
            elif table_name == "enquiries":
                response_type = "enquiry_response"
            elif table_name == "feedback":
                response_type = "feedback_acknowledgement"
            elif isinstance(response, dict) and response.get("status") == "skipped":
                response_type = "skipped"
            
            # Create a database session
            db = SessionLocal()
            
            # Create a new ResponseMetrics record
            metrics = ResponseMetrics(
                user_id=user_id,
                message_id=message_id,
                customer_id=customer_id,
                message_type=message_type,
                response_type=response_type,
                response_time_seconds=response_time_seconds,
                message_received_at=message_received_at,
                response_sent_at=response_sent_at
            )
            
            # Only store metrics if we actually sent a response
            if response_type != "skipped":
                # Add and commit the record
                db.add(metrics)
                db.commit()
                logger.info(f"Stored response metrics: response_time={response_time_seconds:.2f}s, type={response_type}")
            else:
                logger.info(f"Skipped storing metrics for skipped response")
            
            # Close the database session
            db.close()
        except Exception as e:
            logger.error(f"Error storing response metrics: {str(e)}")
    except Exception as e:
        logger.error(f"Error sending WhatsApp response: {str(e)}")
    
    # Return the original state to maintain the flow
    return state
