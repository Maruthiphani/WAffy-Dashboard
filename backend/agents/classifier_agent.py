import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import datetime

# === Setup ===
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

# === Model Config ===
GEMINI_MODEL = "gemini-2.0-flash"
gemini_models = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
# list of gemini models can be found here https://ai.google.dev/gemini-api/docs/models

# === Logging ===
logging.basicConfig(level=logging.INFO)
log = lambda msg: logging.info(f"[Classifier] {msg}")

# === Category & Priority Mapping ===
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

# === Gemini Classification ===


def classify_message_with_gemini(text: str) -> str:
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
    
    generation_config = types.GenerateContentConfig(
        temperature=0.5,
        top_p=0.95,
        max_output_tokens=100,
    

        safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory. HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory. HARM_CATEGORY_CIVIC_INTEGRITY,
                threshold=types.HarmBlockThreshold.BLOCK_NONE,
            ),
        ],

        system_instruction="You are an assistant trained to classify customer WhatsApp messages into categories for customer support.",

    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=generation_config,
    )
    return response.text.strip()


# === Process Message for Logging/Storage ===
def process_message(
    message_text: str,
    customer_id: str,
    sender: str,
    customer_name: str,
    message_id: str,
    timestamp_utc: str,
    message_type: str,
    business_number: str,
    phone_number_id: str
) -> dict:

    category = classify_message_with_gemini(message_text)
    priority = PRIORITY_MAP.get(category, "low")
    timestamp = datetime.fromtimestamp(int(timestamp_utc)).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "timestamp": timestamp,
        "raw_timestamp_utc": int(timestamp_utc),
        "message_id": message_id,
        "message_type": message_type,

        "customer_id": customer_id,
        "sender": sender,
        "customer_name": customer_name,

        "message": message_text,
        "predicted_category": category,
        "priority": priority,

        "business_phone_number": business_number,
        "business_phone_id": phone_number_id
    }
