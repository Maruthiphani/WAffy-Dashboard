-- WAffy Dashboard - Full Database Schema Migration
-- This file contains the complete database schema for the WAffy Dashboard application

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    clerk_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Settings table
CREATE TABLE user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    -- Basic user info
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    
    -- Business info
    business_name VARCHAR(255),
    business_description TEXT,
    contact_phone VARCHAR(50),
    contact_email VARCHAR(255),
    business_address VARCHAR(255),
    business_website VARCHAR(255),
    business_type VARCHAR(100),
    business_tags VARCHAR(255),
    founded_year VARCHAR(10),
    
    -- Categories for message classification
    categories VARCHAR(1000),
    
    -- WhatsApp Cloud API settings
    whatsapp_app_id VARCHAR(255),
    whatsapp_app_secret VARCHAR(255),
    whatsapp_phone_number_id VARCHAR(100),
    whatsapp_verify_token VARCHAR(255),
    whatsapp_api_key VARCHAR(255),
    
    -- CRM Integration settings
    crm_type VARCHAR(50),
    hubspot_access_token VARCHAR(255),
    other_crm_details TEXT,
    
    -- Dashboard settings
    view_consolidated_data BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Customers table
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    customer_name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Businesses table
CREATE TABLE businesses (
    business_id SERIAL PRIMARY KEY,
    business_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Business Tags table
CREATE TABLE business_tags (
    tag_id SERIAL PRIMARY KEY,
    business_type_id INTEGER REFERENCES businesses(business_id),
    tag VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interaction Logs table
CREATE TABLE interaction_logs (
    interaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    whatsapp_message_id VARCHAR(100) UNIQUE,
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    timestamp TIMESTAMP,
    message_type VARCHAR(20),
    category VARCHAR(20),
    priority VARCHAR(10),
    status VARCHAR(20) CHECK (status IN ('open', 'pending', 'resolved', 'escalated')),
    sentiment VARCHAR(10) CHECK (sentiment IN ('positive', 'neutral', 'negative')),
    message_summary VARCHAR(200),
    response_time INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    interaction_id INTEGER,
    order_number VARCHAR(50),
    item VARCHAR(100),
    quantity INTEGER,
    unit VARCHAR(50),
    notes VARCHAR(200),
    order_status VARCHAR(20),
    total_amount VARCHAR(20),
    delivery_address VARCHAR(255),
    delivery_time VARCHAR(100),
    delivery_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issues table
CREATE TABLE issues (
    issue_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    order_id INTEGER REFERENCES orders(order_id),
    issue_type VARCHAR(20),
    description VARCHAR(200),
    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'resolved')),
    priority VARCHAR(10) CHECK (priority IN ('high', 'medium', 'low')),
    resolution_notes VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    order_id INTEGER REFERENCES orders(order_id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comments VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enquiries table
CREATE TABLE enquiries (
    enquiry_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    customer_id VARCHAR(20) REFERENCES customers(customer_id),
    description VARCHAR(200),
    category VARCHAR(20),
    priority VARCHAR(10) CHECK (priority IN ('high', 'medium', 'low')),
    status VARCHAR(20) CHECK (status IN ('open', 'responded', 'converted', 'closed')),
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Error Logs table
CREATE TABLE error_logs (
    error_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Response Metrics table
CREATE TABLE response_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    total_messages INTEGER DEFAULT 0,
    response_time_avg INTEGER DEFAULT 0,
    response_rate FLOAT DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for frequently queried columns
CREATE INDEX idx_customers_user_id ON customers(user_id);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_issues_user_id ON issues(user_id);
CREATE INDEX idx_enquiries_user_id ON enquiries(user_id);
CREATE INDEX idx_error_logs_user_id ON error_logs(user_id);
CREATE INDEX idx_error_logs_error_type ON error_logs(error_type);
