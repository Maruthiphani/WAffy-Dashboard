-- WAffy initial schema migration

-- Customers table
CREATE TABLE Customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Businesses table
CREATE TABLE Businesses (
    business_phone_number VARCHAR(20) PRIMARY KEY,
    business_phone_id VARCHAR(50),
    business_name VARCHAR(100),
    business_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Business_Tags (
    tag_id SERIAL PRIMARY KEY,
    business_type VARCHAR(50),
    tag VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Interactions table
CREATE TABLE Interaction_Logs (
    interaction_id SERIAL PRIMARY KEY,
    whatsapp_message_id VARCHAR(100) UNIQUE,
    customer_id VARCHAR(20) REFERENCES Customers(customer_id),
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
CREATE TABLE Orders (
    order_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES Customers(customer_id),
    order_number VARCHAR(50),
    item VARCHAR(100),
    quantity INTEGER,
    notes VARCHAR(200),
    order_status VARCHAR(20) CHECK (order_status IN ('pending', 'confirmed', 'shipped', 'delivered', 'booked', 'completed', 'canceled')),
    total_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issues table
CREATE TABLE Issues (
    issue_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES Customers(customer_id),
    order_id INTEGER REFERENCES Orders(order_id),
    issue_type VARCHAR(20), --Ex ('complaint', 'return_refund', 'follow_up'),
    description VARCHAR(200),
    status VARCHAR(20) CHECK (status IN ('open', 'in_progress', 'resolved')),
    priority VARCHAR(10) CHECK (priority IN ('high', 'medium', 'low')),
    resolution_notes VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE Feedback (
    feedback_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES Customers(customer_id),
    order_id INTEGER REFERENCES Orders(order_id),
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comments VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Store everything else under the Enquiries table?
CREATE TABLE Enquiries (
    enquiry_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(20) REFERENCES Customers(customer_id),
    description VARCHAR(200),
    category VARCHAR(20),
    priority VARCHAR(10) CHECK (priority IN ('high', 'medium', 'low')),
    status VARCHAR(20) CHECK (status IN ('open', 'responded', 'converted', 'closed')),
    follow_up_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tags table
CREATE TABLE Categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

