# o2security/core.py
import os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64

# Paths for storing master key and data
DATA_DIR = Path.home() / ".o2security"
KEY_FILE = DATA_DIR / "master.key"
PROJECTS_DIR = DATA_DIR / "projects"

def get_master_key() -> bytes:
    """
    Reads master key from environment variable or local file.
    If neither exists, creates and stores a new key.
    """
    DATA_DIR.mkdir(exist_ok=True)
    
    key_b64 = os.environ.get("O2_SECURITY_KEY")
    if key_b64:
        return base64.urlsafe_b64decode(key_b64)
        
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    else:
        print("⚠️ Master key not found. Creating a new one...")
        print(f"🔑 Key storage path: {KEY_FILE}")
        print("🚨 Keep this file secure and make backups!")
        new_key = os.urandom(32)  # 256-bit key
        KEY_FILE.write_bytes(new_key)
        return new_key

def encrypt(data: str, key: bytes) -> str:
    """Encrypts a string using AES-256-GCM."""
    iv = os.urandom(12)  # GCM recommends a 12-byte IV
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    
    ciphertext = encryptor.update(data.encode('utf-8')) + encryptor.finalize()
    # Store IV and tag along with ciphertext
    return base64.urlsafe_b64encode(iv + encryptor.tag + ciphertext).decode('utf-8')

def decrypt(encrypted_data_b64: str, key: bytes) -> str:
    """Decrypts an AES-256-GCM encrypted string."""
    try:
        encrypted_data = base64.urlsafe_b64decode(encrypted_data_b64)
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        decryptor = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()
        
        return (decryptor.update(ciphertext) + decryptor.finalize()).decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return "DECRYPTION_ERROR"

# Ensure directories exist when module is imported
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)