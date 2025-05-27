#!/usr/bin/env python
"""
Interview questions search test script
"""

import os
import json
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from backend.agents.search import search_interview_questions
from backend.agents.search.test.mock_data import create_mock_data

# Import unified config
from backend.config import set_google_cloud_env_vars

# Load environment variables
set_google_cloud_env_vars()

def test_interview_questions_search():
    """
    Test the interview questions search functionality
    """
    # Get test data
    mock_data_obj = create_mock_data()
    
    # Call search function
    try:
        result = search_interview_questions(mock_data_obj["job_description"])
        
        print(json.dumps(result, indent=2))
        
        # Add assertions for pytest
        assert result is not None
        assert "jobTitle" in result
        assert "industry" in result
        assert "experienceLevel" in result
        assert "technicalQuestions" in result
        assert "behavioralQuestions" in result
        assert "interviewProcess" in result
        assert isinstance(result["technicalQuestions"], list)
        assert isinstance(result["behavioralQuestions"], list)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_interview_questions_search() 