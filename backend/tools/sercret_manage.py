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
if not GOOGLE_CLOUD_PROJECT:
    raise EnvironmentError("GOOGLE_CLOUD_PROJECT not set in .env")

def load_firebase_key():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{GOOGLE_CLOUD_PROJECT}/secrets/FIREBASE_KEY_JSON/versions/latest"
    response = client.access_secret_version(request={"name": name})
    secret_str = response.payload.data.decode("utf-8")
    return json.loads(secret_str)