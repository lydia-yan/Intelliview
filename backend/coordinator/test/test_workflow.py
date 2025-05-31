"""
Test script for the updated preparation workflow
"""

import asyncio
import json
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from preparation_workflow import run_preparation_workflow
from mock_data import create_mock_workflow_data

async def test_workflow():
    """Test the interview preparation workflow"""
    print("Starting interview preparation workflow test...")
    
    # Load test data from mock_data.py
    mock_data = create_mock_workflow_data()
    
    # Call the workflow with mock data
    result = await run_preparation_workflow(
        user_id=mock_data["user_id"],
        resume_text=mock_data["resume_text"],
        job_description=mock_data["job_description"],
        linkedin_link=mock_data["linkedin_link"],
        github_link=mock_data["github_link"],
        portfolio_link=mock_data["portfolio_link"],
        additional_info=mock_data["additional_info"],
        num_questions=50
    )
    
    print("Workflow completed!")
    print(f"Success: {result.get('success', False)}")
    print(f"User Email: {result.get('user_id', 'None')}")
    print(f"Generated Session ID: {result.get('session_id', 'None')}")
    print(f"Workflow ID: {result.get('workflow_id', 'None')}")
    
    if result.get("success"):
        print(f"Final Response: {result.get('final_response', 'No response')}")
        
        # Display session state keys
        session_state = result.get('session_state', {})
        if session_state:
            print(f"\nSession State Keys:")
            for key in session_state.keys():
                print(f"  - {key}")
        
        # Parse JSON strings to get actual data
        personal_summary_str = result.get('personal_summary', '{}')
        industry_faqs_str = result.get('industry_faqs', '{}')
        questions_data_str = result.get('questions_data', '[]')
        
        try:
            personal_summary = json.loads(personal_summary_str) if isinstance(personal_summary_str, str) else personal_summary_str
            industry_faqs = json.loads(industry_faqs_str) if isinstance(industry_faqs_str, str) else industry_faqs_str
            questions_data = json.loads(questions_data_str) if isinstance(questions_data_str, str) else questions_data_str
            
            print(f"\nPersonal Summary Keys: {list(personal_summary.keys()) if isinstance(personal_summary, dict) else 'None'}")
            print(f"Industry FAQs Keys: {list(industry_faqs.keys()) if isinstance(industry_faqs, dict) else 'None'}")
            print(f"Questions Data Type: {type(questions_data)}")
            if isinstance(questions_data, list):
                print(f"Number of Questions: {len(questions_data)}")
            elif isinstance(questions_data, dict) and 'error' not in questions_data:
                print(f"Questions Data Keys: {list(questions_data.keys())}")
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON results: {e}")
            print(f"Raw personal_summary: {personal_summary_str[:100]}...")
            print(f"Raw industry_faqs: {industry_faqs_str[:100]}...")
            print(f"Raw questions_data: {questions_data_str[:100]}...")
        
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(test_workflow()) 