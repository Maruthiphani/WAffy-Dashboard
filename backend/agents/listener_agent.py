from fastapi import FastAPI, Request
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

app = FastAPI()

# # Your webhook verification token (must match what you set in Meta Console)
VERIFY_TOKEN = "my_custom_token"

# Load credentials from environment variables

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# GET request to verify the webhook with Meta
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe" and
        params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return "Invalid token"

# Function to send a message back via WhatsApp Cloud API
def send_reply(to: str, message: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("✅ Reply sent:", response.status_code, response.text)

# POST request to receive incoming messages
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
   
    try:
        # Extract the actual message
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message["text"]["body"].lower()

          # Extract customer name from contacts
        entry = data["entry"][0]["changes"][0]["value"]
        customer_name = entry["contacts"][0]["profile"]["name"]

        # Save customer name, message, and number in clean format
        message_info = {
            "Customer_name": customer_name,
            "Text_Message": message["text"]["body"],
            "Whatsapp_Number": sender
        }

        with open("received_messages.json", "a") as f:
            f.write(json.dumps(message_info, indent=2))
            f.write("\n" + "-"*50 + "\n")

        # Keywords considered relevant for cake orders/support
        relevant_keywords = [
            "order", "cake", "buy", "purchase", "help", "issue", "problem", "nut free", "gluten free", "birthday", "engagement", "wedding", "party", "anniversary",
            "event", "celebration", "delivery", "pickup", "time", "date", "location", "contact", "number", "email", "message",
            "question", "inquiry", "feedback", "complaint", "suggestion", "request", "service", "support", "customer", "client",
            "order number", "tracking", "status", "update", "confirmation", "payment", "transaction", "receipt", "invoice",
            "refund", "exchange", "return", "policy", "terms", "conditions", "privacy", "security", "data", "protection",
            "terms of service", "conditions of use", "customer service", "technical support", "help desk", "support team",
            "contact us", "get in touch", "reach out", "customer care", "customer support", "technical assistance", "technical help",
            "support", "menu", "flavor", "size", "price", "custom", "eggless", "urgent", "delay", "confirmation", "allergen"
        ]

        # Check if message is irrelevant
        if not any(keyword in text for keyword in relevant_keywords):
            reply = (
                "Hi! 👋 We specialize in cakes 🎂 and order support. "
                "Could you please clarify your message or mention the order number?"
            )
            send_reply(sender, reply)
        else:
            print("👍 Relevant message received:", text)

    except KeyError:
        print("⚠️ Message format not standard or not a text message.")

    return {"status": "received"}
