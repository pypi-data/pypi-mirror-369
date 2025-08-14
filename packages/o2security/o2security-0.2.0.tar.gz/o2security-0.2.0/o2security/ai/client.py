# o2security/ai/client.py

import sys
from pathlib import Path
import requests
import json

# Add project root to sys.path to find the core module
# This is necessary for the library to find its own modules
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from o2security.core import get_master_key, decrypt
from .memory import AIMemory

# The webapp uses a different path, so we define AI_PROJECTS_DIR for library use
# This assumes a standard installation or development environment.
# A more robust solution might use package resources.
LIB_AI_PROJECTS_DIR = Path.home() / '.o2security' / 'ai_projects'
LIB_AI_PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


class O2AI:
    """
    A secure client for interacting with AI models, using O₂Security for
    credential and memory management.
    """

    def __init__(self, project_name: str):
        """
        Initializes the AI client for a specific project.

        Args:
            project_name (str): The name of the AI project configured in the web UI.
        """
        if not project_name:
            raise ValueError("Project name cannot be empty.")

        self.project_name = project_name
        self._config_path = LIB_AI_PROJECTS_DIR / f"{self.project_name}.json"
        
        if not self._config_path.exists():
            # A fallback for when the webapp path is used in development
            webapp_path = Path(__file__).parent.parent.parent / 'webapp' / 'ai_projects' / f"{self.project_name}.json"
            if webapp_path.exists():
                 self._config_path = webapp_path
            else:
                raise FileNotFoundError(
                    f"Configuration for AI project '{self.project_name}' not found. "
                    f"Please create it via the web dashboard."
                )

        self._master_key = get_master_key()
        self.memory = AIMemory(self.project_name, self._master_key)
        self._load_config()

    def _load_config(self):
        """Loads and decrypts the configuration from the project's JSON file."""
        with open(self._config_path, 'r') as f:
            encrypted_configs = json.load(f)
        
        self.api_key = decrypt(encrypted_configs.get("API_KEY"), self._master_key)
        self.base_url = decrypt(encrypted_configs.get("BASE_URL"), self._master_key) or "https://api.openai.com/v1"
        self.system_prompt = decrypt(encrypted_configs.get("SYSTEM_PROMPT"), self._master_key)

    def set_system_prompt(self, prompt: str):
        """
        Overrides the system prompt for the current session.

        Args:
            prompt (str): The new system prompt.
        """
        self.system_prompt = prompt

    def chat(self, message: str, stream: bool = False) -> str:
        """
        Sends a message to the AI model and gets a response.

        Args:
            message (str): The user's message.
            stream (bool): Whether to stream the response (not implemented in this example).

        Returns:
            str: The AI's response message.
        """
        if not self.api_key:
            raise ValueError("API Key is not set for this project.")

        # Add user message to memory
        self.memory.add_message(role="user", content=message)

        # Prepare payload with history
        messages = self.memory.get_history(limit=10) # Get last 10 messages
        
        # Add system prompt to the start
        if self.system_prompt:
            messages.insert(0, {"role": "system", "content": self.system_prompt})

        payload = {
            "model": "gpt-3.5-turbo", # This could be made configurable
            "messages": messages
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            
            response_data = response.json()
            ai_reply = response_data['choices'][0]['message']['content']

            # Add AI response to memory
            self.memory.add_message(role="assistant", content=ai_reply)

            return ai_reply
        except requests.exceptions.RequestException as e:
            # You might want to log this error
            print(f"Error communicating with AI service: {e}")
            return "Sorry, I encountered an error trying to connect to the AI service."
        except (KeyError, IndexError) as e:
            print(f"Error parsing AI response: {e}")
            return "Sorry, I received an unexpected response from the AI service."

    def clear_memory(self):
        """Clears the conversation history for this project."""
        self.memory.clear_history()
        print("Conversation memory has been cleared.")

