# app/agents/llm_agent.py

import os
from dotenv import load_dotenv
import json
import google.generativeai as genai

load_dotenv()
# Load Gemini API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiLLMAgent:
    def __init__(self, model_name="gemini-2.0-flash-lite"):
        self.model = genai.GenerativeModel(model_name)

    def analyze(self, message: str, context: list[str]) -> dict:
        prompt = self._build_prompt(message, context)

        try:
            response = self.model.generate_content(prompt)
            content = response.text.strip()
            print("[LLMAgent] RAW Gemini output:\n", content)

            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "").strip()
            elif content.startswith("```"):
                content = content.replace("```", "").strip()

            result = json.loads(content)

            # 👇 Enforce default conversation_status if Gemini skipped it
            if "conversation_status" not in result:
                print("⚠️ Gemini did not return 'conversation_status'. Defaulting to 'continue'")
                result["conversation_status"] = "continue"

            return result

        except Exception as e:
            print("[LLMAgent] Gemini error:", e)
            return {
                "category": "unknown",
                "priority": "moderate",
                "extracted_info": {},
                "conversation_status": "continue"
            }


    def _build_prompt(self, message: str, context: list[str]) -> str:
        context_str = "\n".join(f"- {msg}" for msg in context[-5:]) if context else "None"

        return f"""
You are an intelligent assistant. Based on the message history and the new customer message, classify the intent, assign a priority, and extract important details.

Context:
{context_str}

New Message:
"{message}"

Perform these tasks:
1. Classify the message intent: new order, inquiry, update, complaint, etc.
2. Assign priority: high, moderate, low.
3. Extract key information (e.g. product, quantity, address).
4. Conversation status: is the user starting a new conversation, continuing, or ending it?

Respond in JSON format like:
{{
  "category": "new order",
  "priority": "moderate",
  "conversation_status": "continue"  // or: "close", "new",
  "extracted_info": {{
    "order_id": "123456",
    "product": "chocolate cake",
    "delivery_time": "5 PM"
  }}
}}
        """.strip()
