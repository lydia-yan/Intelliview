#!/usr/bin/env python
"""
Interactive test script for resume summarizer
Shows the output of the resume summarizer agent for prompt evaluation
"""

import os
import json
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

# Import from parent directory
from backend.agents.summarizer import agent
from backend.agents.summarizer.test.mock_data import create_mock_data

def run_interactive_test():
    """
    Run a simple test showing the resume summarizer output
    """
    # Set environment variables for Vertex AI
    os.environ["GOOGLE_CLOUD_PROJECT"] = "xxx"  # Replace with your project ID
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
    
    print("Testing resume summarizer...")
    
    # Get test data and run summarizer
    mock_data = create_mock_data()
    
    try:
        result = agent.summarize_resume(
            mock_data["resume_text"],
            mock_data["linkedin_info"],
            mock_data["github_info"],
            mock_data["portfolio_info"],
            mock_data["additional_info"],
            mock_data["job_description"]
        )
        
        # Print formatted JSON result
        print("\n✅ Success! Here's the result:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_interactive_test() 