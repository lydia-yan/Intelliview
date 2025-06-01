import os
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Load .env from project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Get the Firebase key path from env
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
if not firebase_key_path:
    raise EnvironmentError("FIREBASE_KEY_PATH not set in .env")

# Resolve the full path in case it's relative
firebase_key_full_path = (project_root / firebase_key_path).resolve()

if not os.path.exists(firebase_key_full_path):
    raise FileNotFoundError(f"Firebase key file not found at {firebase_key_full_path}")

# Initialize Firebase (only if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate(str(firebase_key_full_path))
    firebase_admin.initialize_app(cred)

db = firestore.client()
