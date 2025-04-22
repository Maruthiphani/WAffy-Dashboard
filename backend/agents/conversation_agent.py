import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# === Load API Key ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

# === Choose model ===
GEMINI_MODEL = "gemini-2.0-flash-lite"  # Or flash if you want faster

# === Prompt Template ===
SYSTEM_INSTRUCTION = """You are a smart agent that analyzes customer conversations over WhatsApp.

Given the last few messages from the same user to a business, your job is to:

1. Understand the overall intent
2. Classify the conversation into one of the categories
3. Determine the priority level
4. Extract any useful structured information (if possible)

Always return a JSON object like this:

{
  "category": "new_order",
  "priority": "high",
  "extracted_info": {
    "product": "nut-free chocolate cake",
    "quantity": 2,
    "delivery_time": "Friday morning"
  }
}

Only include `extracted_info` fields if you are confident.
If something is missing, leave it out. Don't make things up.
"""

def format_conversation(messages: list) -> str:
    """
    Format a list of messages into a readable conversation block.
    Each message should be a dict with 'text' and 'timestamp'.
    """
    return "\n".join([f"[{msg['timestamp']}] {msg['text']}" for msg in messages])

# === Main Agent Function ===

def analyze_conversation(messages: list, business_type: str = None) -> dict:
    """
    messages: List of dicts with 'text' and 'timestamp' keys
    business_type: Optional context (e.g., 'bakery', 'clinic')
    Returns a dict with classification and extracted info
    """

    # Build prompt
    conversation = format_conversation(messages)
    pre_prompt = f"The business type is: {business_type or 'general'}.\n\nHere is the recent conversation:"
    final_prompt = f"{pre_prompt}\n\n{conversation}"

    generation_config = types.GenerateContentConfig(
        temperature=0.4,
        top_p=0.9,
        max_output_tokens=512,
        safety_settings=[
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_HARASSMENT, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH),
            types.SafetySetting(category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE),
        ],
        system_instruction=SYSTEM_INSTRUCTION
    )

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=final_prompt,
            config=generation_config
        )
        raw = response.text.strip()
        print("🧠 Agent Raw Output:\n", raw)

        # 🛠️ Clean up wrapped ```json code block``` if present
        if raw.startswith("```"):
            raw = raw.strip("`").strip()
            if raw.lower().startswith("json"):
                raw = raw[4:].strip()  # remove 'json' language hint

        result = json.loads(raw)
        return result

    except Exception as e:
        print(f"❌ Agent Error: {e}")
        return {
            "category": "others",
            "priority": "moderate",
            "extracted_info": {}
        }
