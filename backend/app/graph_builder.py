from langgraph.graph import StateGraph, END
from app.state import MessageState
from app.nodes.listener_node import listener_node
from app.nodes.context_node import context_node

from app.nodes.llm_node import llm_node
from app.nodes.storage_node import storage_node

def build_graph():
    builder = StateGraph(MessageState)

    builder.add_node("Listener", listener_node)
    builder.add_node("Context", context_node)
    builder.add_node("LLM", llm_node)
    builder.add_node("Storage", storage_node)

    builder.set_entry_point("Listener")
    builder.add_edge("Listener", "Context")
    builder.add_edge("Context", "LLM")
    builder.add_edge("LLM", "Storage")
    builder.add_edge("Storage", END)

    return builder.compile()
