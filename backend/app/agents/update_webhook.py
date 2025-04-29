import requests
import time
import os
import psycopg2
import logging
import sys
from dotenv import load_dotenv
from utils.encryption import decrypt_value

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
NGROK_PORT = os.getenv("NGROK_PORT") 
forwarding_url = os.getenv("FORWARDING_URL")

# ----------------------------------------------
# Database Helper Functions
# ----------------------------------------------

# Fetch verify token for a given phone_number_id
def fetch_verify_token_by_phone_number(phone_number_id):
    print("Fetching credentials for phone_number_id from Waffy database:", phone_number_id)
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT whatsapp_verify_token
        FROM user_settings
        WHERE whatsapp_phone_number_id = %s
    """, (phone_number_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise Exception("No verify token found for this phone_number_id")

    return {
        "VERIFY_TOKEN": decrypt_value(row[0]),
    }

# Fetch credentials app id and app secret for a given phone_number_id
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
        "WHATSAPP_ACCESS_TOKEN": decrypt_value(row[2]),
    }

# ----------------------------------------------
# Meta API Integration
# ----------------------------------------------

# Register the webhook with Meta
def update_webhook(callback_url, app_id, app_secret, verify_token):
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
        "verify_token": verify_token,
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
    

# -----------------------------------------------
# Main Execution Logic
# -----------------------------------------------

# --- Master function to call everything ---
def run_auto_update_webhook(phone_number_id, app_id=None, app_secret=None, verify_token=None):
    print(f"Starting webhook update process for Phone Number ID: {phone_number_id}")
    print("app_id", app_id)
    print("app_secret", app_secret)
    print("verify_token", verify_token)

    # ---- Condition 1: if phone_number_id is missing ----
    if not phone_number_id:
        logging.error("Webhook configuration was unsuccessful, because phone number id was not entered.")
        return {
            "status": "error",
            "message": "Webhook configuration was unsuccessful, because phone number id was not entered."
        }

    print("app_id", app_id)
    print("app_secret", app_secret)

    # Fetch credentials if app_id and app_secret not provided
    if not app_id or not app_secret:
        creds = fetch_credentials_by_phone_number(phone_number_id)
        app_id = creds["APP_ID"]
        app_secret = creds["APP_SECRET"]
        print("Fetched credentials:", app_id, app_secret)

         # ---- Condition : phone_number_id provided but app_id or app_secret missing ----
        if (app_id is not None or app_secret is not None) and (not app_id or not app_secret):
            logging.error("Webhook configuration was unsuccessful, because app id or app secret credentials were not entered.")
            return {
                "status": "error",
                "message": "Webhook configuration was unsuccessful, because app id or app secret credentials were not entered."
            }

    #  Making sure the public-facing backend URL is set
    if not forwarding_url:
        print("No forwarding URL found in .env file. Aborting.")
        return {"status": "error", "message": "No forwarding URL"}

    # Construct the full webhook URL dynamically with phone_number_id
    WEBHOOK_URL_SUFFIX = "webhook/" + phone_number_id
    full_webhook_url = forwarding_url + WEBHOOK_URL_SUFFIX
    print(f"Full Webhook URL: {full_webhook_url}")

    #  Fetch verify_token from database
    if not verify_token:
        token_data = fetch_verify_token_by_phone_number(phone_number_id)
        verify_token = token_data["VERIFY_TOKEN"]
        print("Fetched whatsapp_verify_token:", verify_token,)

    # ---- Condition : when whatsapp_verify_token is missing in database ----
    if (verify_token is None):
        logging.error("Webhook configuration was unsuccessful, because whatsapp verify token credential was not entered.")
        return {
            "status": "error",
         "message": "Webhook configuration was unsuccessful, because whatsapp verify token credential was not entered."
     }    

    # webhook configuration,  Register the webhook
    webhook_update_result=update_webhook(full_webhook_url, app_id, app_secret, verify_token)
    print("Webhook Update Result:", webhook_update_result["message"])
    if webhook_update_result["status"] == "error":
        return webhook_update_result  # return the detailed error message

    return {"status": "success", "webhook_url": full_webhook_url}


# --- Optional way to run if standalone for testing purpose---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        phone_number_id = sys.argv[1]
        run_auto_update_webhook(phone_number_id)
    else:
        print(" Phone number ID must be provided as command-line argument.")
