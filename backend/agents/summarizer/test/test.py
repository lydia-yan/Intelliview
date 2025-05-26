#!/usr/bin/env python
"""
Resume summarizer test script
"""

import os
import json
import pytest
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

# Import unified config and set environment variables
from backend.config import set_google_cloud_env_vars

# Set up environment variables before importing agent
set_google_cloud_env_vars()

# Import from parent directory
from backend.agents.summarizer import agent
from backend.agents.summarizer.test.mock_data import create_mock_data

def test_resume_summarizer():
    """
    Test the resume summarization functionality
    """
    print("Testing resume summarizer...")
    
    # Get test data
    mock_data_obj = create_mock_data()
    
    # Call resume summarization function
    try:
        result = agent.summarize_resume(
            mock_data_obj["resume_text"],
            mock_data_obj["linkedin_info"],
            mock_data_obj["github_info"],
            mock_data_obj["portfolio_info"],
            mock_data_obj["additional_info"],
            mock_data_obj["job_description"]
        )
        
        # Add assertions for pytest
        assert result is not None
        assert "title" in result
        assert "resumeInfo" in result
        assert "linkedinInfo" in result
        assert "githubInfo" in result
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise the exception for pytest to catch

if __name__ == "__main__":
    test_resume_summarizer() 