#!/usr/bin/env python
"""
Simple test script for interview questions search agent
This script uses a predefined job description to search for relevant interview questions
"""

import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from backend.agents.search import search_interview_questions
from backend.agents.search.test.mock_data import create_mock_data

def run_basic_test():
    """
    Run a basic test using predefined job description data
    """
    # Set environment variables
    os.environ["GOOGLE_CLOUD_PROJECT"] = "xxx"  # Replace with your project ID
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    print("\n=== Interview Questions Search Test ===\n")
    
    # Get mock job description data
    job_data = create_mock_data()
    
    print(f"Job Description: {job_data['job_description']}")
    
    print("\nThis may take a minute or two as the agent performs multiple searches...\n")
    
    # Call search function
    try:
        result = search_interview_questions(job_data["job_description"])
        
        
        print(f"\n✅ Search completed successfully!")
        print("\n=== SEARCH RESULTS ===\n")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Search failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_basic_test() 