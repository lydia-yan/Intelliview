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


class PDFConfig:
    """
    PDF processing configuration settings
    """
    # File size limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Supported file extensions
    ALLOWED_EXTENSIONS = {'.pdf'}
    
    # Text quality thresholds
    MIN_TEXT_LENGTH = 30  # minimum characters for valid text
    MIN_TEXT_QUALITY_CHARS = 50  # minimum characters for quality analysis
    MIN_TEXT_QUALITY_WORDS = 5   # minimum words for quality analysis
    
    # PDF processing limits
    MAX_PAGE_COUNT = 50  # maximum pages to process