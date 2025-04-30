# app/agents/review_agent.py

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Order, Customer

logger = logging.getLogger(__name__)

class ReviewAgent:
    """
    Review agent that checks if products from a new order should be added to an existing pending order
    from the same customer.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def review_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review order data and check if it should be consolidated with an existing pending order.
        
        Args:
            data: Order data including customer_id and product information
            
        Returns:
            Updated data with consolidated order information if applicable
        """
        try:
            # Get customer ID
            customer_id = data.get("customer_id")
            if not customer_id:
                logger.warning("No customer_id found in order data")
                return data
                
            # Get message and context
            message = data.get("message", "")
            context = data.get("context", [])
            
            # Log the current data for debugging
            logger.info(f"Reviewing order for customer {customer_id}")
            logger.info(f"Message: {message}")
            logger.info(f"Context: {context}")
            
            # Extract products from the current order
            current_products = self._extract_products(data)
            if not current_products:
                logger.warning("No products found in current order")
                return data
            
            # Log the products found
            product_names = [p.get("item", "") for p in current_products if p.get("item")]
            logger.info(f"Products in current order: {', '.join(product_names)}")
            
            # Check if there's a pending order for this customer
            pending_orders = self._get_pending_orders(customer_id)
            if not pending_orders:
                logger.info(f"No pending orders found for customer {customer_id}")
                return data
            
            # Get the most recent pending order
            most_recent_order = pending_orders[0] if pending_orders else None
            if most_recent_order:
                logger.info(f"Found pending order: {most_recent_order.order_number} created at {most_recent_order.created_at}")
            
            # Check if this is a continuation based on context and message
            is_continuation = self._is_order_continuation(message, current_products, context)
            
            if is_continuation and most_recent_order:
                logger.info(f"This appears to be an addition to existing order {most_recent_order.order_number}")
                
                # Add the existing order number to the data
                data["order_number"] = most_recent_order.order_number
                data["is_addition_to_existing_order"] = True
                
                # Log the products being added
                logger.info(f"Adding products {', '.join(product_names)} to existing order {most_recent_order.order_number}")
                
                # If there was delivery info in the original order, preserve it
                if most_recent_order.delivery_address and not data.get("delivery_address"):
                    data["delivery_address"] = most_recent_order.delivery_address
                    
                if most_recent_order.delivery_time and not data.get("delivery_time"):
                    data["delivery_time"] = most_recent_order.delivery_time
                    
                if most_recent_order.delivery_method and not data.get("delivery_method"):
                    data["delivery_method"] = most_recent_order.delivery_method
            else:
                logger.info(f"Creating a new order for these products")
            
            return data
            
        except Exception as e:
            logger.error(f"Error in review_order: {str(e)}")
            return data
    
    def _extract_products(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract products from order data"""
        products = []
        
        # Check for products array directly in the data object
        if "products" in data and isinstance(data["products"], list) and len(data["products"]) > 0:
            products = data["products"]
        # Check in extracted_info if not found directly
        elif data.get("extracted_info"):
            extracted_info = data.get("extracted_info")
            
            if isinstance(extracted_info, dict):
                # Check for products array in extracted_info
                if "products" in extracted_info and isinstance(extracted_info["products"], list) and len(extracted_info["products"]) > 0:
                    products = extracted_info["products"]
                else:
                    # Try direct keys in extracted_info
                    item = extracted_info.get("product_type", extracted_info.get("item", ""))
                    if item:
                        products = [{
                            "item": item,
                            "quantity": extracted_info.get("quantity", 1),
                            "notes": extracted_info.get("notes", ""),
                            "unit": extracted_info.get("unit", "")
                        }]
        
        return products
    
    def _get_pending_orders(self, customer_id: str) -> List[Order]:
        """Get pending orders for a customer, ordered by most recent first"""
        try:
            # Get distinct order numbers for this customer with status 'pending'
            order_numbers = (
                self.db.query(Order.order_number)
                .filter(Order.customer_id == customer_id)
                .filter(Order.order_status == "pending")
                .distinct()
                .all()
            )
            
            # Get the most recent order for each order number
            recent_orders = []
            for (order_number,) in order_numbers:
                most_recent = (
                    self.db.query(Order)
                    .filter(Order.order_number == order_number)
                    .order_by(desc(Order.created_at))
                    .first()
                )
                if most_recent:
                    recent_orders.append(most_recent)
            
            # Sort by created_at in descending order
            recent_orders.sort(key=lambda x: x.created_at, reverse=True)
            return recent_orders
            
        except Exception as e:
            logger.error(f"Error getting pending orders: {str(e)}")
            return []
    
    def _is_order_continuation(self, message: str, products: List[Dict[str, Any]], context: List[str]) -> bool:
        """
        Determine if the message is a continuation of an existing order conversation.
        
        This checks if the message is asking about a product or adding to an existing order.
        """
        message = message.lower()
        
        # Check if there are explicit keywords indicating this is an addition to an existing order
        addition_keywords = ["also", "add", "along with", "with this", "as well"]
        for keyword in addition_keywords:
            if keyword in message.lower():
                logger.info(f"Found addition keyword: {keyword}")
                return True
                
        # Check if there's context from previous messages
        if context and len(context) > 1:
            # If there are previous messages in the context, it's likely a continuation
            logger.info(f"Found previous messages in context: {len(context)} messages")
            return True
            
        # If we have multiple products in a single message, it's likely a single order
        if len(products) > 1:
            logger.info(f"Found multiple products in a single message: {len(products)} products")
            return False
            
        # By default, return False to create a new order
        return False

# Create a singleton instance
review_agent = None

def get_review_agent(db: Session) -> ReviewAgent:
    """Get or create a ReviewAgent instance"""
    global review_agent
    if review_agent is None:
        review_agent = ReviewAgent(db)
    return review_agent
