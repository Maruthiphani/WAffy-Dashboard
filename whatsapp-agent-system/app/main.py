from fastapi import FastAPI, Request
from app.graph_builder import build_graph
from app.state import MessageState
from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv()
app = FastAPI()

VERIFY_TOKEN = "PaperPencil_TeSt_token123"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

graph = build_graph()

# === Webhook Verification for WhatsApp ===
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return "Invalid token"

# === WhatsApp Message Sender ===
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

# === WhatsApp Webhook Receiver ===
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        message = entry["messages"][0]
        contact = entry["contacts"][0]
        metadata = entry["metadata"]

        # Prepare state for LangGraph
        message_state = MessageState(
            sender=message["from"],
            customer_id=contact["wa_id"],
            customer_name=contact["profile"]["name"],
            message=message["text"]["body"],
            message_id=message["id"],
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(int(message["timestamp"]))),
            raw_timestamp_utc=int(message["timestamp"]),
            message_type=message.get("type", "text"),
            business_phone_number=metadata["display_phone_number"],
            business_phone_id=metadata["phone_number_id"]
        )

        # Run through LangGraph
        result = graph.invoke(message_state)

        # Log
        print("🚀 Final result:\n", json.dumps(result, indent=2))

        # Send reply
        reply = (
            f"Thanks {result['customer_name']}! "
            f"Your message is categorized as *{result['predicted_category']}* "
            f"with *{result['priority']}* priority."
        )
        send_reply(result["sender"], reply)

    except Exception as e:
        print("❌ Error handling message:", str(e))

    return {"status": "received"}
