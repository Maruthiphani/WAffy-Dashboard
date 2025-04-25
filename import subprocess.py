import subprocess
import time
import requests
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path="/Users/harsha/Desktop/latest_hackathon/WAffy-Dashboard/.env")

DATABASE_URL = os.getenv("DATABASE_URL")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_custom_token")
WEBHOOK_URL_SUFFIX = "/webhook"
NGROK_PORT = 8000

def start_listener():
    print("🚀 Starting listener agent...")
    subprocess.Popen(["uvicorn", "listener_agent:app", "--host", "0.0.0.0", "--port", str(NGROK_PORT)])

def start_ngrok():
    print("🌐 Starting ngrok tunnel...")
    subprocess.Popen(["ngrok", "http", str(NGROK_PORT)])

def fetch_credentials_by_phone_number(phone_number_id):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT app_id, app_secret, whatsapp_token
        FROM business_credentials
        WHERE phone_number_id = %s
    """, (phone_number_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise Exception("No credentials found for this phone_number_id")

    return {
        "APP_ID": row[0],
        "APP_SECRET": row[1],
        "WHATSAPP_TOKEN": row[2],
    }

def wait_for_local_server():
    print("⏳ Checking if local FastAPI server is up...")
    for _ in range(10):
        try:
            r = requests.get("http://localhost:8000/webhook")
            if r.status_code in [200, 400]:  # 400 expected from verify token mismatch
                return True
        except:
            pass
        time.sleep(1)
    return False

def get_ngrok_url():
    print("⏳ Waiting for ngrok to initialize...")
    for _ in range(10):
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            tunnels = response.json()["tunnels"]
            for tunnel in tunnels:
                if tunnel["proto"] == "https":
                    return tunnel["public_url"]
        except:
            pass
        time.sleep(1)
    return None

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
        print("✅ Webhook registered successfully:", callback_url)
    else:
        print("❌ Webhook registration failed:", response.text)

if __name__ == "__main__":
    phone_number_id = "599137786621519"

    start_listener()
    start_ngrok()
    time.sleep(5)

    if not wait_for_local_server():
        print("❌ Local FastAPI server is not responding. Aborting.")
        exit()

    forwarding_url = get_ngrok_url()
    if not forwarding_url:
        print("❌ Ngrok URL not available. Aborting.")
        exit()

    creds = fetch_credentials_by_phone_number(phone_number_id)
    full_webhook_url = forwarding_url + WEBHOOK_URL_SUFFIX
    update_webhook(full_webhook_url, creds["APP_ID"], creds["APP_SECRET"])
