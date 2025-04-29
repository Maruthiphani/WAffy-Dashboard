from typing import Dict, Any, Optional, List
from datetime import datetime

def generate_order_confirmation(order_data: Dict[str, Any]) -> str:
    """Generate a confirmation message for an order"""
    order_number = order_data.get("order_number", "N/A")
    item = order_data.get("item", "your items")
    quantity = order_data.get("quantity", 1)
    unit = order_data.get("unit", "")
    total_amount = order_data.get("total_amount", "N/A")
    customer_name = order_data.get("customer_name", "Valued Customer")
    
    # Get delivery information
    delivery_address = order_data.get("delivery_address", "")
    delivery_time = order_data.get("delivery_time", "")
    delivery_method = order_data.get("delivery_method", "")
    
    # Format quantity with unit if available
    quantity_text = f"{quantity} {unit}" if unit else str(quantity)
    
    # Build the basic message
    message = f"""Hello {customer_name},

Thank you for your order! 🎉

*Order Details:*
📋 Order Number: *{order_number}*
🛍️ Item: *{item}*
🔢 Quantity: *{quantity_text}*
💰 Total Amount: *{total_amount}*"""
    
    # Add delivery information if available
    if delivery_address or delivery_time or delivery_method:
        message += "\n\n*Delivery Information:*"
        
        if delivery_method:
            message += f"\n🚚 Delivery Method: *{delivery_method}*"
            
        if delivery_address:
            message += f"\n📍 Delivery Address: *{delivery_address}*"
            
        if delivery_time:
            message += f"\n🕒 Delivery Time: *{delivery_time}*"
    
    # Add closing message
    message += "\n\nYour order has been confirmed and is being processed. We'll send you an update when it ships.\n\nThank you for choosing our service!"""
    
    return message

def generate_order_status_update(order_data: Dict[str, Any], status: str) -> str:
    """Generate a status update message for an order"""
    order_number = order_data.get("order_number", "N/A")
    customer_name = order_data.get("customer_name", "Valued Customer")
    item = order_data.get("item", "your items")
    
    status_emoji = {
        "processing": "⚙️",
        "shipped": "🚚",
        "delivered": "✅",
        "cancelled": "❌",
        "delayed": "⏰"
    }.get(status.lower(), "📦")
    
    status_messages = {
        "processing": "Your order is now being processed. We'll update you when it ships.",
        "shipped": "Your order has been shipped! It's on the way to you.",
        "delivered": "Your order has been delivered. We hope you enjoy it!",
        "cancelled": "Your order has been cancelled as requested.",
        "delayed": "We're sorry, but your order has been delayed. We're working to resolve this as quickly as possible."
    }
    
    status_message = status_messages.get(status.lower(), f"Your order status has been updated to: {status}")
    
    message = f"""Hello {customer_name},

{status_emoji} *Order Status Update* {status_emoji}

Order Number: *{order_number}*
Item: *{item}*
Status: *{status.upper()}*

{status_message}

If you have any questions, please reply to this message.

Thank you for your business!"""
    
    return message

def generate_enquiry_response(enquiry_data: Dict[str, Any], response_text: str) -> str:
    """Generate a response to a customer enquiry"""
    customer_name = enquiry_data.get("customer_name", "Valued Customer")
    enquiry_topic = enquiry_data.get("topic", "your enquiry")
    
    message = f"""Hello {customer_name},

Thank you for your enquiry about *{enquiry_topic}*.

{response_text}

Please let us know if you have any other questions!

Best regards,
Your Business Team"""
    
    return message

def generate_issue_acknowledgement(issue_data: Dict[str, Any]) -> str:
    """Generate an acknowledgement message for a reported issue"""
    issue_id = issue_data.get("issue_id", "N/A")
    issue_type = issue_data.get("issue_type", "issue")
    customer_name = issue_data.get("customer_name", "Valued Customer")
    priority = issue_data.get("priority", "normal").lower()
    
    priority_message = ""
    if priority == "high":
        priority_message = "We understand this is urgent and will prioritize accordingly."
    elif priority == "medium":
        priority_message = "We'll address this as soon as possible."
    else:
        priority_message = "We'll look into this and get back to you."
    
    message = f"""Hello {customer_name},

Thank you for reporting this {issue_type}. We're sorry for any inconvenience caused.

*Issue Reference:* #{issue_id}

{priority_message}

Our support team has been notified and will investigate. We'll update you on our progress.

Thank you for your patience."""
    
    return message

def generate_welcome_message(customer_data: Dict[str, Any]) -> str:
    """Generate a welcome message for a new customer"""
    customer_name = customer_data.get("customer_name", "there")
    business_name = customer_data.get("business_name", "our business")
    
    message = f"""Hello {customer_name}! 👋

Welcome to {business_name}! We're excited to have you with us.

You can use this WhatsApp channel to:
• Place orders
• Ask questions
• Report issues
• Check order status

How can we help you today?"""
    
    return message

def generate_product_catalog_message(products: List[Dict[str, Any]]) -> str:
    """Generate a message showing available products from the catalog"""
    if not products:
        return "Sorry, we don't have any products available at the moment."
    
    products_text = ""
    for i, product in enumerate(products[:10], 1):  # Limit to 10 products to avoid message size limits
        name = product.get("name", "Unknown Product")
        price = product.get("price", "N/A")
        unit = product.get("unit", "")
        unit_text = f" per {unit}" if unit else ""
        
        products_text += f"{i}. *{name}* - ${price}{unit_text}\n"
    
    if len(products) > 10:
        products_text += f"\n...and {len(products) - 10} more products."
    
    message = f"""*Our Product Catalog*

Here are our available products:

{products_text}

To order, simply send a message with the product name and quantity you'd like."""
    
    return message

def generate_issue_response(issue_data: Dict[str, Any]) -> str:
    """Generate a response message for an issue"""
    issue_type = issue_data.get("issue_type", "issue")
    priority = issue_data.get("priority", "medium")
    
    # Estimate response time based on priority
    response_time = "24 hours"
    if priority == "high":
        response_time = "4 hours"
    elif priority == "medium":
        response_time = "12 hours"
    
    message = f"""Thank you for bringing this {issue_type} to our attention.

We've received your report and have created a support ticket. Our team will investigate this matter and get back to you within {response_time}.

If you have any additional information to share, please reply to this message.

We appreciate your patience!"""
    
    return message

def generate_enquiry_response(enquiry_data: Dict[str, Any]) -> str:
    """Generate a response message for an enquiry"""
    category = enquiry_data.get("category", "enquiry")
    
    message = f"""Thank you for your {category} enquiry.

We've received your message and our team is working on providing you with the most accurate information. We'll get back to you as soon as possible.

In the meantime, you can check our website for more information or browse our FAQ section.

Thank you for your interest in our services!"""
    
    return message

def generate_feedback_acknowledgment(feedback_data: Dict[str, Any]) -> str:
    """Generate an acknowledgment message for feedback"""
    rating = feedback_data.get("rating", 0)
    
    if rating >= 4:
        message = """Thank you for your positive feedback!

We're delighted to hear that you had a great experience with our service. Your satisfaction is our top priority, and we're committed to maintaining the high standards you've come to expect from us.

We look forward to serving you again soon!"""
    else:
        message = """Thank you for your feedback.

We appreciate you taking the time to share your experience with us. We're sorry to hear that it didn't meet your expectations. Your feedback is valuable to us and will help us improve our services.

A member of our team will reach out to you shortly to address your concerns and find a solution that works for you."""
    
    return message

def generate_general_response(customer_name: Optional[str] = None) -> str:
    """Generate a general response message"""
    greeting = "Hello"
    if customer_name:
        greeting = f"Hello {customer_name}"
    
    message = f"""{greeting},

Thank you for contacting us. We've received your message and will get back to you as soon as possible.

Our business hours are Monday to Friday, 9 AM to 6 PM. If you've reached out to us outside of these hours, we'll respond on the next business day.

Thank you for your patience!"""
    
    return message
