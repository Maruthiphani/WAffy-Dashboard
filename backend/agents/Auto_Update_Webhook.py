import requests
import subprocess
import time
import os
import psycopg2
import sys
from dotenv import load_dotenv
from Util import decrypt_value  

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_custom_token")
WEBHOOK_URL_SUFFIX = "/webhook"
NGROK_PORT = os.getenv("NGROK_PORT")

#Checking if the listener server is already up
def is_listener_running():
    try:
        r = requests.get(f"http://127.0.0.1:{NGROK_PORT}/docs", timeout=2)
        return r.status_code == 200 or r.status_code == 404  # 404 is fine if /docs doesn't exist
    except:
        return False

#Starting the listener server
def start_listener():
    print("Starting listener agent...")
    #subprocess.Popen(["uvicorn", "listener_agent:app", "--host", "0.0.0.0", "--port", str(NGROK_PORT)])
    subprocess.Popen(
    ["uvicorn", "listener_agent:app", "--host", "0.0.0.0", "--port", str(NGROK_PORT)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True
)

#Checking if the ngrok tunnel is already up
def is_ngrok_running():
    try:
        r = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        return r.status_code == 200
    except:
        return False

#Starting the ngrok tunnel
def start_ngrok():
    print("Starting ngrok tunnel...")
    #subprocess.Popen(["ngrok", "http", str(NGROK_PORT)])
    subprocess.Popen(
    ["ngrok", "http", str(NGROK_PORT)],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    start_new_session=True
)

# Fetch credentials for a given phone_number_id
def fetch_credentials_by_phone_number(phone_number_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT whatsapp_app_id, whatsapp_app_secret, whatsapp_api_key
        FROM user_settings
        WHERE whatsapp_phone_number_id = %s
    """, (phone_number_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise Exception("No credentials found for this phone_number_id")

    return {
        
        "APP_ID": decrypt_value(row[0]),
        "APP_SECRET": decrypt_value(row[1]),
        "WHATSAPP_TOKEN": decrypt_value(row[2]),
    }



#Checking if local FastAPI server is up.
def wait_for_local_server():
    print("Checking if local FastAPI server is up...")
    for _ in range(10):
        try:
            r = requests.get("http://localhost:8000/webhook")
            if r.status_code in [200, 400]:  # 400 expected from verify token mismatch
                return True
        except:
            pass
        time.sleep(1)
    return False

# Get ngrok public forwarding URL
def get_ngrok_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("Error getting ngrok URL:", e)
    return None

# Register the webhook with Meta
def update_webhook(callback_url, app_id, app_secret):
    url = f"https://graph.facebook.com/v19.0/{app_id}/subscriptions"
    params = {
        "access_token": f"{app_id}|{app_secret}",
        "object": "whatsapp_business_account",
        "callback_url": callback_url,
        "fields": "messages",
        "verify_token": VERIFY_TOKEN,
    }

    response = requests.post(url, data=params)
    if response.status_code == 200:
        print("✅ Webhook updated successfully:", callback_url)
    else:
        print("Failed to update webhook:", response.text)

# Main script entry point
if __name__ == "__main__":

    #below line is only for testing purpose. Need to remove it after testing
    #phone_number_id = "599137786621519"
    #phone_number_id = "599137786621519"

    # Check if listener already running
    if is_listener_running():
        print("Listener server already running.")
    else:
        start_listener()
        time.sleep(5)
   
    #Checking if local FastAPI server is up.
    if not wait_for_local_server():
        print("Local FastAPI server not responding. Aborting.")
        exit()

   #Checking if the ngrok tunnel is already up
    if not is_ngrok_running():
        start_ngrok()
        time.sleep(5)
    else:
        print("Ngrok is already running.")

    creds = fetch_credentials_by_phone_number(phone_number_id)
    forwarding_url = get_ngrok_url()

    if forwarding_url:
        full_webhook_url = forwarding_url + WEBHOOK_URL_SUFFIX
        # Function call to register the webhook with Meta
        update_webhook(full_webhook_url, creds["APP_ID"], creds["APP_SECRET"])
    else:
        print("No forwarding URL found. Aborting.")
