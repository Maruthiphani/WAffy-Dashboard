import os
import json
import logging
import ast
from dotenv import load_dotenv
from datetime import datetime
from google import genai
from google.genai import types
from info_extractor import extract_info
from context_helper import get_message_context, update_log_entry_by_message_id

# === Setup ===
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

GEMINI_MODEL = "gemini-2.0-flash-lite"
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

# === Prompt Builder for Score-Based Classification ===
def build_prompt_with_scores(message: str, category_list: list) -> str:
    return f"""
You are an AI assistant that classifies WhatsApp messages into one of the following categories:
{', '.join(category_list)}.

Return a JSON dictionary where each category is assigned a score between 0 and 1, representing how well the message fits.

Example:
{{
  "new_order": 0.8,
  "feedback": 0.1,
  ...
}}

Message: "{message}"
"""

# === Gemini Classifier With Scores ===
def classify_message_with_gemini(text: str, category_list: list, priority_map: dict) -> tuple:
    prompt = build_prompt_with_scores(text, category_list)

    generation_config = types.GenerateContentConfig(
        temperature=0.5,
        top_p=0.95,
        max_output_tokens=200,
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

    raw_response = response.text.strip()

    def clean_and_parse_scores(raw: str) -> dict:
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.replace("```json", "").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()
            if cleaned.startswith("```"):
                cleaned = cleaned[3:].strip()

            # Optional: log what we're trying to parse
            with open(DEBUG_LOG_PATH, "a") as debug_log:
                debug_log.write(f"\n Cleaned for Parsing:\n{cleaned}\n")

            parsed = ast.literal_eval(cleaned)
            return {k: float(v) for k, v in parsed.items() if k in category_list}
        except Exception as e:
            with open(DEBUG_LOG_PATH, "a") as debug_log:
                debug_log.write(f"\n Parsing Failed: {str(e)}\n")
            return {cat: 0 for cat in category_list} | {"others": 1.0}

    scores = clean_and_parse_scores(raw_response)
    best_category = max(scores, key=scores.get)
    priority = priority_map.get(best_category, "moderate")

    # === Log Everything ===
    with open(DEBUG_LOG_PATH, "a") as debug_log:
        debug_log.write("\n\n====== CLASSIFICATION LOG ======\n")
        debug_log.write(f"📝 Message: {text}\n")
        debug_log.write(f"📤 Prompt:\n{prompt}\n")
        debug_log.write(f"📥 Gemini Response:\n{raw_response}\n")
        debug_log.write(f"🏷️ Chosen Category: {best_category}\n")
        debug_log.write(f"⚖️ Priority: {priority}\n")
        debug_log.write(f"🔍 All Scores:\n{json.dumps(scores, indent=2)}\n")

    return best_category, priority


# === Main Processing Function ===
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

    # Get contextual conversation history (last few messages)
    context_text = get_message_context(customer_id, phone_number_id, int(timestamp_utc)) or message_text
    print("🧠 Context used:\n", context_text)

    category, priority = classify_message_with_gemini(context_text, all_categories, priority_map)
    extracted_info = extract_info(context_text, category)
    timestamp = datetime.fromtimestamp(int(timestamp_utc)).strftime("%Y-%m-%d %H:%M:%S")

    update_log_entry_by_message_id(message_id, {
    "timestamp": timestamp,
    "predicted_category": category,
    "priority": priority,
    "extracted_info": extracted_info
    })

    return {
        "timestamp": timestamp,
        "raw_timestamp_utc": int(timestamp_utc),
        "message_id": message_id,
        "message_type": message_type,

        "customer_id": customer_id,
        "sender": sender,
        "customer_name": customer_name,

        "message": context_text,
        "predicted_category": category,
        "priority": priority,
        "extracted_info": extracted_info,

        "business_phone_number": business_number,
        "business_phone_id": phone_number_id
    }
