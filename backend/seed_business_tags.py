import os
from app.models import Business, BusinessTag
from database import SessionLocal
from datetime import datetime

# Suggested tags by business type
SUGGESTED_BY_TYPE = {
    "bakery": ["pickup_time", "customization_request", "dietary_preference"],
    "clinic": ["appointment_booking", "reschedule_appointment", "symptoms", "insurance_query"],
    "electronics": ["product_issue", "technical_support", "warranty_claim"],
    "stationery": ["bulk_order_request", "product_availability", "delivery_time_query"],
    "tiffin_service": ["new_subscription", "pause_service", "meal_customization", "address_update", "delivery_issue", "billing_query"],
    "salon": ["appointment_booking", "stylist_request", "package_inquiry", "service_feedback"],
    "fitness_center": ["membership_inquiry", "class_schedule", "trainer_availability", "payment_query"]
}

# Create a database session
session = SessionLocal()

def seed_business_and_tags():
    for business_type, tags in SUGGESTED_BY_TYPE.items():
        # Create a business record if not exists
        business = session.query(Business).filter_by(business_type=business_type).first()
        if not business:
            business = Business(
                business_type=business_type,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(business)
            session.commit()
        # Add tags for this business
        for tag in tags:
            exists = session.query(BusinessTag).filter_by(
                business_type_id=business.business_id,
                tag=tag
            ).first()
            if not exists:
                session.add(BusinessTag(
                    business_type_id=business.business_id,
                    tag=tag,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ))
    session.commit()
    print("Seeded businesses and business tags.")

if __name__ == "__main__":
    seed_business_and_tags()
