#!/usr/bin/env python
"""
Question generator test script
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
from backend.agents.question_generator import generate_custom_questions
from backend.agents.question_generator.test.mock_data import create_mock_data

def test_question_generator():
    """
    Test the question generation functionality
    """
    
    print("Testing question generator...")
    
    # Get test data
    mock_data_obj = create_mock_data()
    
    # Call question generation function
    try:
        result = generate_custom_questions(
            mock_data_obj["personal_summary"],
            mock_data_obj["industry_faqs"],
            mock_data_obj["num_questions"]
        )
                
        # Add assertions for pytest
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        
        # Check RecommendedQA structure
        for qa in result:
            assert "question" in qa
            assert "answer" in qa
            assert "tags" in qa
            
            # Check that question and answer are strings
            assert isinstance(qa["question"], str)
            assert isinstance(qa["answer"], str)
            
            # Check that answer is empty (will be filled by answer_generator)
            assert qa["answer"] == ""
            
            # Check that tags is a list
            assert isinstance(qa["tags"], list)
            assert len(qa["tags"]) > 0
            
            # Check that all tags are strings
            for tag in qa["tags"]:
                assert isinstance(tag, str)
        
        # Check that we have a reasonable number of questions
        expected_questions = mock_data_obj["num_questions"]
        assert len(result) <= expected_questions + 2  # Allow some flexibility
                
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise the exception for pytest to catch

if __name__ == "__main__":
    test_question_generator() 