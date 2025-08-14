# webapp/cli.py
import sys
from pathlib import Path

# Add project root path to sys.path to find o2security module
# This is necessary when running the script directly
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Now we can import the app
from webapp.app import app

def main():
    """Main function to run the server from command line."""
    print("🚀 O₂Security server is running...")
    print("🌐 Access the dashboard at http://127.0.0.1:5001")
    try:
        # Run Flask server
        app.run(host='0.0.0.0', port=5001)
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")

if __name__ == '__main__':
    main()