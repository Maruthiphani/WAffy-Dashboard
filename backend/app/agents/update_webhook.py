import requests
import subprocess
import time
import os
import psycopg2
import logging
import sys
from dotenv import load_dotenv
from utils.encryption import decrypt_value

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "PaperPencil_TeSt_token123")
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
    ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", str(NGROK_PORT)],
   # stdout=subprocess.DEVNULL,
    #stderr=subprocess.DEVNULL,
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
    print("Fetching credentials for phone_number_id from Waffy database:", phone_number_id)
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
            r = requests.get(f"http://localhost:{NGROK_PORT}/webhook")
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
def update_webhook(callback_url, app_id, app_secret, verify_token=None):
    print("Starting webhook update process...")
    print("callback_url", callback_url)
    print("app_id", app_id)
    print("app_secret", app_secret)
    url = f"https://graph.facebook.com/v19.0/{app_id}/subscriptions"
    
    # Use the provided verify_token if available, otherwise fall back to the default
    token_to_use = verify_token if verify_token else VERIFY_TOKEN
    print(f"Using verify token: {'Custom token' if verify_token else 'Default token'}")
    
    params = {
        "access_token": f"{app_id}|{app_secret}",
        "object": "whatsapp_business_account",
        "callback_url": callback_url,
        "fields": "messages",
        "verify_token": token_to_use,
    }

    response = requests.post(url, data=params)
    print("Webhook response:", response.text)
    if response.status_code == 200:
        print("✅ Webhook updated successfully:", callback_url)
        return {
            "status": "success",
            "message": f"Webhook updated successfully: {callback_url}"
        }
    else:
        print("Failed to update webhook:", response.text)
        return {
            "status": "error",
            "message": "Webhook configuration was unsuccessful for the entered credentials. Please check the entered credentials again.",
            "details": response.text  # optional: can help in debugging
        }
    

# --- Master function to call everything ---
def run_auto_update_webhook(phone_number_id, app_id=None, app_secret=None, verify_token=None):
    print(f"Starting webhook update process for Phone Number ID: {phone_number_id}")

    # ---- Condition 1: phone_number_id is missing ----
    if not phone_number_id:
        logging.error("Webhook configuration was unsuccessful, because phone number id was not entered.")
        return {
            "status": "error",
            "message": "Webhook configuration was unsuccessful, because phone number id was not entered."
        }

    # 1. Check or start listener
    if not is_listener_running():
        start_listener()
        time.sleep(5)
        if not wait_for_local_server():
            print("Local FastAPI server not responding. Aborting.")
            return {"status": "error", "message": "Local server not up"}
    else:
        print("Listener server already running.")

    # 2. Check or start ngrok
    if not is_ngrok_running():
        start_ngrok()
        time.sleep(5)
    else:
        print("Ngrok is already running.")

    print("app_id", app_id)
    print("app_secret", app_secret)
    # 3. Fetch credentials if app_id and app_secret not provided
    if not app_id or not app_secret:
        creds = fetch_credentials_by_phone_number(phone_number_id)
        app_id = creds["APP_ID"]
        app_secret = creds["APP_SECRET"]
        print("Fetched credentials:", app_id, app_secret)

         # ---- Condition 2: phone_number_id provided but app_id or app_secret missing ----
        if (app_id is not None or app_secret is not None) and (not app_id or not app_secret):
            logging.error("Webhook configuration was unsuccessful, because app id or app secret credentials were not entered.")
            return {
                "status": "error",
                "message": "Webhook configuration was unsuccessful, because app id or app secret credentials were not entered."
            }

    # 4. Get forwarding URL
    forwarding_url = get_ngrok_url()
    if not forwarding_url:
        print("No forwarding URL found. Aborting.")
        return {"status": "error", "message": "No forwarding URL"}

    full_webhook_url = forwarding_url + WEBHOOK_URL_SUFFIX
    print(f"Full Webhook URL: {full_webhook_url}")

    # 5. Update webhook
    webhook_update_result=update_webhook(full_webhook_url, app_id, app_secret, verify_token)
    print("Webhook Update Result:", webhook_update_result["message"])
    if webhook_update_result["status"] == "error":
        return webhook_update_result  # return the detailed error message

    return {"status": "success", "webhook_url": full_webhook_url}


# --- Optional way to run if standalone ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        phone_number_id = sys.argv[1]
        run_auto_update_webhook(phone_number_id)
    else:
        print(" Phone number ID must be provided as command-line argument.")
