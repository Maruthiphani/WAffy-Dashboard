# app/nodes/storage_node.py

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.agents.logger_agent import LoggerAgent, get_user_id_from_business_phone_id
from app.state import MessageState
from pydantic import BaseModel
from app.utils.time_utils import convert_relative_time_to_date

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function moved to app.utils.time_utils

def storage_node(state: MessageState) -> MessageState:
    try:
        business_phone_id = state.business_phone_id

        user_id = get_user_id_from_business_phone_id(business_phone_id)
        
        if user_id:
            logger_agent = LoggerAgent(str(user_id))
        else:
            logger_agent = LoggerAgent("4")  # Default user ID

        # Create a dictionary from the state but preserve special attributes
        state_dict = state.dict()
        
        # Check if this is an addition to an existing order (from review agent)
        if hasattr(state, 'is_addition_to_existing_order') and state.is_addition_to_existing_order:
            state_dict['is_addition_to_existing_order'] = True
            print(f"STORAGE NODE: Found is_addition_to_existing_order flag on state")
            
        if hasattr(state, 'order_number') and state.order_number:
            state_dict['order_number'] = state.order_number
            print(f"STORAGE NODE: Found order_number on state: {state.order_number}")
            
        # Pass the state with preserved attributes to the logger agent
        result = logger_agent.process_messages([state_dict])
        logger.info(f"Logger agent result: {json.dumps(result, default=str)}")
        
        # Check if the logger agent created new data and set it on the state
        if result and result.get('status') == 'success':
            # Process table-specific data directly from the result
            if 'table' in result:
                table_name = result.get('table')
                print(f"STORAGE NODE: Processing data for table: {table_name}")
                
                # Handle orders
                if table_name == 'orders' and 'orders' in result:
                    orders = result.get('orders', [])
                    if orders and len(orders) > 0:
                        # Get the order number from the first order
                        new_order_number = orders[0].get('order_number')
                        if new_order_number:
                            # Set the order number on the state object
                            state.order_number = new_order_number
                            print(f"STORAGE NODE: Setting order_number on state: {new_order_number}")
                            logger.info(f"Setting order_number on state: {new_order_number}")
                
                # Handle issues
                elif table_name == 'issues' and 'issue' in result:
                    issue = result.get('issue')
                    if issue and issue.get('issue_id'):
                        # Set the issue ID on the state object
                        state.issue_id = issue.get('issue_id')
                        print(f"STORAGE NODE: Setting issue_id on state: {issue.get('issue_id')}")
                        logger.info(f"Setting issue_id on state: {issue.get('issue_id')}")
                
                # Handle enquiries
                elif table_name == 'enquiries' and 'enquiry' in result:
                    enquiry = result.get('enquiry')
                    if enquiry and enquiry.get('enquiry_id'):
                        # Set the enquiry ID on the state object
                        state.enquiry_id = enquiry.get('enquiry_id')
                        print(f"STORAGE NODE: Setting enquiry_id on state: {enquiry.get('enquiry_id')}")
                        logger.info(f"Setting enquiry_id on state: {enquiry.get('enquiry_id')}")
                
                # Handle feedback
                elif table_name == 'feedback' and 'feedback' in result:
                    feedback = result.get('feedback')
                    if feedback and feedback.get('feedback_id'):
                        # Set the feedback ID on the state object
                        state.feedback_id = feedback.get('feedback_id')
                        print(f"STORAGE NODE: Setting feedback_id on state: {feedback.get('feedback_id')}")
                        logger.info(f"Setting feedback_id on state: {feedback.get('feedback_id')}")
            
            # Also check in the results array for backward compatibility
            elif result.get('results'):
                for result_item in result.get('results', []):
                    if isinstance(result_item, dict) and 'table' in result_item:
                        table_name = result_item.get('table')
                        print(f"STORAGE NODE: Processing data for table from results array: {table_name}")
                        
                        # Handle orders
                        if table_name == 'orders' and 'orders' in result_item:
                            orders = result_item.get('orders', [])
                            if orders and len(orders) > 0:
                                # Get the order number from the first order
                                new_order_number = orders[0].get('order_number')
                                if new_order_number:
                                    # Set the order number on the state object
                                    state.order_number = new_order_number
                                    print(f"STORAGE NODE: Setting order_number on state from results array: {new_order_number}")
                                    logger.info(f"Setting order_number on state from results array: {new_order_number}")
        
        # Get message type and data
        message_type = state.message_type if hasattr(state, 'message_type') else state.get('message_type', '')
        message_data = state.dict() if hasattr(state, 'dict') else state
        
        # Check if this is an addition to an existing order (from review agent)
        is_addition_to_existing_order = False
        order_number = None
        
        if hasattr(state, 'metadata') and state.metadata:
            if 'is_addition_to_existing_order' in state.metadata:
                is_addition_to_existing_order = state.metadata['is_addition_to_existing_order']
                logger.info(f"Review agent identified this as an addition to an existing order")
                
            if 'order_number' in state.metadata:
                order_number = state.metadata['order_number']
                logger.info(f"Using order number from review agent: {order_number}")
        
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
                # Initialize order_data
                order_data = {}
                
                # Check if data is a list of orders or a dictionary
                if isinstance(first_result.get("data"), list) and len(first_result["data"]) > 0:
                    # It's a list of Order objects
                    created_orders = first_result["data"]
                    logger.info(f"Found {len(created_orders)} orders in result")
                    
                    # Get the first order for order number and other details
                    first_order = created_orders[0]
                    
                    # Extract order details from the first order
                    if hasattr(first_order, 'order_number') and first_order.order_number:
                        order_data['order_number'] = first_order.order_number
                        logger.info(f"Using order number from created order: {first_order.order_number}")
                        
                    if hasattr(first_order, 'customer_id') and first_order.customer_id:
                        order_data['customer_id'] = first_order.customer_id
                        
                    # Get all items from all orders with the same order number
                    items = []
                    for order in created_orders:
                        if hasattr(order, 'item') and order.item:
                            items.append({
                                'item': order.item,
                                'quantity': order.quantity if hasattr(order, 'quantity') else 1,
                                'unit': order.unit if hasattr(order, 'unit') else '',
                                'notes': order.notes if hasattr(order, 'notes') else ''
                            })
                    
                    if items:
                        order_data['products'] = items
                        logger.info(f"Added {len(items)} products to order data")
                else:
                    # It's a dictionary with order details
                    order_data = first_result.get("data", {})
                    logger.info(f"Extracted order_data: {json.dumps(order_data, default=str)}")
                
                # If this is an addition to an existing order, update the order data
                if is_addition_to_existing_order and order_number:
                    # Always use the order number from the review agent for consistency
                    order_data['order_number'] = order_number
                    order_data['is_addition_to_existing_order'] = True
                    logger.info(f"Updated order data with existing order number: {order_number}")
                
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
