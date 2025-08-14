# o2security/tokman.py
import json
from .core import decrypt, get_master_key, PROJECTS_DIR

class TokenManager:
    def __init__(self):
        self._master_key = get_master_key()
        self._current_project_data = None
        self._current_project_name = None

    def select_project(self, project_name: str):
        """Selects a project to read tokens from."""
        project_file = PROJECTS_DIR / f"{project_name}.json"
        if not project_file.exists():
            raise FileNotFoundError(f"Project '{project_name}' not found. Did you create it in the dashboard?")
        
        with open(project_file, 'r') as f:
            self._current_project_data = json.load(f)
        self._current_project_name = project_name
        print(f"✅ Project '{project_name}' selected successfully.")

    def get(self, token_name: str) -> str:
        """Decrypts and returns a token from the selected project."""
        if self._current_project_data is None:
            raise Exception("No project selected. Use `select_project` first.")
        
        encrypted_value = self._current_project_data.get(token_name)
        if encrypted_value is None:
            raise KeyError(f"Token '{token_name}' not found in project '{self._current_project_name}'.")
            
        return decrypt(encrypted_value, self._master_key)

# Create an instance for easy module-level usage
tokman = TokenManager()