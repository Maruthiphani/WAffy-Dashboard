from fastapi import FastAPI, Request, BackgroundTasks 
import json
import requests
import os
import psycopg2
import time 
import asyncio  
from collections import defaultdict  
from dotenv import load_dotenv
from google.cloud import translate_v2 as translate 
from Translator_agent import translate_to_english, detect_language, translate_to_language

load_dotenv()  # Load environment variables from .env

translate_client = translate.Client()

app = FastAPI()

VERIFY_TOKEN = "my_custom_token"
DATABASE_URL = os.getenv("DATABASE_URL")

# Get WhatsApp token from the database
def get_business_credentials(phone_number_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT whatsapp_api_key
        FROM user_settings
        WHERE whatsapp_app_id = %s
    """, (phone_number_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        return {"WHATSAPP_TOKEN": row[0]}
    return None

# GET request to verify webhook setup
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe" and
        params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return "Invalid token"

# Send a reply to the customer
# def send_reply(phone_number_id: str, to: str, message: str):
#     creds = get_business_credentials(phone_number_id)
#     if not creds:
#         print("No token found for phone_number_id:", phone_number_id)
#         return

#     whatsapp_token = creds["WHATSAPP_TOKEN"]
#     url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
#     headers = {
#         "Authorization": f"Bearer {whatsapp_token}",
#         "Content-Type": "application/json"
#     }
#     payload = {
#         "messaging_product": "whatsapp",
#         "to": to,
#         "text": {"body": message}
#     }
#     response = requests.post(url, headers=headers, json=payload)
#     print("Reply sent:", response.status_code, response.text)

# Handle incoming webhook message
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        message = entry["messages"][0]
        contact = entry["contacts"][0]
        metadata = entry["metadata"]

        # Extract details
        sender = message["from"]
        message_text = message["text"]["body"]

        # Translate to English if not already
        detected_lang = translate_client.detect_language(message_text)["language"]
        if detected_lang != "en":
            translated_message = translate_to_english(message_text)
            print("Translated:", translated_message)
        else:
            translated_message = message_text

        message_id = message["id"]
        timestamp_utc = message["timestamp"]
        message_type = message.get("type", "text")

        customer_id = contact["wa_id"]
        customer_name = contact["profile"]["name"]

        phone_number_id = metadata["phone_number_id"]
        business_number = metadata["display_phone_number"]

        # Log all details into result
        result = {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "Whatsapp_Number": sender,
            "Detected_Language": detected_lang,
            "Original_Text_Message": message_text,
            "Translated_Text_Message": translated_message,
            "message_id": message_id,
            "timestamp_utc": timestamp_utc,
            "message_type": message_type,
            "business_number": business_number,
            "phone_number_id": phone_number_id
        }

        with open("received_messages.json", "a") as f:
            f.write(json.dumps(result, indent=2))
            f.write("\n" + "-" * 50 + "\n")
        
        # #code to send reply to customer depending on recieved messege is valid or invalid
        # relevant_keywords = [
        #     "order", "cake", "buy", "purchase", "help", "issue", "problem", "nut free", "gluten free", "birthday", "engagement",
        #     "wedding", "party", "anniversary", "event", "celebration", "delivery", "pickup", "time", "date", "location",
        #     "contact", "number", "email", "message", "question", "inquiry", "feedback", "complaint", "suggestion", "request",
        #     "service", "support", "customer", "client", "order number", "tracking", "status", "update", "confirmation",
        #     "payment", "transaction", "receipt", "invoice", "refund", "exchange", "return", "policy", "terms", "conditions",
        #     "privacy", "security", "data", "protection", "terms of service", "conditions of use", "customer service",
        #     "technical support", "help desk", "support team", "contact us", "get in touch", "reach out", "customer care",
        #     "technical assistance", "technical help", "menu", "flavor", "size", "price", "custom", "eggless", "urgent",
        #     "delay", "allergen", "product"
        # ]

        # if not any(keyword in translated_message for keyword in relevant_keywords):
        #     reply = (
        #         "Hi! 👋 We specialize in cakes 🎂 and order support. "
        #         "Could you please clarify your message or mention the order number?"
        #     )
        #     send_reply(phone_number_id, sender, reply)
        # else:
        #     # Send thank-you / acknowledgment reply
        #     reply_en = "Thanks for your message! 🍰 We’ve received your request and will follow up shortly."
        #     reply = reply_en if detected_lang == "en" else translate_to_language(reply_en, detected_lang)
        #     send_reply(phone_number_id, sender, reply)

    except KeyError:
        print("Message format not standard or not a text message.")

    return {"status": "received"}
