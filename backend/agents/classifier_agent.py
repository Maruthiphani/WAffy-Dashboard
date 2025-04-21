import os
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
from google import genai
from google.genai import types

# === Setup ===
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

GEMINI_MODEL = "gemini-2.0-flash"
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "business_config.json")
DEBUG_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "classification_debug.log")

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
log = lambda msg: logging.info(f"[Classifier] {msg}")

# === Load Business Config ===
def load_business_config(phone_number_id: str) -> dict:
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("Missing business_config.json")

    with open(CONFIG_PATH, "r") as f:
        all_configs = json.load(f)

    for business_id, info in all_configs.items():
        if info.get("phone_number_id") == phone_number_id:
            return info
    raise ValueError(f"No config found for phone_number_id: {phone_number_id}")

# === Build Prompt Dynamically ===
def build_prompt(message: str, category_descriptions: dict) -> str:
    desc_block = "\n".join([f"{i+1}. {cat} - {desc}" for i, (cat, desc) in enumerate(category_descriptions.items())])

    return f"""You are an AI assistant that classifies WhatsApp messages into one of the following categories:

{desc_block}

Classify the following message:
\"{message}\"

Reply with only the category name.
"""

# === Smart Descriptions (optional, could be moved to config)
CATEGORY_DESCRIPTIONS = {
    "new_order": "Customer shows clear intent to purchase something.",
    "order_status": "Asks about delivery, tracking, or the progress of an existing order.",
    "general_inquiry": "Questions about product details, pricing, store hours, payment options, or company policies.",
    "complaint": "Expressions of dissatisfaction or reports of a bad experience.",
    "return_refund": "Clear requests for returns, refunds, or exchanges.",
    "follow_up": "Refers to a previous conversation or nudges for a reply.",
    "feedback": "Reviews, suggestions, compliments, or general opinions.",
    "others": "Anything that doesn’t fit above.",
}

# === Gemini Classification ===
def classify_message_with_gemini(text: str, category_list: list) -> str:
    # Build category description block
    category_descriptions = {cat: CATEGORY_DESCRIPTIONS.get(cat, f"{cat} category") for cat in category_list}
    prompt = build_prompt(text, category_descriptions)

    generation_config = types.GenerateContentConfig(
        temperature=0.5,
        top_p=0.95,
        max_output_tokens=100,
        safety_settings=[
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
        ],
        system_instruction="You are an assistant trained to classify customer WhatsApp messages into categories for customer support."
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=generation_config,
    )

    category = response.text.strip()
    if category not in category_list:
        category = "others"

    # Log prompt + response for debugging
    with open(DEBUG_LOG_PATH, "a") as debug_log:
        debug_log.write(f"\n\n=== Message: {text}\n")
        debug_log.write(f"Prompt:\n{prompt}\n")
        debug_log.write(f"Response:\n{response.text.strip()}\n")
        debug_log.write(f"Final Category: {category}\n")

    return category

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

    config = load_business_config(phone_number_id)
    all_categories = config.get("suggested_categories", []) + config.get("custom_categories", [])
    priority_map = config.get("priorities", {})

    category = classify_message_with_gemini(message_text, all_categories)
    priority = priority_map.get(category, "moderate")
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
