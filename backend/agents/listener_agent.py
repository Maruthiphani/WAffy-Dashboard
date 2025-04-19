def listen_for_new_message():
    """
    I am simulating a listener agent that returns a new message,
    customer ID, and sender (e.g. WhatsApp number).
    """
    print("Listening for new WhatsApp message...\n")

    # Simulate an incoming payload
    message = input("Enter message: ")
    customer_id = input("Enter customer ID: ")
    sender = input("Enter sender (e.g., phone or email): ")

    return {
        "message": message,
        "customer_id": customer_id,
        "sender": sender
    }
