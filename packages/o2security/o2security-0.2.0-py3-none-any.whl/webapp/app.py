# webapp/app.py
import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from pathlib import Path
import sys
import requests # Used for making requests to AI APIs

# Add project root path to sys.path to find o2security module
# This assumes your directory structure is:
# /your_project_root
# |- o2security/
# |  |- core.py
# |  |- ai/
# |- webapp/
# |  |- app.py
# |  |- templates/
sys.path.append(str(Path(__file__).parent.parent))
from o2security.core import encrypt, decrypt, get_master_key, PROJECTS_DIR
# We will create these new modules for the AI functionality
# from o2security.ai import O2AI 

# --- Constants and Setup ---
app = Flask(__name__)
app.secret_key = os.urandom(24)
MASTER_KEY = get_master_key()

# Create directories if they don't exist
AI_PROJECTS_DIR = Path(__file__).parent / 'ai_projects'
PROJECTS_DIR.mkdir(exist_ok=True)
AI_PROJECTS_DIR.mkdir(exist_ok=True)

# --- Helper Functions for AI Projects ---
def get_ai_project_path(project_name: str) -> Path:
    """Returns the JSON file path for an AI project's config."""
    return AI_PROJECTS_DIR / f"{project_name}.json"

def load_ai_project_data(project_name: str) -> dict:
    """Loads AI project config from file."""
    file_path = get_ai_project_path(project_name)
    if not file_path.exists():
        return {}
    with open(file_path, 'r') as f:
        encrypted_data = json.load(f)
    
    decrypted_data = {}
    for key, value in encrypted_data.items():
        # We only decrypt values for display; API key remains encrypted
        # For simplicity in the web UI, we will decrypt non-sensitive data
        # In a real app, you might handle this differently.
        try:
            decrypted_data[key] = decrypt(value, MASTER_KEY)
        except Exception:
            decrypted_data[key] = "Error Decrypting" # Or handle error appropriately
    return decrypted_data


def save_ai_project_data(project_name: str, data: dict):
    """Encrypts and saves AI project config to file."""
    file_path = get_ai_project_path(project_name)
    encrypted_data = {}
    for key, value in data.items():
        encrypted_data[key] = encrypt(str(value), MASTER_KEY)
    
    with open(file_path, 'w') as f:
        json.dump(encrypted_data, f, indent=2)

# --- Helper Functions for Token Projects (Original) ---
def get_project_path(project_name: str) -> Path:
    return PROJECTS_DIR / f"{project_name}.json"

def load_project_data(project_name: str) -> dict:
    file_path = get_project_path(project_name)
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_project_data(project_name: str, data: dict):
    file_path = get_project_path(project_name)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# --- Token Project Routes (Original) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        if project_name and not get_project_path(project_name).exists():
            save_project_data(project_name, {})
            flash(f'Token Project "{project_name}" created successfully!', 'success')
        else:
            flash('Invalid project name or project already exists.', 'danger')
        return redirect(url_for('index'))
    
    projects = [p.stem for p in PROJECTS_DIR.glob('*.json')]
    return render_template('index.html', projects=projects)

@app.route('/project/<project_name>', methods=['GET', 'POST'])
def project_view(project_name):
    if not get_project_path(project_name).exists():
        return redirect(url_for('index'))

    if request.method == 'POST':
        token_key = request.form.get('token_key')
        token_value = request.form.get('token_value')
        if token_key and token_value:
            encrypted_value = encrypt(token_value, MASTER_KEY)
            data = load_project_data(project_name)
            data[token_key] = encrypted_value
            save_project_data(project_name, data)
            flash(f'Token "{token_key}" added successfully.', 'success')
        else:
            flash('Token name and value cannot be empty.', 'danger')
        return redirect(url_for('project_view', project_name=project_name))

    project_data = load_project_data(project_name)
    return render_template('project.html', project_name=project_name, tokens=project_data)

# --- AI Project Routes (New) ---
@app.route('/ai', methods=['GET', 'POST'])
def ai_dashboard():
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        if project_name and not get_ai_project_path(project_name).exists():
            # Create an empty config file
            save_ai_project_data(project_name, {
                "SYSTEM_PROMPT": "You are a helpful assistant.",
                "BASE_URL": "",
                "API_KEY": ""
            })
            flash(f'AI Project "{project_name}" created successfully!', 'success')
        else:
            flash('Invalid project name or project already exists.', 'danger')
        return redirect(url_for('ai_dashboard'))
    
    projects = [p.stem for p in AI_PROJECTS_DIR.glob('*.json')]
    return render_template('ai_dashboard.html', projects=projects)

@app.route('/ai/<project_name>', methods=['GET', 'POST'])
def ai_project_view(project_name):
    if not get_ai_project_path(project_name).exists():
        flash(f'AI Project "{project_name}" not found.', 'danger')
        return redirect(url_for('ai_dashboard'))

    if request.method == 'POST':
        # In the HTML, we submit multiple inputs with the same names
        keys = request.form.getlist('config_key')
        values = request.form.getlist('config_value')
        
        # Load existing data
        data = load_ai_project_data(project_name)

        for key, value in zip(keys, values):
            # Don't save an empty password field, keep the old one
            if key == "API_KEY" and not value:
                continue
            data[key] = value

        save_ai_project_data(project_name, data)
        flash('AI configuration saved successfully.', 'success')
        return redirect(url_for('ai_project_view', project_name=project_name))

    configs = load_ai_project_data(project_name)
    return render_template('ai_project_view.html', project_name=project_name, configs=configs)

# --- API Route for AI Chat (New) ---
@app.route('/api/ai/<project_name>/chat', methods=['POST'])
def ai_chat_api(project_name):
    if not get_ai_project_path(project_name).exists():
        return jsonify({"error": "Project not found"}), 404

    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # For now, we implement the logic directly. Later, this will use O2AI class.
        configs = load_ai_project_data(project_name)
        api_key = configs.get("API_KEY")
        base_url = configs.get("BASE_URL") or "https://api.openai.com/v1" # Default to OpenAI
        system_prompt = configs.get("SYSTEM_PROMPT")

        if not api_key:
            return jsonify({"error": "API Key is not configured for this project."}), 400

        # This is a sample payload for OpenAI's API. It may need to be adjusted for other services.
        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                # In a real app, you'd load conversation history here from the SQLite DB
                {"role": "user", "content": user_message}
            ]
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Make the request to the AI service
        api_response = requests.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        api_response.raise_for_status() # Raise an exception for bad status codes
        
        response_data = api_response.json()
        ai_reply = response_data['choices'][0]['message']['content']

        # Here you would save the user_message and ai_reply to the encrypted SQLite DB
        # memory = O2AI(project_name).memory
        # memory.add_message('user', user_message)
        # memory.add_message('assistant', ai_reply)

        return jsonify({"reply": ai_reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API request failed: {e}"}), 500
    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {e}"}), 500


if __name__ == '__main__':
    # Use a different port to avoid conflict with other apps
    app.run(debug=True, port=5001)
