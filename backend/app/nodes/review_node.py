"""
Review node for processing order data and checking if it should be consolidated with existing orders.
"""

import json
import logging
from typing import Dict, Any
from app.state import MessageState
from app.agents.review_agent import get_review_agent
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db

logger = logging.getLogger(__name__)

def review_node(state: MessageState, db: Session = Depends(get_db)) -> MessageState:
    """
    Review node that checks if an order should be added to an existing pending order.
    
    This node is inserted between the LLM node and the Storage node to review order data
    before it's stored in the database.
    
    Args:
        state: The current message state
        db: Database session
        
    Returns:
        Updated message state with consolidated order information if applicable
    """
    try:
        # Only process orders
        if state.table_name != "orders":
            logger.info("Not an order, skipping review")
            return state
            
        logger.info(f"Reviewing order data for customer {state.customer_id}")
        
        # Get the review agent
        review_agent = get_review_agent(db)
        
        # Prepare data for review
        data = {
            "customer_id": state.customer_id,
            "message": state.message,
            "context": state.context,
            "extracted_info": state.extracted_info,
            "category": state.predicted_category,
            "priority": state.priority
        }
        
        # Review the order data
        reviewed_data = review_agent.review_order(data)
        logger.info(f"Review agent processed order data: {json.dumps(reviewed_data, default=str)}")
        
        # Update state with reviewed data if it's an addition to an existing order
        if reviewed_data.get("is_addition_to_existing_order", False):
            # Set attributes directly on the state object
            try:
                # Set these as direct attributes on the state object
                state.is_addition_to_existing_order = True
                state.order_number = reviewed_data.get("order_number")
                print(f"REVIEW NODE: Setting is_addition_to_existing_order to True directly on state")
                print(f"REVIEW NODE: Setting order_number to '{reviewed_data.get('order_number')}' directly on state")
            except Exception as e:
                print(f"REVIEW NODE: Error setting attributes on state: {e}")
                logger.error(f"Error setting attributes on state: {e}")
            
            # Also add to extracted_info to ensure it's passed to the logger agent
            if not hasattr(state, 'extracted_info') or state.extracted_info is None:
                state.extracted_info = {}
                
            # Make sure extracted_info is a dictionary
            if not isinstance(state.extracted_info, dict):
                state.extracted_info = {}
                
            # Add order_number to extracted_info
            state.extracted_info["order_number"] = reviewed_data.get("order_number")
            state.extracted_info["is_addition_to_existing_order"] = True
            
            # These are now set above in the try block
            
            # Log that we're adding to an existing order
            logger.info(f"Adding to existing order {reviewed_data.get('order_number')}")
            
            # If there was delivery info in the original order, preserve it
            if "delivery_address" in reviewed_data:
                # Set directly on state if possible
                try:
                    state.delivery_address = reviewed_data.get("delivery_address")
                    print(f"REVIEW NODE: Setting delivery_address directly on state")
                except Exception as e:
                    print(f"REVIEW NODE: Could not set delivery_address on state: {e}")
                # Always set in extracted_info
                state.extracted_info["delivery_address"] = reviewed_data.get("delivery_address")
                
            if "delivery_time" in reviewed_data:
                # Set directly on state if possible
                try:
                    state.delivery_time = reviewed_data.get("delivery_time")
                    print(f"REVIEW NODE: Setting delivery_time directly on state")
                except Exception as e:
                    print(f"REVIEW NODE: Could not set delivery_time on state: {e}")
                # Always set in extracted_info
                state.extracted_info["delivery_time"] = reviewed_data.get("delivery_time")
                
            if "delivery_method" in reviewed_data:
                # Set directly on state if possible
                try:
                    state.delivery_method = reviewed_data.get("delivery_method")
                    print(f"REVIEW NODE: Setting delivery_method directly on state")
                except Exception as e:
                    print(f"REVIEW NODE: Could not set delivery_method on state: {e}")
                # Always set in extracted_info
                state.extracted_info["delivery_method"] = reviewed_data.get("delivery_method")
        
        return state
        
    except Exception as e:
        logger.error(f"Error in review_node: {str(e)}")
        # Don't modify state if there's an error
        return state
