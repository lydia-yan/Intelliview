#!/usr/bin/env python
"""
Interactive test for Answer Generator Agent
Provides formatted output for development and debugging
"""

import os, pytest
import sys
import json
if os.getenv("CI") == "true":
    pytest.skip("Skipping Firestore-dependent tests in CI", allow_module_level=True)

# Add project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from backend.agents.answer_generator.agent import generate_personalized_answers
from backend.agents.answer_generator.test.mock_data import create_mock_questions_from_generator
from backend.agents.question_generator.test.mock_data import create_mock_personal_summary
from backend.config import set_google_cloud_env_vars

def setup_environment():
    """Set up environment"""
    print("Answer Generator Agent - Interactive Test")
    print("=" * 50)
    print("Setting up environment...")
    set_google_cloud_env_vars()
    print("Environment ready")

def display_input_data(questions_data, personal_summary):
    """Display input data"""
    print(f"\nInput Data:")
    print(f"- Target Position: {personal_summary.get('title', 'Unknown')}")
    print(f"- Questions to Answer: {len(questions_data)}")

def display_results(agent_output):
    """Display agent results"""
    print(f"\nResults:")
    
    if isinstance(agent_output, dict) and "error" in agent_output:
        print(f"Error: {agent_output['error']}")
        return False
    
    if not isinstance(agent_output, list):
        print(f"Unexpected output type: {type(agent_output)}")
        return False
    
    print(f"Generated {len(agent_output)} personalized answers")
    
    # Display each answer
    for i, answer_item in enumerate(agent_output, 1):
        print(f"\n--- Answer {i} ---")
        
        if isinstance(answer_item, dict):
            question = answer_item.get('question', 'No question')
            answer = answer_item.get('answer', 'No answer')
            tags = answer_item.get('tags', [])
            
            print(f"Question: {question}")
            print(f"Answer: {answer}")
            print(f"Tags: {', '.join(tags)}")
        else:
            print(f"Invalid answer format: {answer_item}")
    
    # Raw JSON output
    print("\n" + "=" * 80)
    print("\nRaw JSON Output (RecommendedQA format):")
    print(json.dumps(agent_output, ensure_ascii=False, indent=2))
    
    return True

def run_interactive_test():
    """Run the interactive test"""
    try:
        setup_environment()
        
        # Prepare test data
        print(f"\nPreparing test data...")
        questions_data = create_mock_questions_from_generator()
        personal_summary = create_mock_personal_summary()
        
        display_input_data(questions_data, personal_summary)
        
        # Generate answers
        print(f"\nGenerating answers...")
        print("This may take a moment...")
        
        agent_output = generate_personalized_answers(
            questions_data=questions_data,
            personal_summary=personal_summary
        )
        
        # Display results
        success = display_results(agent_output)
        
        if success:
            print(f"\nTest completed successfully!")
        else:
            print(f"\nTest failed!")
            return False
        
        return True
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_interactive_test()
    
    if not success:
        sys.exit(1) 