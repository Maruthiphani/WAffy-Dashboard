from typing import Dict, Any, Optional
from datetime import datetime

def generate_order_confirmation(order_data: Dict[str, Any]) -> str:
    """Generate a confirmation message for an order"""
    order_number = order_data.get("order_number", "N/A")
    item = order_data.get("item", "your items")
    quantity = order_data.get("quantity", 1)
    total_amount = order_data.get("total_amount", "N/A")
    
    message = f"""Thank you for your order!

*Order Details:*
Order Number: {order_number}
Item: {item}
Quantity: {quantity}
Total Amount: {total_amount}

Your order has been confirmed and is being processed. We'll send you an update when it ships.

Thank you for choosing our service!"""
    
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
