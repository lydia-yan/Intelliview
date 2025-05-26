"""
Backend configuration management
Provides unified environment variable setup for all agents
"""

import os
from dotenv import load_dotenv
from pathlib import Path

def set_google_cloud_env_vars():
    """
    Load Google Cloud environment variables from backend/.env file
    """
    backend_dir = Path(__file__).parent
    env_file_path = backend_dir / ".env"
    load_dotenv(env_file_path)
