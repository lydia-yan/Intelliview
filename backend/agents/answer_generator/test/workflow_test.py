#!/usr/bin/env python
"""
Answer Generator workflow test
Tests complete workflow: Question Generator → Answer Generator → Database storage
"""

import os
import sys
import pytest

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skipping Firestore-dependent tests in CI"
)

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

from backend.agents.question_generator.agent import generate_custom_questions
from backend.agents.answer_generator.agent import generate_and_save_personalized_answers
from backend.agents.question_generator.test.mock_data import create_mock_personal_summary, create_mock_industry_faqs
from backend.config import set_google_cloud_env_vars

def test_complete_workflow():
    """Test complete workflow: question generation → answer generation → database storage"""
    
    print("Answer Generator - Workflow Test")
    print("=" * 40)
    
    # Setup
    set_google_cloud_env_vars()
    personal_summary = create_mock_personal_summary()
    industry_faqs = create_mock_industry_faqs()
    
    # Test IDs
    user_id = "test_user_001"
    workflow_id = "test_workflow_001"
    
    print(f"Position: {personal_summary['title']}")
    print(f"User ID: {user_id}")
    print(f"Workflow ID: {workflow_id}")
    
    # Step 1: Generate questions
    print(f"\nStep 1: Generating questions...")
    questions = generate_custom_questions(
        personal_summary=personal_summary,
        industry_faqs=industry_faqs,
        num_questions=50
    )
    
    if not isinstance(questions, list) or len(questions) == 0:
        print(f"❌ Question generation failed")
        return False
    
    print(f"✅ Generated {len(questions)} questions")
    
    # Step 2: Generate answers and save to database
    print(f"\nStep 2: Generating answers and saving to database...")
    result = generate_and_save_personalized_answers(
        questions_data=questions,
        personal_summary=personal_summary,
        user_id=user_id,
        workflow_id=workflow_id
    )
    
    if not result.get("success"):
        print(f"❌ Answer generation/save failed: {result.get('error', 'Unknown error')}")
        return False
    
    print(f"✅ Saved {result['questions_count']} Q&A pairs to database")
    
    # Step 3: Verify tags preservation
    if result.get('answers'):
        sample = result['answers'][0]
        original_tags = questions[0].get('tags', [])
        saved_tags = sample.get('tags', [])
        
        if original_tags == saved_tags:
            print(f"✅ Tags preserved correctly: {saved_tags}")
        else:
            print(f"⚠️  Tags changed from {original_tags} to {saved_tags}")
    
    print(f"\n✅ Workflow test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    if not success:
        sys.exit(1) 