# WAffy - Your Smart WhatsApp Agent for SMBs

**WAffy** is a smart multi-agent system designed to streamline WhatsApp communication for small and medium-sized businesses (SMBs). It transforms chaotic WhatsApp inboxes into organized, actionable workflows, saving time and improving customer engagement.

![image](https://github.com/user-attachments/assets/33a4cfa9-a694-467b-b844-90ce86461c51)


---

## Problem

SMBs rely heavily on **WhatsApp** for customer interactions, including orders, queries, complaints, and updates. However, they face significant challenges:
- **Unstructured inboxes** that are overwhelming to manage.
- **Manual data entry** into Excel or CRMs, which is time-consuming.
- **Missed follow-ups**, leading to lost deals or delayed responses.

---

## Solution - **WAffy**

**WAffy** automates and organizes WhatsApp communication with the following features:
- **Listens** to incoming messages via the WhatsApp Cloud API.
- **Classifies** messages by category (e.g., order, complaint, inquiry) and urgency in real time.
- **Logs** messages automatically into Excel or HubSpot CRM.
- **Generates AI-driven responses** for common queries.
- **Visualizes** data in a clean, interactive React dashboard.

WAffy turns WhatsApp chaos into clarity with zero manual effort, making life easier for business.

---

## Multilingual Support

WAffy supports **40+ languages**, including English, Hindi, Tamil, Spanish, Arabic, and more. It classifies, tags, and responds to messages in any supported language, ensuring seamless communication with diverse customers.

> WAffy speaks your customers’ language — literally!

---

## Target Audience

WAffy is designed for:
- Small and medium sized independent brands (clothing, decor, handmade goods).
- Service-based businesses (fitness trainers, tutors, coaches).
- Local sellers using WhatsApp as their primary customer channel.

---

## Impact on buisnesses

| **Before WAffy**                | **After WAffy**                                   |
|---------------------------------|---------------------------------------------------|
| Hundreds of mixed chats         | Categorized and prioritized messages              |
| Manual CRM entry                | Auto-logged to HubSpot/Excel                      |
| Missed follow-ups               | Clear tags and dashboard alerts                   |
| Slow replies                    | Instant AI-suggested replies                      |
| Language constraints            | Auto Translate for smoother conversation          |
| Spam or toxic messges           | Smart filters + bot detection                     |


## Real-World Example

A  backery shop receives 50–80 WhatsApp messages daily, including order queries, customization information and feedback.

**Before WAffy:**
- The shop owner manually read each message.
- Wrote down orders in a notebook or spreadsheet
- Sometimes forgot last-minute changes or urgent complaints
- Missed responses that leads to unhappy customers.

**After WAffy:**
- Messages are tagged (e.g., order, complaint, feedback).
- Critical messages are marked urgent.
- Data is synced to HubSpot automatically.
- Suggested replies save **2+ hours daily**.

---

## Current Features (MVP)

- ✅ WhatsApp Cloud API webhook setup.
- ✅ Listener Agent captures incoming messages.
- ✅ Language translation for 40+ languages using Gemini API.
- ✅ Message classification with tags (e.g., order, complaint).
- ✅ Excel logging with download option.
- ✅ HubSpot ticket creation via API.
- ✅ Basic React dashboard with real-time data.
- ✅ AI-generated responses for basic order queries.

---

## Future Scope

- **Feedback Learning**: Improve classification accuracy over time.
- **Catalog Management**: Manage product info and send links via chat.
- **OCR Agent**: Read payment screenshots to update systems.
- **Multi-User Support**: Enable team collaboration for SMBs.
- **Real-Time Alerts**: Enhance reply-from-dashboard functionality.
- **Smart Nudges**: Suggest follow-ups based on message behavior.
- **Customer Sentiment Analysis**: Gain insights for business improvement.
- **Recurring Workflows**: Automate weekly reports and re-engagement messages.

---

## Technical Stack

| **Layer**           | **Technologies**                                                                 |
|---------------------|----------------------------------------------------------------------------------|
| **Backend**         | FastAPI (Python)                                                                |
| **AI & Agents**     | LangGraph for multi-agent AI orchestration                                      |
| **Frontend**        | React.js, Tailwind CSS, Ant Design                                              |
| **Authentication**  | Clerk.dev                                                                       |
| **Database**        | PostgreSQL (hosted on Aiven with SSL)                                           |
| **Integrations**    | WhatsApp Cloud API (Graph API v18.0), HubSpot API, Excel/Google Sheets via APIs |
| **Deployment**      | Production: FastAPI on Render, React-frontend on Vercel                         |                         
| **ORM**             | SQLAlchemy                   |   

---

## Architecture
<img src="https://i.imgur.com/mwUh2Nf.png">


### Multi-Agent Architecture

Agent orchestration is managed using LangGraph, enabling structured, stateful workflows between agents based on message type and context. Each agent operates as a node in the   graph, with transitions defined by classification outcomes and processing stages.

<img src="https://i.imgur.com/bpTQmcK.png">


1. **Listener Agent**  
   - Receives all incoming messages from the **WhatsApp Cloud API** webhook.  
   - Parses the payload, authenticates the request, and prepares a normalized message object.  
   - Passes the message forward for validation and processing.
     
<p align="center">
<img src="https://i.imgur.com/jOt1tRI.png" width="350" style="float:left; margin-right:70px"/>
</p>

2. **Context Agent**  
   - Fetches the latest conversation context (e.g., the last few messages from the same user).  
   - Enables continuity in conversations and helps understand follow-up or fragmented messages.  
   - Appends contextual information to the current message before sending it to the LLM Agent.

3. **LLM Agent**  
   - The core logic layer, powered by a large language model, performs:  
     - Intent classification (e.g., order, enquiry, complaint).  
     - Priority tagging (e.g., high, medium, low).  
     - Entity extraction (e.g., product, quantity, name).  
     - Language understanding across **40+ languages**.  
   - Returns a structured JSON payload with intent and extracted fields.

4. **Review Agent**  
   - Applicable only for order-related messages.  
   - Checks if an order from the same customer exists within a 30-minute window.  
   - Consolidates new messages with existing orders or treats them as fresh orders.  
   - Ensures multiple short messages from a customer are grouped appropriately.

5. **Logger Agent**  
   - Stores structured message data in the **PostgreSQL** database.  
   - If CRM sync is enabled, creates/updates contacts and logs tickets in **HubSpot** with relevant tags and details.  
   - Ensures reliable storage of message history and metadata for future reference.
  
     <img src="https://i.imgur.com/z0bPfXF.png" width="350"/>
     

6. **Responder Agent**  
   - Selects appropriate responses (predefined templates or dynamic) based on the classified message type and extracted data.  
   - Sends replies to users via the **WhatsApp Cloud API** and logs the response status.  
   - Serves as the final communication step in the workflow.
  
   - 

---

## Features

### Clerk Authentication
- Secure, real-time authentication with Clerk for seamless login/logout.

### Frontend (React + Tailwind CSS + Ant Design)
- **Dashboard**: Manage Orders, Customers, and Inquiries via a tab-based UI.  
- **Hero Slider**: Display promotions and banners.  
- **Dynamic Filtering**: Filter by Customer ID or Date with live updates.  
- **Vibrant UI/UX**: Gradient buttons, active tabs, responsive tables, and real-time data.

### Backend (FastAPI)
- **APIs**: `/api/orders`, `/api/customers`, `/api/enquiries`.  
- **Data Fetching**: Pulls data securely from PostgreSQL.  
- **Automatic Refresh**: Updates dashboard data instantly on filter submission.

### Database (PostgreSQL)
- Structured tables for orders, customers, and enquiries.  
- Automatic timestamps for record creation and updates.  
- Secure SSL connection via Aiven.

---

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-repo/waffy.git
   cd waffy
   ```

2. **Install Dependencies**:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `cd frontend && npm install`

3. **Configure Environment**:
   - Set up `.env` with WhatsApp API keys, HubSpot tokens, and Aiven PostgreSQL credentials.
   - ENCRYPTION_KEY=
   - DATABASE_URL=postgresql://avnadmin:AVNS_8qhqmlqzPGBFt4YTjQA@pg-waffy-waffy.g.aivencloud.com:26140/waffy_db?sslmode=require
   - FORWARDING_URL=https://https://waffy-dashboard.onrender.com
   - Configure Clerk.dev for authentication.

4. **Run Locally**:
   - Backend: `uvicorn main:app --reload`
   - Frontend: `npm start`
   - Use ngrok for temporary HTTPS webhook URLs.
   - place the forwarding URL obtained using ngrok, in .env file.

5. **Deploy to Production**:
   - Backend: Deploy FastAPI to Render.
   - Frontend: Build and host on Vercel or Netlify.

---

**Application Flow:**
Add the screenshots of the WAffy app navigation

---
   
**Project Repository URL:**
https://github.com/Maruthiphani/WAffy-Dashboard.git

---

**Deployed Endpoint URL for backend FastAPI:** https://waffy-dashboard.onrender.com

**Deployed Endpoint URL for Frontend:** https://waffy-dashboard.vercel.app/

---

**Project Video:**

---

**Team Members:**
1)Nagajyothi Prakash : njp-coder
2)Akanksha Vishwakarma : akanksha-vishwak
3)Maruthi Phanindra Ayyagari : Maruthiphani
4)Harsha Naik : Harsha-Ramesh-Naik


---


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


---




