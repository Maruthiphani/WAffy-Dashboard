from langgraph.graph import StateGraph, END
from app.state import MessageState
from app.nodes.listener_node import listener_node
from app.nodes.context_node import context_node
from app.nodes.llm_node import llm_node
from app.nodes.storage_node import storage_node
from app.nodes.responder_node import responder_node
from app.nodes.review_node import review_node

def build_graph():
    builder = StateGraph(MessageState)

    builder.add_node("Listener", listener_node)
    builder.add_node("Context", context_node)
    builder.add_node("LLM", llm_node)
    builder.add_node("Review", review_node)
    builder.add_node("Storage", storage_node)
    builder.add_node("Responder", responder_node)

    builder.set_entry_point("Listener")
    builder.add_edge("Listener", "Context")
    builder.add_edge("Context", "LLM")
    builder.add_edge("LLM", "Review")
    builder.add_edge("Review", "Storage")

    def route_to_responder(state):
        return "Responder"
            
    builder.add_conditional_edges(
        "Storage",
        route_to_responder
    )

    builder.add_edge("Responder", END)

    return builder.compile()
