# === Constants ===

# Waffy default categories (used in all businesses)
DEFAULT_CATEGORIES = [
    "new_order",
    "order_status",
    "general_inquiry",
    "complaint",
    "return_refund",
    "follow_up",
    "feedback",
    "others"
]

# Suggested categories by business type
SUGGESTED_BY_TYPE = {
    "bakery": [
        "pickup_time",
        "customization_request",
        "dietary_preference"
    ],
    "clinic": [
        "appointment_booking",
        "reschedule_appointment",
        "symptoms",
        "insurance_query"
    ],
    "electronics": [
        "product_issue",
        "technical_support",
        "warranty_claim"
    ],
    "stationery": [
        "bulk_order_request",
        "product_availability",
        "delivery_time_query"
    ],
    "tiffin_service": [
        "new_subscription",
        "pause_service",
        "meal_customization",
        "address_update",
        "delivery_issue",
        "billing_query"
    ],
    "salon": [
        "appointment_booking",
        "stylist_request",
        "package_inquiry",
        "service_feedback"
    ],
    "fitness_center": [
        "membership_inquiry",
        "class_schedule",
        "trainer_availability",
        "payment_query"
    ]
}

# Priority mapping for default + type-based categories
DEFAULT_PRIORITY_MAP = {
    # === Waffy core ===
    "new_order": "high",
    "order_status": "moderate",
    "general_inquiry": "moderate",
    "complaint": "high",
    "return_refund": "high",
    "follow_up": "moderate",
    "feedback": "low",
    "others": "low",

    # === Bakery ===
    "pickup_time": "moderate",
    "customization_request": "low",
    "dietary_preference": "moderate",

    # === Clinic ===
    "appointment_booking": "high",
    "reschedule_appointment": "moderate",
    "symptoms": "moderate",
    "insurance_query": "low",

    # === Electronics ===
    "product_issue": "moderate",
    "technical_support": "high",
    "warranty_claim": "moderate",

    # === Stationery ===
    "bulk_order_request": "high",
    "product_availability": "moderate",
    "delivery_time_query": "moderate",

    # === Tiffin Service ===
    "new_subscription": "high",
    "pause_service": "moderate",
    "meal_customization": "moderate",
    "address_update": "moderate",
    "delivery_issue": "high",
    "billing_query": "moderate",

    # === Salon ===
    "stylist_request": "moderate",
    "package_inquiry": "moderate",
    "service_feedback": "low",

    # === Fitness Center ===
    "membership_inquiry": "moderate",
    "class_schedule": "moderate",
    "trainer_availability": "moderate",
    "payment_query": "moderate"
}
