from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    clerk_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with UserSettings
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    customers = relationship("Customer", back_populates="user")
    interactions = relationship("Interaction", back_populates="user")
    orders = relationship("Order", back_populates="user")
    issues = relationship("Issue", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    enquiries = relationship("Enquiry", back_populates="user")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic user info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    
    # Business info
    business_name = Column(String, nullable=True)
    business_description = Column(Text, nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    business_address = Column(String, nullable=True)
    business_website = Column(String, nullable=True)
    business_type = Column(String, nullable=True)
    business_tags = Column(String, nullable=True)  # Store as JSON string
    founded_year = Column(String, nullable=True)
    
    # Categories for message classification
    categories = Column(String, nullable=True)  # Store as JSON string or comma-separated
    
    # WhatsApp Cloud API settings
    whatsapp_app_id = Column(String, nullable=True)
    whatsapp_app_secret = Column(String, nullable=True)
    whatsapp_phone_number_id = Column(String, nullable=True)
    whatsapp_verify_token = Column(String, nullable=True)
    whatsapp_api_key = Column(String, nullable=True)
    
    # CRM Integration settings
    crm_type = Column(String, nullable=True)
    hubspot_access_token = Column(String, nullable=True)
    other_crm_details = Column(Text, nullable=True)
    
    # Dashboard settings
    view_consolidated_data = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with User model
    user = relationship("User", back_populates="settings")



class Customer(Base):
    __tablename__ = "customers"
    customer_id = Column(String(20), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_name = Column(String(100))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    orders = relationship("Order", back_populates="customer")
    feedbacks = relationship("Feedback", back_populates="customer")
    enquiries = relationship("Enquiry", back_populates="customer")
    interactions = relationship("Interaction", back_populates="customer")
    user = relationship("User", back_populates="customers")

class Business(Base):
    __tablename__ = "businesses"
    business_id = Column(Integer, primary_key=True, autoincrement=True)
    business_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = relationship("BusinessTag", back_populates="business")

class BusinessTag(Base):
    __tablename__ = "business_tags"
    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    business_type_id = Column(Integer, ForeignKey('businesses.business_id'))
    tag = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    business = relationship("Business", back_populates="tags")

class Interaction(Base):
    __tablename__ = "interaction_logs"
    interaction_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_message_id = Column(String(100), unique=True)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    timestamp = Column(DateTime)
    message_type = Column(String(20))
    category = Column(String(20))
    priority = Column(String(10))
    status = Column(String(20))
    sentiment = Column(String(10))
    message_summary = Column(String(200))
    response_time = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer = relationship("Customer", back_populates="interactions")
    user = relationship("User", back_populates="interactions")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    interaction_id = Column(Integer, nullable=True)
    order_number = Column(String(50))
    item = Column(String(100))
    quantity = Column(Integer)
    notes = Column(String(200))
    order_status = Column(String(20))
    total_amount = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer = relationship("Customer", back_populates="orders")
    feedbacks = relationship("Feedback", back_populates="order")
    user = relationship("User", back_populates="orders")

class Issue(Base):
    __tablename__ = "issues"
    issue_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=True)
    description = Column(String(200))
    issue_type = Column(String(20))  # Using issue_type instead of category
    status = Column(String(20))
    priority = Column(String(10))
    resolution_notes = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="issues")

class Feedback(Base):
    __tablename__ = "feedback"
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    rating = Column(Integer)
    comments = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer = relationship("Customer", back_populates="feedbacks")
    order = relationship("Order", back_populates="feedbacks")
    user = relationship("User", back_populates="feedbacks")

class Enquiry(Base):
    __tablename__ = "enquiries"
    enquiry_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    customer_id = Column(String(20), ForeignKey('customers.customer_id'))
    description = Column(String(200))
    category = Column(String(20))
    priority = Column(String(10))
    status = Column(String(20))
    follow_up_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    customer = relationship("Customer", back_populates="enquiries")
    user = relationship("User", back_populates="enquiries")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

class ErrorLog(Base):
    __tablename__ = "error_logs"
    error_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with User model (optional)
    user = relationship("User", backref="error_logs")
