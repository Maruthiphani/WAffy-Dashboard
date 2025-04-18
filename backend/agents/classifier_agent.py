import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv
from google import genai
from datetime import datetime

# ============ SETUP ============

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=gemini_api_key)

gemini_models = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
# list of gemini models can be found here https://ai.google.dev/gemini-api/docs/models

# Output paths
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(OUTPUT_DIR, "classified_messages.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "classified_messages.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.INFO)
log = lambda msg: logging.info(f"[Classifier] {msg}")

CATEGORY_LIST = [
    "new_order", "order_status", "general_inquiry", "complaint",
    "return_refund", "follow_up", "feedback", "others"
]

PRIORITY_MAP = {
    "complaint": "high",
    "return_refund": "high",
    "new_order": "high",
    "order_status": "moderate",
    "follow_up": "moderate",
    "general_inquiry": "moderate",
    "feedback": "low",
    "others": "low"
}

# ============ CLASSIFICATION FUNCTION ============

def classify_message_with_gemini(text):
    prompt = f"""You are an AI assistant that classifies WhatsApp messages into one of the following categories:

1. new_order - Customer shows clear intent to purchase something.
2. order_status - Asks about delivery, tracking, or the progress of an existing order.
3. general_inquiry - Questions about product details, pricing, store hours, payment options, or company policies.
4. complaint - Expressions of dissatisfaction or reports of a bad experience.
5. return_refund - Clear requests for returns, refunds, or exchanges.
6. follow_up - Refers to a previous conversation or nudges for a reply.
7. feedback - Reviews, suggestions, compliments, or general opinions.
8. others - Anything that doesn’t fit above.

Classify the following message:

\"{text}\"

Reply with only the category name.
"""
    response = client.models.generate_content(
        model=gemini_models[1],
        contents=prompt
    )

    return response.text.strip()

# ============ PROCESS MESSAGE ============

def process_message(message_text, customer_id="unknown", sender="unknown"):
    category = classify_message_with_gemini(message_text)
    priority = PRIORITY_MAP.get(category, "low")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    entry = {
        "timestamp": timestamp,
        "customer_id": customer_id,
        "sender": sender,
        "message": message_text,
        "predicted_category": category,
        "priority": priority
    }

    return entry

# ============ LOG TO CSV ============

def append_to_csv(entry, file_path=CSV_PATH):
    df = pd.DataFrame([entry])
    if not os.path.exists(file_path):
        df.to_csv(file_path, index=False)
    else:
        df.to_csv(file_path, mode="a", header=False, index=False)
    log("Written to CSV")

# ============ LOG TO JSON ============

def append_to_json(entry, file_path=JSON_PATH):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log("Written to JSON")

# ============ MAIN (for test run or standalone usage) ============

if __name__ == "__main__":
    from listener_agent import listen_for_new_message

    incoming = listen_for_new_message()

    result = process_message(
        message_text=incoming["message"],
        customer_id=incoming["customer_id"],
        sender=incoming["sender"]
    )

    print(f"\nCategory: {result['predicted_category']} | Priority: {result['priority']}")
    append_to_csv(result)
    append_to_json(result)
    print("Message logged.")
