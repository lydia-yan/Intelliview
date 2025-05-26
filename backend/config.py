"""
Backend configuration management
Provides unified environment variable setup for all agents
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from google.genai import Client

def set_google_cloud_env_vars():
    """
    Load Google Cloud environment variables from backend/.env file
    """
    backend_dir = Path(__file__).parent
    env_file_path = backend_dir / ".env"
    load_dotenv(env_file_path)

def get_google_ai_client():
    """
    Create and return a configured Google AI client
    Call this function in each agent to get a ready-to-use client
    """
    return Client(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
        vertexai=os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True").lower() == "true"
    )
