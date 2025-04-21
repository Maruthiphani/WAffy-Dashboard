import os
import json
from datetime import datetime, timedelta

# === Constants ===
LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "classified_messages.json")
MAX_MESSAGES = 6  # how many recent messages to join
MAX_TIME_WINDOW_MINUTES = 5

def get_message_context(customer_id: str, business_id: str, current_ts_utc: int) -> str:
    """Return combined recent message history for same customer & business"""
    if not os.path.exists(LOG_PATH):
        return ""

    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            history = json.load(f)
    except:
        return ""

    # Convert to datetime object
    now = datetime.utcfromtimestamp(current_ts_utc)

    # Filter messages for same customer and business
    relevant = [
        msg for msg in history
        if msg.get("customer_id") == customer_id
        and msg.get("business_phone_id") == business_id
    ]

    # Sort by timestamp
    relevant.sort(key=lambda m: m.get("raw_timestamp_utc", 0), reverse=True)

    # Only keep messages within time window
    recent = [
        msg for msg in relevant
        if abs(current_ts_utc - msg.get("raw_timestamp_utc", 0)) <= MAX_TIME_WINDOW_MINUTES * 60
    ]

    # Take last N
    last_msgs = recent[:MAX_MESSAGES]
    texts = [msg.get("message", "") for msg in reversed(last_msgs)]
    return "\n".join(texts).strip()
