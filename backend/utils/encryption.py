"""
Utility functions for encrypting and decrypting sensitive data
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get encryption key from environment or generate a new one
def get_encryption_key():
    """
    Get or generate an encryption key for sensitive data.
    Uses an environment variable if available, otherwise generates a new key.
    """
    key = os.getenv("ENCRYPTION_KEY")
    
    if not key:
        # Generate a key and save it to .env
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        # Use a default password if none is provided
        password = os.getenv("ENCRYPTION_PASSWORD", "waffy-secure-default-key")
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Save the key to .env file
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        with open(env_path, 'a') as f:
            f.write(f"\nENCRYPTION_KEY={key.decode()}\n")
        
        print("Generated new encryption key and saved to .env")
    else:
        # Convert the string key back to bytes
        key = key.encode() if isinstance(key, str) else key
    
    return key

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
        decrypted_value = cipher.decrypt(base64.urlsafe_b64decode(encrypted_value))
        return decrypted_value.decode()
    except Exception as e:
        print(f"Error decrypting value: {e}")
        return None
