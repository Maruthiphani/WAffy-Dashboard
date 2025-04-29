# WAffy Dashboard Architecture

## Overview
WAffy Dashboard is a WhatsApp message management system that organizes messages, tags customer chats, and synchronizes with CRM systems. The architecture follows a modern client-server pattern with a React frontend and FastAPI backend.

```mermaid
graph TD
    %% Main Components
    Client[Client Browser]
    FrontEnd[Frontend - React]
    BackEnd[Backend - FastAPI]
    DB[(PostgreSQL Database)]
    WhatsApp[WhatsApp API]
    HubSpot[HubSpot CRM]
    Excel[Excel Export]
    
    %% Frontend Components
    FrontEnd --> |React Components| Pages
    Pages --> Dashboard[Dashboard.jsx]
    Pages --> Settings[Settings Page]
    Pages --> Auth[Authentication Pages]
    
    FrontEnd --> |Services| UserService[userService.js]
    FrontEnd --> |State Management| AppState[App State]
    
    %% Backend Components
    BackEnd --> |API Routes| Routes[API Endpoints]
    BackEnd --> |Data Models| Models[SQLAlchemy Models]
    BackEnd --> |Agents| Agents[Processing Agents]
    
    %% Agents
    Agents --> ListenerAgent[Listener Agent]
    Agents --> AutoUpdateWebhook[Auto Update Webhook]
    Agents --> TranslatorAgent[Translator Agent]
    
    %% Models
    Models --> UserModel[User]
    Models --> SettingsModel[UserSettings]
    Models --> CustomerModel[Customer]
    Models --> OrderModel[Order]
    Models --> IssueModel[Issue]
    Models --> EnquiryModel[Enquiry]
    Models --> FeedbackModel[Feedback]
    Models --> InteractionModel[Interaction]
    Models --> BusinessModel[Business/Tags]
    Models --> ErrorLogModel[Error Logs]
    
    %% Data Flow
    Client <--> FrontEnd
    FrontEnd <--> |HTTP/REST| BackEnd
    BackEnd <--> DB
    
    %% External Integrations
    WhatsApp <--> |Webhooks| ListenerAgent
    ListenerAgent --> DB
    BackEnd <--> HubSpot
    BackEnd --> Excel
    
    %% Authentication Flow
    Client <--> |Authentication| Clerk[Clerk Auth]
    Clerk --> FrontEnd
    
    %% Styling
    classDef frontend fill:#ff9999,stroke:#333,stroke-width:1px;
    classDef backend fill:#9999ff,stroke:#333,stroke-width:1px;
    classDef database fill:#99ff99,stroke:#333,stroke-width:1px;
    classDef external fill:#ffff99,stroke:#333,stroke-width:1px;
    
    class Client,FrontEnd,Pages,Dashboard,Settings,Auth,UserService,AppState frontend;
    class BackEnd,Routes,Models,Agents,ListenerAgent,AutoUpdateWebhook,TranslatorAgent backend;
    class DB,UserModel,SettingsModel,CustomerModel,OrderModel,IssueModel,EnquiryModel,FeedbackModel,InteractionModel,BusinessModel,ErrorLogModel database;
    class WhatsApp,HubSpot,Excel,Clerk external;
```

## Component Details

### Frontend (React)
- **Authentication**: Uses Clerk for user authentication
- **UI Framework**: Tailwind CSS for styling with a pink-to-yellow gradient theme
- **Key Pages**:
  - Dashboard: Displays orders, customers, enquiries, and issues with filtering capabilities
  - Settings: Manages user profile, business details, and integration settings
- **Services**:
  - userService.js: Handles API communication with the backend

### Backend (FastAPI)
- **API Endpoints**: RESTful endpoints for CRUD operations on all data models
- **Data Models**: SQLAlchemy ORM models for database interaction
- **Agents**:
  - Listener Agent: Processes incoming WhatsApp messages
  - Auto Update Webhook: Configures WhatsApp API webhooks
  - Translator Agent: Handles message translation if needed

### Database (PostgreSQL)
- **Core Tables**:
  - Users: Stores user information and authentication details
  - UserSettings: Stores user preferences and API credentials
  - Customers: Customer information
  - Orders: Order details including items, quantity, unit, and status
  - Issues: Customer issues and their resolution status
  - Enquiries: Customer inquiries and follow-up information
  - Interactions: Records of customer interactions

### External Integrations
- **WhatsApp API**: Connects via webhooks to receive and send messages
- **HubSpot CRM**: Creates contacts, notes, and tickets for high-priority messages
- **Excel Export**: Alternative to CRM for exporting customer data

## Data Flow

1. **Message Reception**:
   - WhatsApp sends messages to the Listener Agent via webhooks
   - Messages are processed, categorized, and stored in the database

2. **User Authentication**:
   - Users authenticate via Clerk
   - Backend validates user identity and provides user-specific data

3. **Dashboard Operations**:
   - Frontend requests data filtered by the logged-in user's ID
   - Backend returns only data relevant to the authenticated user
   - Data is displayed with the latest entries first

4. **CRM Integration**:
   - High-priority messages trigger HubSpot ticket creation
   - Customer information is synchronized with the CRM

5. **Settings Management**:
   - User updates WhatsApp API credentials
   - Backend encrypts sensitive data before storage
   - Auto Update Webhook configures the WhatsApp API webhook

## Security Features
- Encryption of sensitive API keys and tokens
- User-specific data filtering
- Clerk authentication integration
- Secure webhook verification
