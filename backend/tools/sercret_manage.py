from google.cloud import secretmanager
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
FIREBASE_KEY_PATH = os.getenv("FIREBASE_KEY_PATH")

if not GOOGLE_CLOUD_PROJECT:
    raise EnvironmentError("GOOGLE_CLOUD_PROJECT not set in .env")

def load_firebase_key():
    if os.getenv("CI") == "true" or (FIREBASE_KEY_PATH and "dummy.json" in FIREBASE_KEY_PATH):
        return None  # return a fake value so imports don’t crash
    if FIREBASE_KEY_PATH:
        # Read from local file
        key_path = project_root / FIREBASE_KEY_PATH
        if not key_path.exists():
            raise FileNotFoundError(f"Firebase key file not found at {key_path}")
        with open(key_path, 'r') as f:
            return json.load(f)
    else:
        # Read from Secret Manager
        try:
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/FIREBASE_KEY_JSON/versions/latest"
            response = client.access_secret_version(request={"name": name})
            secret_str = response.payload.data.decode("utf-8")
            return json.loads(secret_str)
        except Exception as e:
            raise Exception(f"Failed to load Firebase key from Secret Manager: {str(e)}")