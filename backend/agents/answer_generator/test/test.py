#!/usr/bin/env python
"""
Answer Generator Agent unit tests for CI/CD
Tests core functionality and schema compatibility
"""

import os
import sys
import json
import pytest

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import unified config and set environment variables
from backend.config import set_google_cloud_env_vars

# Set up environment variables before importing agent
set_google_cloud_env_vars()

from backend.agents.answer_generator.agent import generate_personalized_answers
from backend.agents.question_generator.test.mock_data import create_mock_personal_summary
from backend.agents.answer_generator.test.mock_data import create_mock_questions_from_generator
from backend.data.schemas import RecommendedQA
from pydantic import ValidationError

def test_answer_generator_basic():
    """Test basic answer generation functionality"""
    
    # Prepare test data
    personal_summary = create_mock_personal_summary()
    mock_questions = create_mock_questions_from_generator()
    
    # Test answer generation
    result = generate_personalized_answers(
        questions_data=mock_questions,
        personal_summary=personal_summary
    )
    
    # Basic assertions
    assert result is not None
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Check each answer has required fields
    for answer_item in result:
        assert isinstance(answer_item, dict)
        
        required_fields = ['question', 'answer', 'tags']
        for field in required_fields:
            assert field in answer_item, f"Missing field: {field}"
        
        # Check answer is not empty
        assert answer_item['answer'] is not None
        assert answer_item['answer'].strip() != "", "Answer should not be empty"
        
        # Check tags is a list
        assert isinstance(answer_item['tags'], list)
        assert len(answer_item['tags']) > 0, "Tags should not be empty"
        
        # Check that all tags are strings
        for tag in answer_item['tags']:
            assert isinstance(tag, str)

def test_database_schema_compatibility():
    """Test if answer generator output is compatible with RecommendedQA schema"""
    
    # Prepare test data
    questions_data = create_mock_questions_from_generator()
    personal_summary = create_mock_personal_summary()
    
    # Generate answers
    agent_output = generate_personalized_answers(
        questions_data=questions_data,
        personal_summary=personal_summary
    )
    
    assert isinstance(agent_output, list), "Agent output should be a list"
    assert len(agent_output) > 0, "Agent should generate at least one answer"
    
    # Validate schema compatibility
    validated_answers = []
    for answer_data in agent_output:
        assert isinstance(answer_data, dict), "Each answer should be a dictionary"
        
        # Check required fields
        required_fields = ['question', 'answer', 'tags']
        for field in required_fields:
            assert field in answer_data, f"Missing required field: {field}"
        
        # Ensure tags is a list
        if not isinstance(answer_data.get('tags'), list):
            if isinstance(answer_data.get('tags'), str):
                answer_data['tags'] = [answer_data['tags']]
            else:
                answer_data['tags'] = []
        
        # Validate with schema
        qa = RecommendedQA(**answer_data)
        validated_answers.append(qa)
    
    assert len(validated_answers) == len(agent_output), "All answers should pass schema validation"
    
    # Test JSON serialization
    storage_format = [qa.model_dump() for qa in validated_answers]
    json_str = json.dumps(storage_format, ensure_ascii=False)
    parsed_data = json.loads(json_str)
    
    # Verify deserialized data
    for qa_data in parsed_data:
        RecommendedQA(**qa_data)

if __name__ == "__main__":
    test_answer_generator_basic()
    test_database_schema_compatibility()