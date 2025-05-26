#!/usr/bin/env python
"""
Interactive test script for question generator agent
Shows the output of the question generator agent for prompt evaluation
"""

import os
import json
import sys

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

# Import from parent directory

from backend.config import set_google_cloud_env_vars

# Set up environment variables before importing agent
set_google_cloud_env_vars()

# Import from parent directory
from backend.agents.question_generator import generate_custom_questions
from backend.agents.question_generator.test.mock_data import create_mock_data

def run_interactive_test():
    """
    Run a simple test showing the question generator output
    """
    # Set environment variables using config (automatically loads from .env)
    set_google_cloud_env_vars()
    
    print("Testing question generator...")
    
    # Get test data
    mock_data = create_mock_data()
    
    print(f"\n=== Input Data Summary ===")
    print(f"Candidate: {mock_data['personal_summary']['title']}")
    print(f"Target Role: {mock_data['industry_faqs']['jobTitle']}")
    print(f"Industry: {mock_data['industry_faqs']['industry']}")
    print(f"Questions to Generate: {mock_data['num_questions']}")
    
    print(f"\nThis may take a minute or two as the agent analyzes the data and generates questions...\n")
    
    try:
        result = generate_custom_questions(
            mock_data["personal_summary"],
            mock_data["industry_faqs"],
            mock_data["num_questions"]
        )
        
        # Print formatted result
        print("\nSuccess! Here's the result:")
        print("=" * 80)
        
        if isinstance(result, list):
            print(f"\nGENERATED QUESTIONS ({len(result)} questions)")
            for i, qa in enumerate(result, 1):
                print(f"\n--- Question {i} ---")
                print(f"Question: {qa['question']}")
                print(f"Answer: {qa['answer']}")
                print(f"Tags: {', '.join(qa['tags'])}")
        else:
            print(f"\nUnexpected result format: {type(result)}")
        
        print("\n" + "=" * 80)
        print("\nRaw JSON Output (RecommendedQA format):")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\nTest failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_interactive_test() 