"""
Utility functions for encrypting and decrypting sensitive data
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get encryption key from environment or use a default for development
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "waffy_encryption_key_for_development_only")

# Properly format the key for Fernet (must be 32 url-safe base64-encoded bytes)
# Generate a consistent key using SHA-256 hash (which produces 32 bytes)
def get_encryption_key():
    """
    Get or generate an encryption key for sensitive data.
    Uses a consistent method matching the one in main.py
    """
    digest = hashes.Hash(hashes.SHA256())
    digest.update(ENCRYPTION_KEY.encode())
    key_bytes = digest.finalize()
    
    # Convert to URL-safe base64-encoded format as required by Fernet
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return fernet_key

# Initialize Fernet cipher with the encryption key
def get_cipher():
    """Get the Fernet cipher for encryption/decryption"""
    key = get_encryption_key()
    return Fernet(key)

def encrypt_value(value):
    """
    Encrypt a sensitive value
    
    Args:
        value (str): The value to encrypt
        
    Returns:
        str: The encrypted value as a base64 string
    """
    if not value:
        return None
    
    cipher = get_cipher()
    encrypted_value = cipher.encrypt(value.encode())
    return base64.urlsafe_b64encode(encrypted_value).decode()

def decrypt_value(encrypted_value):
    """
    Decrypt an encrypted value
    
    Args:
        encrypted_value (str): The encrypted value as a base64 string
        
    Returns:
        str: The decrypted value
    """
    if not encrypted_value:
        return None
    
    cipher = get_cipher()
    try:
        # First try the method from main.py (direct decryption)
        try:
            return cipher.decrypt(encrypted_value.encode()).decode()
        except Exception:
            # If that fails, try the previous method (with base64 decoding)
            decrypted_value = cipher.decrypt(base64.urlsafe_b64decode(encrypted_value))
            return decrypted_value.decode()
    except Exception as e:
        logger.error(f"Error decrypting value: {e}")
        return None