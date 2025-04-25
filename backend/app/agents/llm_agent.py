# app/agents/llm_agent.py

# app/agents/llm_agent.py

import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime
from google import genai
from google.genai import types
from app.utils.category_map import DEFAULT_CATEGORIES, DEFAULT_PRIORITY_MAP, STANDARD_KEYS


categories_str = ", ".join(DEFAULT_CATEGORIES)
priority_map_str = "\n".join(f"- {k}: {v}" for k, v in DEFAULT_PRIORITY_MAP.items())
schema_str = "\n".join(f"- {k}: {v}" for k, v in STANDARD_KEYS.items())



# === Load credentials and initialize client ===
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

GEMINI_MODEL = "gemini-2.0-flash-lite"  # update to latest model if available

class GeminiLLMAgent:
    def analyze(self, message: str, context: list[str] = None, prev_info: dict | None = None) -> dict:
        prompt = self._build_prompt(message, context)

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

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=generation_config,
            )
            content = response.text.strip()
            print("[LLMAgent] RAW Gemini output:\n", content)

            if response.candidates and hasattr(response.candidates[0], "finish_reason"):
                print("🔒 Safety Finish Reason:", response.candidates[0].finish_reason)

            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            content = re.sub(r'//.*', '', content)

            result = json.loads(content)
            return result

        except Exception as e:
            print("[LLMAgent] Gemini error:", e)
            return {
                "category": "others",
                "priority": "moderate",
                "conversation_status": "continue",
                "extracted_info": {}
            }

    def _build_prompt(self, message: str, context: list[str] = None) -> str:
        context_str = "\n".join(f"- {msg}" for msg in context[-10:]) if context else "None"
    

        return f"""
You are a smart assistant that processes customer messages sent to a business on WhatsApp.

Message:
"{message}"

Context (last messages from this customer):
{context_str}

Your tasks:
- Classify intent.
- Assign a priority.
- Decide if this message is related to the context.
- If related: combine the extracted_info meaningfully.
- Return conversation_status: 'new', 'continue', or 'close'.

Categories to choose from:
{categories_str}

Priority mapping:
{priority_map_str}

Use the following keywords for extracted_info:
{schema_str}

Your job is to intelligently **update the extracted_info** based on the new message.
If the message adds or updates products, addresses, delivery methods, etc., reflect that.
If it says something irrelevant like "thanks", the extracted_info should remain unchanged.

---

Respond in JSON format like:
{{
  "category": "complaint",
  "priority": "high",
  "conversation_status": "continue",
  "extracted_info": {{
    "issue": "damaged product",
    "product": "lotion",
    "request": "replacement or refund"
  }}
}}

If it's an order or update, you can also respond like:
{{
  "category": "new order",
  "priority": "moderate",
  "conversation_status": "continue",
  "extracted_info": {{
    "items": [
      {{ "product": "A4 paper", "quantity": 5 }},
      {{ "product": "black pens", "quantity": 3 }}
    ],
    "delivery_address": "14 Park Street"
  }}
}}
        """.strip()

# ✅ Singleton
llm_agent = GeminiLLMAgent()



# import os
# import json
# from dotenv import load_dotenv
# import google.generativeai as genai
# from app.utils.category_map import DEFAULT_CATEGORIES, DEFAULT_PRIORITY_MAP, STANDARD_KEYS

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# categories_str = ", ".join(DEFAULT_CATEGORIES)
# priority_map_str = "\n".join(f"- {k}: {v}" for k, v in DEFAULT_PRIORITY_MAP.items())
# schema_str = "\n".join(f"- {k}: {v}" for k, v in STANDARD_KEYS.items())

# class GeminiLLMAgent:
#     def __init__(self, model_name="gemini-1.5-pro-latest"):
#         self.model = genai.GenerativeModel(model_name)

#     def analyze(self, message: str) -> dict:
#         prompt = self._build_prompt(message)

#         try:
#             response = self.model.generate_content(prompt)
#             content = response.text.strip()
#             print("[LLMAgent] RAW Gemini output:\n", content)

#             if content.startswith("```json"):
#                 content = content.replace("```json", "").replace("```", "").strip()
#             elif content.startswith("```"):
#                 content = content.replace("```", "").strip()

#             return json.loads(content)
#         except Exception as e:
#             print("[LLMAgent] Error:", e)
#             return {
#                 "category": "unknown",
#                 "priority": "moderate",
#                 "conversation_status": "continue",
#                 "extracted_info": {}
#             }

#     def _build_prompt(self, message: str) -> str:
#         return f"""
# You are a smart assistant that processes customer messages sent to a business on WhatsApp.

# Task:
# - Analyze the message and classify its intent.
# - Assign a priority (high, moderate, low).
# - Extract useful structured information.
# - Indicate if this message continues, closes, or starts a conversation.

# Message:
# "{message}"

# Categories to choose from:
# {categories_str}

# Priority mapping:
# {priority_map_str}

# Use the following keywords for extracted_info:
# {schema_str}

# Respond in JSON:
# {{
#   "category": "new order",
#   "priority": "high",
#   "conversation_status": "continue",
#   "extracted_info": {{
#     "delivery_time": "6pm Saturday"
#   }}
# }}
#         """.strip()

# # ✅ Export singleton
# llm_agent = GeminiLLMAgent()
