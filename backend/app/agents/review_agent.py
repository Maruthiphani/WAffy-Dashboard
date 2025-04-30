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
            print("\n" + "=" * 50)
            print("REVIEW AGENT: Starting review_order process")
            print(f"REVIEW AGENT: Input data: {json.dumps(data, default=str)[:200]}...")
            print("=" * 50)
            
            # Get customer ID
            customer_id = data.get("customer_id")
            print(f"REVIEW AGENT: 🔍 Original customer_id from data: '{customer_id}', Type: {type(customer_id)}")
            
            # Try to clean up the customer_id if it's not in the expected format
            if customer_id and isinstance(customer_id, str):
                # Remove any non-digit characters if it's a phone number
                if customer_id.startswith("+") or customer_id.startswith("91"):
                    cleaned_id = ''.join(c for c in customer_id if c.isdigit())
                    print(f"REVIEW AGENT: 🔍 Cleaned customer_id: '{cleaned_id}'")
                    # Add country code if it's missing
                    if not cleaned_id.startswith("91") and len(cleaned_id) == 10:
                        cleaned_id = "91" + cleaned_id
                        print(f"REVIEW AGENT: 🔍 Added country code: '{cleaned_id}'")
                    customer_id = cleaned_id
            
            if not customer_id:
                print("REVIEW AGENT: ❌ No customer_id found in order data")
                logger.warning("No customer_id found in order data")
                return data
                
            # Get message and context
            message = data.get("message", "")
            context = data.get("context", [])
            
            print(f"REVIEW AGENT: 👤 Customer ID: {customer_id}")
            print(f"REVIEW AGENT: 💬 Message: {message}")
            print(f"REVIEW AGENT: 📜 Context: {context[-2:] if len(context) > 1 else context}")
            
            # Log the current data for debugging
            logger.info(f"Reviewing order for customer {customer_id}")
            logger.info(f"Message: {message}")
            logger.info(f"Context: {context}")
            
            # Check if this is a direct addition to an existing order based on the message
            is_direct_addition = False
            addition_keywords = ["also", "add", "along with", "with this", "as well"]
            for keyword in addition_keywords:
                if keyword in message.lower():
                    is_direct_addition = True
                    print(f"REVIEW AGENT: 🔍 Found addition keyword: '{keyword}'")
                    logger.info(f"Found addition keyword: {keyword}")
                    break
                    
            print(f"REVIEW AGENT: 🔄 Is direct addition based on keywords: {is_direct_addition}")
            
            # Extract products from the current order
            print("REVIEW AGENT: 🔍 Extracting products from order data...")
            current_products = self._extract_products(data)
            if not current_products:
                print("REVIEW AGENT: ❌ No products found in current order")
                logger.warning("No products found in current order")
                return data
            
            # Log the products found
            product_names = [p.get("item", "") for p in current_products if p.get("item")]
            print(f"REVIEW AGENT: 📦 Products found: {', '.join(product_names)}")
            logger.info(f"Products in current order: {', '.join(product_names)}")
            
            # Check if there's a pending order for this customer
            print(f"REVIEW AGENT: 🔍 Checking for pending orders for customer {customer_id}...")
            pending_orders = self._get_pending_orders(customer_id)
            if not pending_orders:
                print("REVIEW AGENT: ❌ No pending orders found for this customer")
                logger.info(f"No pending orders found for customer {customer_id}")
                return data
            
            # Get the most recent pending order
            most_recent_order = pending_orders[0] if pending_orders else None
            if most_recent_order:
                print(f"REVIEW AGENT: ✅ Found pending order: {most_recent_order.order_number}")
                print(f"REVIEW AGENT: 📅 Order created at: {most_recent_order.created_at}")
                logger.info(f"Found pending order: {most_recent_order.order_number} created at {most_recent_order.created_at}")
                
                # Check if the order was created recently (within 30 minutes)
                now = datetime.now()
                order_time = most_recent_order.created_at
                time_diff = now - order_time
                minutes_diff = time_diff.total_seconds() / 60
                print(f"REVIEW AGENT: ⏱️ Time since order creation: {minutes_diff:.2f} minutes")
                
                # If the order is recent or there's a direct addition keyword, add to existing order
                time_recent = time_diff.total_seconds() < 1800  # 30 minutes in seconds
                print(f"REVIEW AGENT: ⏱️ Order is recent (< 30 min): {time_recent}")
                
                if is_direct_addition or time_recent:
                    print(f"REVIEW AGENT: ✅ DECISION: Adding to existing order {most_recent_order.order_number}")
                    print(f"REVIEW AGENT: 📝 Reason: {'Direct addition keyword found' if is_direct_addition else 'Recent order'}")
                    print(f"REVIEW AGENT: 🔄 is_direct_addition={is_direct_addition}, time_recent={time_recent}")
                    logger.info(f"Adding to existing order {most_recent_order.order_number} due to {'direct addition keyword' if is_direct_addition else 'recent order'}")
                    
                    # Update data with existing order number
                    data["order_number"] = most_recent_order.order_number
                    data["is_addition_to_existing_order"] = True
                    print(f"REVIEW AGENT: 🏷️ Setting order_number to '{most_recent_order.order_number}'")
                    print(f"REVIEW AGENT: 🏷️ Setting is_addition_to_existing_order to True")
                    
                    # Log the decision
                    logger.info(f"Consolidated order with existing order {most_recent_order.order_number}")
                    print("REVIEW AGENT: 🔄 Returning updated data with consolidated order information")
                    
                    # If there was delivery info in the original order, preserve it
                    if most_recent_order.delivery_address and not data.get("delivery_address"):
                        data["delivery_address"] = most_recent_order.delivery_address
                        print("REVIEW AGENT: 🏠 Preserving delivery address from existing order")
                        
                    if most_recent_order.delivery_time and not data.get("delivery_time"):
                        data["delivery_time"] = most_recent_order.delivery_time
                        print("REVIEW AGENT: 🕒 Preserving delivery time from existing order")
                        
                    if most_recent_order.delivery_method and not data.get("delivery_method"):
                        data["delivery_method"] = most_recent_order.delivery_method
                        print("REVIEW AGENT: 🚚 Preserving delivery method from existing order")
                else:
                    print("REVIEW AGENT: ❌ DECISION: Creating new order (existing order is too old)")
                    print(f"REVIEW AGENT: ⏱️ Time since last order: {minutes_diff:.2f} minutes (threshold: 30 minutes)")
                    print(f"REVIEW AGENT: 🔄 is_direct_addition={is_direct_addition}, time_recent={time_recent}")
                    print(f"REVIEW AGENT: 💾 NOT adding to existing order {most_recent_order.order_number}")
                    logger.info(f"Creating a new order for these products (existing order is too old)")
            else:
                print("REVIEW AGENT: ❌ DECISION: Creating new order (no pending orders found)")
                print(f"REVIEW AGENT: 💾 No pending orders found for customer {customer_id}")
                print(f"REVIEW AGENT: 💾 Will create a new order with a new order number")
                logger.info(f"Creating a new order for these products (no pending orders found)")
                
            print("REVIEW AGENT: 🔄 Final decision:")
            print(f"REVIEW AGENT: - Order number: {data.get('order_number', 'New order (will be generated)')}") 
            print(f"REVIEW AGENT: - Is addition to existing: {data.get('is_addition_to_existing_order', False)}")
            print("=" * 50)
            
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
            print(f"REVIEW AGENT: 📦 Getting pending orders for customer {customer_id}")
            print(f"REVIEW AGENT: 🔍 Customer ID type: {type(customer_id)}, value: '{customer_id}'")
            # Get the most recent order for this customer
            # Try different approaches to match the customer_id with the database
            customer_id_str = str(customer_id)
            print(f"REVIEW AGENT: 🔍 Using customer_id as string: '{customer_id_str}'")
            
            # Try different query approaches with error handling
            result1 = result2 = result3 = None
            query1 = query2 = query3 = None
            
            try:
                # Try direct comparison with the original customer_id
                query1 = self.db.query(Order).filter(Order.customer_id == customer_id).order_by(desc(Order.created_at))
                result1 = query1.first()
                print(f"REVIEW AGENT: 🔍 Query 1 (original ID): {result1 is not None}")
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error in Query 1: {str(e)}")
            
            try:
                # Try with string casting
                query2 = self.db.query(Order).filter(Order.customer_id == customer_id_str).order_by(desc(Order.created_at))
                result2 = query2.first()
                print(f"REVIEW AGENT: 🔍 Query 2 (string cast): {result2 is not None}")
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error in Query 2: {str(e)}")
            
            try:
                # Try with explicit cast in SQL
                from sqlalchemy import cast, String
                query3 = self.db.query(Order).filter(cast(Order.customer_id, String) == customer_id_str).order_by(desc(Order.created_at))
                result3 = query3.first()
                print(f"REVIEW AGENT: 🔍 Query 3 (SQL cast): {result3 is not None}")
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error in Query 3: {str(e)}")
            
            # Use the query that worked
            if result2 is not None:
                query = query2
                print("REVIEW AGENT: 🔍 Using query 2 (string cast)")
            elif result1 is not None:
                query = query1
                print("REVIEW AGENT: 🔍 Using query 1 (original ID)")
            elif result3 is not None:
                query = query3
                print("REVIEW AGENT: 🔍 Using query 3 (SQL cast)")
            else:
                # Default to query2 if none worked
                query = query2
                print("REVIEW AGENT: 🔍 No queries returned results, defaulting to query 2")
            
            # Print the raw SQL query for debugging
            print(f"REVIEW AGENT: 🔍 Raw SQL query: {query}")
            
            # Check if there are ANY orders for this customer, regardless of status
            try:
                all_orders = self.db.query(Order).filter(Order.customer_id == customer_id_str).all()
                print(f"REVIEW AGENT: 🔍 Found {len(all_orders)} total orders for customer {customer_id_str}")
                if all_orders:
                    print(f"REVIEW AGENT: 🔍 First order: ID={all_orders[0].order_id}, Number={all_orders[0].order_number}, Status={all_orders[0].order_status}")
                    print(f"REVIEW AGENT: 🔍 Customer ID in DB: '{all_orders[0].customer_id}', Type: {type(all_orders[0].customer_id)}")
                else:
                    print(f"REVIEW AGENT: 🔍 No orders found with exact customer ID: '{customer_id_str}'")
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error checking for all orders: {str(e)}")
                
            # Try a LIKE query to find similar customer IDs
            try:
                print("REVIEW AGENT: 🔍 Trying LIKE query to find similar customer IDs...")
                from sqlalchemy import or_
                similar_orders = self.db.query(Order).filter(
                    or_(
                        Order.customer_id.like(f"%{customer_id_str}%"),
                        Order.customer_id.like(f"%{customer_id_str.lstrip('+')}%")  # Try without leading +
                    )
                ).all()
                if similar_orders:
                    print(f"REVIEW AGENT: 🔍 Found {len(similar_orders)} orders with similar customer ID")
                    print(f"REVIEW AGENT: 🔍 Similar customer IDs found: {[order.customer_id for order in similar_orders[:5]]}")
                else:
                    print("REVIEW AGENT: 🔍 No similar customer IDs found")
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error in LIKE query: {str(e)}")
                    
            # Get all customer IDs in the database to see what's available
            try:
                all_customers = self.db.query(Order.customer_id).distinct().limit(10).all()
                print(f"REVIEW AGENT: 🔍 Sample customer IDs in database: {[cid[0] for cid in all_customers]}")
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error getting sample customer IDs: {str(e)}")
            
            try:
                most_recent_order = query.first()

                # Check if most_recent_order exists before trying to access its properties
                if most_recent_order:
                    print(f"REVIEW AGENT: 📦 Most recent order: {most_recent_order.order_number} - {most_recent_order.created_at}")
                    print(f"REVIEW AGENT: 📦 Most recent order status: {most_recent_order.order_status}")
                else:
                    print(f"REVIEW AGENT: ❌ No orders found for customer {customer_id}")
                
                # If no orders or the most recent order is not pending, return empty list
                if not most_recent_order or most_recent_order.order_status != "pending":
                    print(f"REVIEW AGENT: ❌ No pending orders found for customer {customer_id}")
                    return []
            except Exception as e:
                print(f"REVIEW AGENT: ⚠️ Error checking most recent order: {str(e)}")
                return []
            
            # Return the most recent order in a list
            print(f"REVIEW AGENT: ✅ Found pending order {most_recent_order.order_number} for customer {customer_id}")
            print(f"REVIEW AGENT: 📦 Order details: Created={most_recent_order.created_at}, Item={most_recent_order.item}")
            return [most_recent_order]
            
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
