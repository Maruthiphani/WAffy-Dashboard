from agents.conversation_agent import analyze_conversation

# Simulated WhatsApp chat messages
# messages = [
#     {"timestamp": "09:50", "text": "hey"},
#     {"timestamp": "09:51", "text": "can I place an order"},
#     {"timestamp": "09:52", "text": "for 2 cakes"},
#     {"timestamp": "09:53", "text": "nut-free please"}
# ]

# messages = [
#     {"timestamp": "10:00", "text": "Hey there"},
#     {"timestamp": "10:01", "text": "Any update on my order #1234?"},
#     {"timestamp": "10:02", "text": "I placed it two days ago"}
# ]

# messages = [
#     {"timestamp": "11:15", "text": "The cake I received was melted"},
#     {"timestamp": "11:16", "text": "Totally unacceptable"},
#     {"timestamp": "11:17", "text": "I want a refund or replacement"}
# ]

# messages = [
#     {"timestamp": "12:00", "text": "Hello?"},
#     {"timestamp": "12:10", "text": "Any update?"},
#     {"timestamp": "12:30", "text": "Please check my message"}
# ]

# messages = [
#     {"timestamp": "13:00", "text": "Hi"},
#     {"timestamp": "13:01", "text": "Do you offer sugar-free options?"},
#     {"timestamp": "13:02", "text": "Or eggless cakes?"}
# ]

messages = [
    {"timestamp": "14:00", "text": "I want to return my last order"},
    {"timestamp": "14:01", "text": "The size is wrong"},
    {"timestamp": "14:02", "text": "Can you help me with the refund process?"}
]


result = analyze_conversation(messages, business_type="bakery")

print("\n🎯 Final Agent Output:\n", result)
