# import requests
# import os
# import psycopg2
# from dotenv import load_dotenv

# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")
# VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_custom_token")
# #WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
# #APP_ID = os.getenv("APP_ID")
# #APP_SECRET = os.getenv("APP_SECRET")
# WEBHOOK_URL_SUFFIX = "/webhook"
# PHONE_NUMBER_ID="599137786621519"

# def fetch_credentials_by_phone_number(PHONE_NUMBER_ID):
#     conn = psycopg2.connect(DATABASE_URL)
#     cursor = conn.cursor()
#     cursor.execute("""
#         SELECT app_id, app_secret, whatsapp_token
#         FROM business_credentials
#         WHERE phone_number_id = %s
#     """, (PHONE_NUMBER_ID,))
#     row = cursor.fetchone()
#     cursor.close()
#     conn.close()

#     if not row:
#         raise Exception("No credentials found for this phone_number_id")

#     return {
#         "APP_ID": row[0],
#         "APP_SECRET": row[1],
#         "WHATSAPP_TOKEN": row[2],
#     }

# # Get ngrok public forwarding URL
# def get_ngrok_url():
#     try:
#         response = requests.get("http://127.0.0.1:4040/api/tunnels")
#         tunnels = response.json()["tunnels"]
#         for tunnel in tunnels:
#             if tunnel["proto"] == "https":
#                 return tunnel["public_url"]
#     except Exception as e:
#         print("Error getting ngrok URL:", e)
#     return None

# # Subscribe or update the webhook
# def update_webhook(callback_url, APP_ID, APP_SECRET):
#     url = f"https://graph.facebook.com/v19.0/{APP_ID}/subscriptions"
#     params = {
#         "access_token": f"{APP_ID}|{APP_SECRET}",
#         "object": "whatsapp_business_account",
#         "callback_url": callback_url,
#         "fields": "messages",
#         "verify_token": VERIFY_TOKEN,
#     }

#     response = requests.post(url, data=params)
#     if response.status_code == 200:
#         print("✅ Webhook updated successfully:", callback_url)
#     else:
#         print("Failed to update webhook:", response.text)

# if __name__ == "__main__":
#     forwarding_url = get_ngrok_url()
#     if forwarding_url:
#         full_webhook_url = forwarding_url + WEBHOOK_URL_SUFFIX
#         update_webhook(full_webhook_url, creds["APP_ID"], creds["APP_SECRET"])
#     else:
#         print("No forwarding URL found.")
import requests
import os
import psycopg2
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_custom_token")
WEBHOOK_URL_SUFFIX = "/webhook"

# Fetch credentials for a given phone_number_id
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
        print("❌ Failed to update webhook:", response.text)

# Main script entry point
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage: python Auto_Update_Webhook.py <phone_number_id>")
        sys.exit(1)

    phone_number_id = sys.argv[1]
    creds = fetch_credentials_by_phone_number(phone_number_id)
    forwarding_url = get_ngrok_url()

    if forwarding_url:
        full_webhook_url = forwarding_url + WEBHOOK_URL_SUFFIX
        update_webhook(full_webhook_url, creds["APP_ID"], creds["APP_SECRET"])
    else:
        print("❌ No forwarding URL found.")
