# app/agents/listener_agent.py

from fastapi import APIRouter, Request
from app.state import MessageState
import time, json, os

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "PaperPencil_TeSt_token123")

def get_listener_router(graph):
    router = APIRouter()

    @router.get("/webhook")
    async def verify_webhook(request: Request):
        params = request.query_params
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == VERIFY_TOKEN
        ):
            return int(params.get("hub.challenge"))
        return "Invalid token"

    @router.post("/webhook")
    async def receive_whatsapp_message(request: Request):
        data = await request.json()
        try:
            entry = data["entry"][0]["changes"][0]["value"]
            message = entry["messages"][0]
            contact = entry["contacts"][0]
            metadata = entry["metadata"]

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
