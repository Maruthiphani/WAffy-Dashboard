import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types

# === Setup ===
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

gemini_models = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite"]
GEMINI_MODEL = "gemini-2.0-flash-lite"
DEBUG_LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "info_extraction_debug.log")

# === Categories That Need Info Extraction ===
CATEGORIES_REQUIRING_EXTRACTION = [
    "new_order",
    "appointment_booking",
    "general_inquiry",
    "complaint",
    "return_refund",
    "customization_request", 
    "delivery_time_query"
]

# === Info Extraction Prompt ===
def build_extraction_prompt(message: str) -> str:
    return f"""
Extract structured data from the following customer message. Return only a JSON object with the fields that are actually mentioned.

Possible fields (only include what is present in the message):
- product
- quantity
- delivery_date
- pickup_time
- dietary_preference
- address
- contact
- customization
- budget
- urgency
- issue_description
- refund_reason

Message: "{message}"

Return only valid JSON.
""".strip()

# === Info Extractor ===
def extract_info(message_text: str, category: str) -> dict:
    if category not in CATEGORIES_REQUIRING_EXTRACTION:
        return {}

    prompt = build_extraction_prompt(message_text)

    generation_config = types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.9,
        max_output_tokens=300,
        safety_settings=[
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
        ],
        system_instruction="You are an assistant that extracts structured details from customer service messages."
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=generation_config,
        )
        raw = response.text.strip()

        # Clean any Markdown formatting if present
        if raw.startswith("```json"):
            raw = raw.replace("```json", "").strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()
        if raw.startswith("```"):
            raw = raw[3:].strip()

        extracted = json.loads(raw)

        # Log
        with open(DEBUG_LOG_PATH, "a") as f:
            f.write("\n\n====== INFO EXTRACTION LOG ======\n")
            f.write(f"📝 Message: {message_text}\n")
            f.write(f"📤 Prompt:\n{prompt}\n")
            f.write(f"📥 Response:\n{raw}\n")
            f.write(f"✅ Extracted:\n{json.dumps(extracted, indent=2)}\n")

        return extracted

    except Exception as e:
        with open(DEBUG_LOG_PATH, "a") as f:
            f.write("\n\n Extraction Error\n")
            f.write(f"Message: {message_text}\n")
            f.write(f"Error: {str(e)}\n")
        return {}
