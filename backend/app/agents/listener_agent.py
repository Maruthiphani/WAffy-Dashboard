# app/agents/listener_agent.py

from fastapi import APIRouter, Request, HTTPException
from app.state import MessageState
import time, json, os
import psycopg2
from collections import defaultdict
from utils.encryption import decrypt_value
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# In-memory rate limiter
message_counter = defaultdict(list)

MAX_MESSAGES_PER_MINUTE = 10  
TIME_WINDOW_SECONDS = 60  

#get verify token from database
def fetch_verify_token_by_phone_number(phone_number_id):
    print("Fetching credentials for phone_number_id from Waffy database:", phone_number_id)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT whatsapp_verify_token
        FROM user_settings
        WHERE whatsapp_phone_number_id = %s
    """, (phone_number_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise Exception("No verify token found for this phone_number_id")

    return {
        "VERIFY_TOKEN": decrypt_value(row[0]),
    }

def get_listener_router(graph):
    # Create a FastAPI router to handle webhook routes
    router = APIRouter()

    # ---- Webhook Verification Endpoint ----
    @router.get("/webhook/{phone_number_id}")
    
    async def verify_webhook(phone_number_id: str, request: Request):
        #get verify token from database
        expected_token = fetch_verify_token_by_phone_number(decrypt_value(phone_number_id))
        VERIFY_TOKEN= expected_token["VERIFY_TOKEN"]
        # Extract query parameters from Facebook's verification request
        params = request.query_params
        # If the mode is 'subscribe' and the token matches, return the challenge code to verify
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return int(params.get("hub.challenge"))
        # If token is invalid, return a plain text error
        return "Invalid token"

    # ---- Webhook Message Receiver Endpoint ----
    @router.post("/webhook/{phone_number_id}")
    async def receive_whatsapp_message(phone_number_id: str, request: Request):
        data = await request.json()
        try:
            entry = data["entry"][0]["changes"][0]["value"]
            message = entry["messages"][0]
            contact = entry["contacts"][0]
            metadata = entry["metadata"]

            customer_id=contact["wa_id"]
            current_time = time.time()
            # RATE LIMIT CHECK
            timestamps = message_counter[customer_id]
            # Only keep timestamps in last 60 seconds
            timestamps = [ts for ts in timestamps if current_time - ts < TIME_WINDOW_SECONDS]
            timestamps.append(current_time)
            message_counter[customer_id] = timestamps

            if len(timestamps) > MAX_MESSAGES_PER_MINUTE:
                raise HTTPException(status_code=429, detail="Too many messages, slow down.")

             # ---- Populate structured state for processing ----
            state = MessageState(
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

            result = graph.invoke(state)
            print("Final result:\n", json.dumps(result, indent=2))

        except Exception as e:
            print("Webhook Error:", e)

        return {"status": "received"}

    return router
