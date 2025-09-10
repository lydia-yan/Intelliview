import os
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth, firestore
from backend.tools.sercret_manage import load_firebase_key

# Only initialize Firebase once
db = None

if os.getenv("CI") == "true":
    from unittest.mock import MagicMock
    db = MagicMock()
else:
    if not firebase_admin._apps:
        firebase_creds = load_firebase_key()
        cred = credentials.Certificate(firebase_creds)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
