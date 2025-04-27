# app/constants/category_map.py

DEFAULT_CATEGORIES = [
    "new_order", "order_status", "general_inquiry", "complaint", "return_refund",
    "follow_up", "feedback", "greetings", "others"
]

SUGGESTED_BY_TYPE = {
    "bakery": ["pickup_time", "customization_request", "dietary_preference"],
    "clinic": ["appointment_booking", "reschedule_appointment", "symptoms", "insurance_query"],
    "electronics": ["product_issue", "technical_support", "warranty_claim"],
    "stationery": ["bulk_order_request", "product_availability", "delivery_time_query"],
    "tiffin_service": ["new_subscription", "pause_service", "meal_customization", "address_update", "delivery_issue", "billing_query"],
    "salon": ["appointment_booking", "stylist_request", "package_inquiry", "service_feedback"],
    "fitness_center": ["membership_inquiry", "class_schedule", "trainer_availability", "payment_query"]
}

DEFAULT_PRIORITY_MAP = {
    "new_order": "high", "order_status": "moderate", "general_inquiry": "moderate",
    "complaint": "high", "return_refund": "high", "follow_up": "moderate", "feedback": "low", "others": "low",
    "pickup_time": "high", "customization_request": "high", "dietary_preference": "high",
    "appointment_booking": "high", "reschedule_appointment": "high", "symptoms": "moderate", "insurance_query": "low",
    "product_issue": "moderate", "technical_support": "high", "warranty_claim": "moderate",
    "bulk_order_request": "high", "product_availability": "moderate", "delivery_time_query": "moderate",
    "new_subscription": "high", "pause_service": "moderate", "meal_customization": "moderate",
    "address_update": "moderate", "delivery_issue": "high", "billing_query": "moderate",
    "stylist_request": "moderate", "package_inquiry": "moderate", "service_feedback": "low",
    "membership_inquiry": "moderate", "class_schedule": "moderate", "trainer_availability": "moderate", "payment_query": "moderate"
}

STANDARD_KEYS = {
    "products": "List of ordered items. Each item can have: item, quantity, details",
    "delivery_method": "pickup or delivery",
    "delivery_address": "Full address string for delivery",
    "pickup_time": "Pickup time if customer plans to collect",
    "delivery_time": "Requested delivery time",
    "notes": "Any custom instructions (e.g., 'no nuts', 'wrap nicely', 'style', 'source', 'design')",
    "payment_status": "e.g., paid, unpaid, advance required",
    "issue": "Description of problem (e.g., 'damaged item')",
    "request": "Special request or action expected (e.g., 'refund', 'replacement')",
    "appointment_time": "For services like clinic/salon, booking time",
    "contact_info": "Phone/email provided for follow-up",
}

# app/utils/table_mapper.py

# These are known fixed categories
CATEGORY_TO_TABLE = {
    "new_order": "orders",
    "order_status": "orders",
    "complaint": "issues",
    "return_refund": "issues",
    "follow_up": "issues",
    "feedback": "feedback",
    "general_inquiry": "enquiries",
}

# Define irrelevant categories separately (greetings, thanks, etc.)
IGNORED_CATEGORIES = {"greetings", "thanks", "small_talk", "chitchat"}

def map_category_to_table(category: str) -> str | None:
    category = category.lower().strip()

    if category in IGNORED_CATEGORIES:
        return None 

    if category in CATEGORY_TO_TABLE:
        return CATEGORY_TO_TABLE[category] 

    return "enquiries" #user created categories

