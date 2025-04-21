from fastapi import FastAPI, Request
from classifier_agent import process_message
from logger_agent import append_to_csv, append_to_json
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
app = FastAPI()

VERIFY_TOKEN = "PaperPencil_TeSt_token123"
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

# === Webhook Verification ===
@app.get("/webhook")
async def verify(request: Request):
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe" and
        params.get("hub.verify_token") == VERIFY_TOKEN
    ):
        return int(params.get("hub.challenge"))
    return "Invalid token"

# === WhatsApp reply sender ===
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
    print(" Reply sent:", response.status_code, response.text)

# === POST handler for messages ===
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()

    # Pretty-print payload for inspection
    # print("\n Incoming WhatsApp Webhook Payload:")
    # print(json.dumps(data, indent=2))

    try:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender=message["from"]
        entry = data["entry"][0]["changes"][0]["value"]
        contact = entry["contacts"][0]
        metadata = entry["metadata"]

        result = process_message(
            message_text=message["text"]["body"],
            customer_id=contact["wa_id"],
            sender=message["from"],
            customer_name=contact["profile"]["name"],
            message_id=message["id"],
            timestamp_utc=message["timestamp"],
            message_type=message.get("type", "text"),
            business_number=metadata["display_phone_number"],
            phone_number_id=metadata["phone_number_id"]
        )
        print("🚀 Final output to log:\n", json.dumps(result, indent=2))

        append_to_csv(result)
        append_to_json(result)

        # Optional auto-response
        reply = (
            f"Thanks {result['customer_name']}! "
            f"Your message is categorized as *{result['predicted_category']}* "
            f"with *{result['priority']}* priority."
        )
        send_reply(sender, reply)

    except Exception as e:
        print("Error:", str(e))

    return {"status": "received"}
