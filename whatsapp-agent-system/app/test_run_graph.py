# app/test_run_graph.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.graph_builder import build_graph
from datetime import datetime
import pprint

# Build the graph (same as main FastAPI would)
graph = build_graph()

# Dummy input message (mocked WhatsApp payload)
message_data = {
    "sender": "447778596773",
    "message": "Please make the cake eggless.",
    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    "raw_timestamp_utc": int(datetime.utcnow().timestamp()),
    "message_id": "wamid.test123",
    "message_type": "text",
    "customer_name": "Akanksha",
    "business_phone_number": "15556454320",
    "business_phone_id": "574048935800997"
}

# Run the LangGraph
result = graph.invoke(message_data)

# Print the output
print("\n📦 Final Processed Message:\n")
pprint.pprint(result, width=120)
