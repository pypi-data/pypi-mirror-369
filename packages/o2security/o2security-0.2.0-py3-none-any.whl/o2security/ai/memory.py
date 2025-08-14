# o2security/ai/memory.py
import sqlite3
import json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib
import base64

# Directory to store memory databases
MEMORY_DIR = Path.home() / '.o2security' / 'ai_memory'
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

class AIMemory:
    """
    Manages encrypted conversation history in a local SQLite database.
    Each project gets its own database file.
    """
    BLOCK_SIZE = 16 # 16 bytes for AES

    def __init__(self, project_name: str, master_key: bytes):
        """
        Initializes the memory store for a project.

        Args:
            project_name (str): The name of the AI project.
            master_key (bytes): The master encryption key from o2security.core.
        """
        db_path = MEMORY_DIR / f"{project_name}.db"
        self._conn = sqlite3.connect(db_path)
        self._cursor = self._conn.cursor()
        self._create_table()
        
        # Derive a specific key for this memory instance from the master key
        self._encryption_key = hashlib.sha256(master_key + project_name.encode()).digest()

    def _create_table(self):
        """Creates the 'history' table if it doesn't exist."""
        self._cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                encrypted_message TEXT NOT NULL
            )
        """)
        self._conn.commit()

    def _encrypt(self, plain_text_data: dict) -> str:
        """Encrypts a dictionary using AES-256-CBC."""
        data_bytes = json.dumps(plain_text_data).encode('utf-8')
        cipher = AES.new(self._encryption_key, AES.MODE_CBC)
        iv = cipher.iv
        encrypted_data = cipher.encrypt(pad(data_bytes, self.BLOCK_SIZE))
        # Return IV and encrypted data as a single base64 string
        return base64.b64encode(iv + encrypted_data).decode('utf-8')

    def _decrypt(self, encrypted_text: str) -> dict:
        """Decrypts a base64 string to a dictionary."""
        encrypted_blob = base64.b64decode(encrypted_text)
        iv = encrypted_blob[:self.BLOCK_SIZE]
        encrypted_data = encrypted_blob[self.BLOCK_SIZE:]
        cipher = AES.new(self._encryption_key, AES.MODE_CBC, iv)
        decrypted_bytes = unpad(cipher.decrypt(encrypted_data), self.BLOCK_SIZE)
        return json.loads(decrypted_bytes.decode('utf-8'))

    def add_message(self, role: str, content: str):
        """Encrypts and adds a message to the history."""
        message_data = {"role": role, "content": content}
        encrypted_message = self._encrypt(message_data)
        self._cursor.execute("INSERT INTO history (encrypted_message) VALUES (?)", (encrypted_message,))
        self._conn.commit()

    def get_history(self, limit: int = 10) -> list[dict]:
        """Retrieves and decrypts the last N messages from history."""
        self._cursor.execute("SELECT encrypted_message FROM history ORDER BY id DESC LIMIT ?", (limit,))
        rows = self._cursor.fetchall()
        # Decrypt and reverse the order to be chronological
        return [self._decrypt(row[0]) for row in reversed(rows)]

    def clear_history(self):
        """Deletes all records from the history table."""
        self._cursor.execute("DELETE FROM history")
        self._conn.commit()

    def __del__(self):
        """Ensures the database connection is closed when the object is destroyed."""
        if self._conn:
            self._conn.close()

