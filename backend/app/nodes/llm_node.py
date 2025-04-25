from app.agents.llm_agent import GeminiLLMAgent
from app.state import MessageState
import json

llm_agent = GeminiLLMAgent()

def merge_extracted_info(existing: dict, new: dict) -> dict:
    merged = existing.copy()

    for key, value in new.items():
        if isinstance(value, list):
            merged.setdefault(key, [])

            # Replace if item name matches
            for new_item in value:
                existing_items = merged[key]
                found = False
                for i, old_item in enumerate(existing_items):
                    if old_item.get("item") == new_item.get("item"):
                        existing_items[i] = new_item  # Replace with updated one
                        found = True
                        break
                if not found:
                    existing_items.append(new_item)

        else:
            merged[key] = value  # override or add

    return merged


def llm_node(state: MessageState) -> MessageState:
    if not state.message:
        print("[LLMNode] No message to analyze")
        return state

    print(f"[LLMNode] 🤖 Analyzing message: {state.message}")
    result = llm_agent.analyze(state.message, state.context or [])

    state.predicted_category = result.get("category", "unknown")
    state.priority = result.get("priority", "moderate")
    state.conversation_status = result.get("conversation_status", "continue")

    new_info = result.get("extracted_info", {})
    existing_info = state.extracted_info or {}
    state.extracted_info = merge_extracted_info(existing_info, new_info)

    print(f"[LLMNode] ✅ Analysis result:\n{json.dumps(result, indent=2)}")
    print(f"[LLMNode] 🧾 Merged extracted_info:\n{json.dumps(state.extracted_info, indent=2)}")

    return state
