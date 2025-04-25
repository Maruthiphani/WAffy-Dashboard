import json
import sys
import os
import uuid
import getpass
from datetime import datetime
from agents.logger_agent import process_whatsapp_messages, LoggerAgent

# Generate unique message IDs for testing
def generate_test_message_id():
    return f"wamid.test_{uuid.uuid4().hex[:12]}"

# Sample test data
test_messages = [
    {
        "timestamp": "2025-04-22 19:28:15",
        "raw_timestamp_utc": 1745350095,
        "message_id": generate_test_message_id(),
        "message_type": "text",
        "customer_id": "447778596773",
        "sender": "447778596773",
        "customer_name": "Akanksha",
        "message": "hi",
        "predicted_category": "greeting",
        "priority": "low",
        "extracted_info": {},
        "context": [],
        "business_phone_number": "15556454320",
        "business_phone_id": "574048935800997"
    },
    {
        "message": "can i place an order",
        "predicted_category": "new order",
        "priority": "high",
        "extracted_info": {},
        "context": ["hi"],
        "customer_id": "447778596773",
        "sender": "447778596773",
        "timestamp": "2025-04-22 19:29:15",
        "message_id": generate_test_message_id(),
    },
    {
        "message": "for 2 cakes",
        "predicted_category": "new order",
        "priority": "moderate",
        "extracted_info": {
            "quantity": "2",
            "product_type": "cakes"
        },
        "context": ["hi", "can i place an order"],
        "customer_id": "447778596773",
        "sender": "447778596773",
        "timestamp": "2025-04-22 19:30:15",
        "message_id": generate_test_message_id(),
    },
    {
        "message": "nut-free please",
        "predicted_category": "order modification",
        "priority": "high",
        "extracted_info": {
            "allergy_info": "nut-free",
            "previous_order_details_needed": "true"
        },
        "context": ["hi", "can i place an order", "for 2 cakes"],
        "customer_id": "447778596773",
        "sender": "447778596773",
        "timestamp": "2025-04-22 19:31:15",
        "message_id": generate_test_message_id(),
    }
]

class TestLoggerAgent(LoggerAgent):
    """Extended LoggerAgent for testing purposes"""
    
    def __init__(self, user_id, hubspot_token=None):
        """Initialize with optional HubSpot token for testing"""
        super().__init__(user_id)
        
        # Override user settings if HubSpot token is provided
        if hubspot_token and self.user_settings:
            self.user_settings["crm_type"] = "hubspot"
            self.user_settings["hubspot_access_token"] = hubspot_token
            print(f"Using provided HubSpot Access Token for testing")
    
    def _store_messages(self, messages):
        """Override to skip database storage during testing"""
        print("Skipping database storage for testing")
        return
    
    def _process_excel(self, messages):
        """Process messages for Excel export"""
        try:
            # Create timestamp for filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Process customers
            customers_data = []
            messages_data = []
            orders_data = []
            
            # Extract unique customers
            unique_customers = {}
            for msg in messages:
                customer_id = msg.get("customer_id", msg.get("sender"))
                if not customer_id or customer_id in unique_customers:
                    continue
                
                unique_customers[customer_id] = {
                    "customer_id": customer_id,
                    "name": msg.get("customer_name", ""),
                    "last_message_timestamp": msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
                }
            
            # Add customers to data
            customers_data.extend(unique_customers.values())
            
            # Process messages
            for msg in messages:
                if "message" not in msg:
                    continue
                
                messages_data.append({
                    "message_id": msg.get("message_id", ""),
                    "customer_id": msg.get("customer_id", msg.get("sender", "")),
                    "timestamp": msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                    "message": msg.get("message", ""),
                    "predicted_category": msg.get("predicted_category", ""),
                    "priority": msg.get("priority", ""),
                    "extracted_info": json.dumps(msg.get("extracted_info", {})),
                    "context": json.dumps(msg.get("context", []))
                })
                
                # Check if this is an order-related message
                if msg.get("predicted_category") in ["new order", "order modification"]:
                    orders_data.append({
                        "customer_id": msg.get("customer_id", msg.get("sender", "")),
                        "timestamp": msg.get("timestamp", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                        "message": msg.get("message", ""),
                        "extracted_info": json.dumps(msg.get("extracted_info", {})),
                        "status": "new"
                    })
            
            # Save to Excel files
            if customers_data:
                self._save_to_excel(customers_data, "customers", timestamp)
            
            if messages_data:
                self._save_to_excel(messages_data, "messages", timestamp)
            
            if orders_data:
                self._save_to_excel(orders_data, "orders", timestamp)
            
            return {
                "status": "success", 
                "message": f"Exported data to Excel files",
                "files": {
                    "customers": f"customers_{timestamp}.xlsx" if customers_data else None,
                    "messages": f"messages_{timestamp}.xlsx" if messages_data else None,
                    "orders": f"orders_{timestamp}.xlsx" if orders_data else None
                }
            }
            
        except Exception as e:
            print(f"Error processing Excel export: {e}")
            return {"status": "error", "message": str(e)}

def main():
    """Run the logger agent with test data"""
    # Check if a user ID was provided as a command line argument
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        # Default test user ID - replace with a valid user ID from your database
        user_id = input("Enter a valid user ID (Clerk ID): ")
    
    # Ask for CRM type
    crm_type = input("Which CRM to test? (hubspot/excel) [default: excel]: ").lower() or "excel"
    
    # If HubSpot is selected, ask for an access token
    hubspot_token = None
    if crm_type == "hubspot":
        print("\nTo test HubSpot integration, you need a Private App Access Token.")
        print("You can create one at: https://app.hubspot.com/settings/integrations/private-apps")
        hubspot_token = getpass.getpass("Enter your HubSpot Private App Access Token: ")
        if not hubspot_token:
            print("No token provided. Falling back to Excel export.")
            crm_type = "excel"
        
        # Ask if we should test ticket creation
        test_tickets = input("Test ticket creation for high-priority messages? (y/n) [default: y]: ").lower() != "n"
        if test_tickets:
            # Ensure all messages are high priority for testing
            for msg in test_messages:
                msg["priority"] = "high"
            print("Set all messages to high priority for ticket testing")
    
    print(f"\nRunning logger agent for user: {user_id}")
    print(f"Processing {len(test_messages)} test messages...")
    print(f"CRM type: {crm_type}")
    
    # Create a test instance of LoggerAgent
    agent = TestLoggerAgent(user_id, hubspot_token)
    
    # Force CRM type if Excel is selected
    if crm_type == "excel" and agent.user_settings:
        print(f"Original CRM type: {agent.user_settings.get('crm_type', 'None')}")
        agent.user_settings["crm_type"] = "excel"
        print(f"Forced CRM type to: excel")
    
    # Process the test messages
    if crm_type == "excel":
        result = agent._process_excel(test_messages)
    else:
        # Process with HubSpot
        result = agent._process_hubspot(test_messages)
    
    # Print the result
    print("\nResult:")
    print(json.dumps(result, indent=2))
    
    # If Excel files were created, show their location
    if crm_type == "excel" and result.get("status") == "success" and "files" in result:
        excel_dir = os.path.join(os.getcwd(), "excel_exports")
        if os.path.exists(excel_dir):
            print(f"\nExcel files directory: {excel_dir}")
            files = os.listdir(excel_dir)
            if files:
                print("Generated files:")
                for file in files:
                    if file.endswith(".xlsx"):
                        file_path = os.path.join(excel_dir, file)
                        file_size = os.path.getsize(file_path)
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        print(f"  - {file} ({file_size} bytes, modified: {file_time})")

if __name__ == "__main__":
    main()
