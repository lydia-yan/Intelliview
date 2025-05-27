"""Answer Generator Agent - Generate personalized interview answers based on questions and user background"""

import json
import os
import asyncio
import sys
import re

# Add the project root to the Python path if necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import unified config
from backend.config import set_google_cloud_env_vars

# Load environment variables
set_google_cloud_env_vars()

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from .prompt import ANSWER_GENERATION_PROMPT
from backend.data.database import firestore_db
from backend.data.schemas import RecommendedQA

# Create global agent instance
ANSWER_GENERATOR_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="answer_generator",
    description="Generate personalized interview answers using clear thinking",
    instruction=ANSWER_GENERATION_PROMPT,
    tools=[]  # No tools needed - uses provided data from question_generator and personal background
)

def generate_and_save_personalized_answers(questions_data, personal_summary, user_id, workflow_id):
    """
    Generate personalized interview answers and save them to database
    
    Args:
        questions_data: Output from question_generator agent (list of questions with empty answers)
        personal_summary: Output from summarizer agent (dict with resume info)
        user_id: User ID for database storage
        workflow_id: Workflow ID for database storage
        
    Returns:
        dict: Result with success status and database storage confirmation
    """
    return asyncio.run(_run_answer_generator_and_save(questions_data, personal_summary, user_id, workflow_id))

async def _run_answer_generator_and_save(questions_data, personal_summary, user_id, workflow_id):
    """Generate answers and save to database"""
    
    answers_result = await _run_answer_generator(questions_data, personal_summary)
    
    if isinstance(answers_result, dict) and "error" in answers_result:
        return answers_result
    
    if not isinstance(answers_result, list):
        return {
            "error": "Invalid answer generation result",
            "raw_result": answers_result
        }
    
    # Convert to RecommendedQA objects for database storage
    try:
        recommended_qas = []
        for answer_item in answers_result:
            if isinstance(answer_item, dict):
                # Ensure required fields exist
                validated_item = {
                    "question": answer_item.get("question", ""),
                    "answer": answer_item.get("answer", ""),
                    "tags": answer_item.get("tags", [])
                }
                # Ensure tags is a list
                if not isinstance(validated_item["tags"], list):
                    if isinstance(validated_item["tags"], str):
                        validated_item["tags"] = [validated_item["tags"]]
                    else:
                        validated_item["tags"] = []
                
                qa = RecommendedQA(**validated_item)
                recommended_qas.append(qa)
        
        # Save to database
        save_result = firestore_db.set_recommended_qas(user_id, workflow_id, recommended_qas)
        
        return {
            "success": True,
            "message": save_result["message"],
            "questions_count": len(recommended_qas),
            "answers": [qa.model_dump() for qa in recommended_qas]
        }
        
    except Exception as e:
        return {
            "error": f"Error saving to database: {str(e)}",
            "raw_answers": answers_result
        }

def generate_personalized_answers(questions_data, personal_summary):
    """
    Generate personalized interview answers based on questions and user background (without database save)
    
    Args:
        questions_data: Output from question_generator agent (list of questions with empty answers)
        personal_summary: Output from summarizer agent (dict with resume info)
        
    Returns:
        list: Questions with personalized answers filled in, compatible with RecommendedQA schema
    """
    return asyncio.run(_run_answer_generator(questions_data, personal_summary))

async def _run_answer_generator(questions_data, personal_summary):
    """Internal async function that executes the AI call"""
    
    # Extract key components for answer generation
    target_job_title = personal_summary.get("title", "Unknown Position")
    job_description = personal_summary.get("jobDescription", "")
    candidate_background = {
        "resumeInfo": personal_summary.get("resumeInfo", ""),
        "additionalInfo": personal_summary.get("additionalInfo", ""),
        "linkedinInfo": personal_summary.get("linkedinInfo", ""),
        "githubInfo": personal_summary.get("githubInfo", ""),
        "portfolioInfo": personal_summary.get("portfolioInfo", "")
    }
    
    # Extract questions from the questions_data
    questions_list = []
    if isinstance(questions_data, list):
        questions_list = questions_data
    elif isinstance(questions_data, dict):
        # Try to extract from various possible keys
        for key in ['questions', 'customized_questions', 'interview_questions', 'data']:
            if key in questions_data and isinstance(questions_data[key], list):
                questions_list = questions_data[key]
                break
        
        # If still not found, check if it's a single question object
        if not questions_list and all(k in questions_data for k in ['question']):
            questions_list = [questions_data]
    
    if not questions_list:
        return {
            "error": "No valid questions found in input data",
            "raw_input": questions_data
        }
    
    # Extract just the question texts for processing
    questions_only = []
    for q in questions_list:
        if isinstance(q, dict) and 'question' in q:
            questions_only.append(q['question'])
        elif isinstance(q, str):
            questions_only.append(q)
    
    # Prepare structured input data
    input_data = f"""
    ## TARGET JOB INFORMATION
    **Position**: {target_job_title}
    **Job Requirements**: {job_description}
    
    ## CANDIDATE'S BACKGROUND
    **Resume Information**: {candidate_background['resumeInfo']}
    **Additional Information**: {candidate_background['additionalInfo']}
    **LinkedIn Profile**: {candidate_background['linkedinInfo']}
    **GitHub Profile**: {candidate_background['githubInfo']}
    **Portfolio**: {candidate_background['portfolioInfo']}
    
    ## INTERVIEW QUESTIONS TO ANSWER
    {json.dumps(questions_only, indent=2)}
    """
    
    # Set up ADK runtime environment
    session_service = InMemorySessionService()
    runner = Runner(
        agent=ANSWER_GENERATOR_AGENT,
        app_name="answer_generator_app",
        session_service=session_service
    )
    
    # Create session
    session_id = f"session_{hash(input_data)}"
    await session_service.create_session(
        app_name="answer_generator_app",
        user_id="user",
        session_id=session_id
    )
    
    # Create input content
    content = types.Content(
        role="user",
        parts=[types.Part(text=input_data)]
    )
    
    # Call agent and get response
    response_text = None
    async for event in runner.run_async(
        user_id="user",
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            break
    
    # Parse JSON result
    try:
        # First, try to extract JSON from Markdown code blocks if present
        markdown_json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        markdown_matches = re.findall(markdown_json_pattern, response_text)
        
        if markdown_matches:
            clean_json_str = markdown_matches[0].strip()
            result = json.loads(clean_json_str)
        else:
            result = json.loads(response_text)
            
    except json.JSONDecodeError:
        # If still not valid JSON, try to extract JSON array using brackets
        try:
            start_index = response_text.find('[')
            end_index = response_text.rfind(']') + 1
            if start_index >= 0 and end_index > start_index:
                json_str = response_text[start_index:end_index]
                result = json.loads(json_str)
            else:
                # Fallback: try to find object notation
                start_index = response_text.find('{')
                end_index = response_text.rfind('}') + 1
                if start_index >= 0 and end_index > start_index:
                    json_str = response_text[start_index:end_index]
                    result = json.loads(json_str)
                else:
                    raise ValueError("Could not find valid JSON in the response")
        except Exception as e:
            result = {
                "error": f"Error parsing response: {str(e)}",
                "raw_response": response_text
            }
    
    # Validate and ensure proper format, preserving original tags
    if isinstance(result, list):
        # Ensure each item has the required fields and preserve original tags
        validated_result = []
        for i, item in enumerate(result):
            if isinstance(item, dict):
                # Get original tags from questions_list
                original_tags = []
                if i < len(questions_list):
                    original_question = questions_list[i]
                    if isinstance(original_question, dict):
                        original_tags = original_question.get("tags", [])
                        # Ensure tags is a list
                        if not isinstance(original_tags, list):
                            if isinstance(original_tags, str):
                                original_tags = [original_tags]
                            else:
                                original_tags = []
                
                # Create validated item with original tags
                validated_item = {
                    "question": item.get("question", ""),
                    "answer": item.get("answer", ""),
                    "tags": original_tags
                }
                
                validated_result.append(validated_item)
        
        return validated_result
    
    return result

def update_questions_with_answers(questions_data, answers_data):
    """
    Helper function to merge questions with generated answers
    
    Args:
        questions_data: Original questions from question_generator
        answers_data: Generated answers from answer_generator
        
    Returns:
        list: Combined questions and answers in RecommendedQA format
    """
    if not isinstance(questions_data, list) or not isinstance(answers_data, list):
        return []
    
    combined_results = []
    
    # Match questions with answers
    for i, question_item in enumerate(questions_data):
        if i < len(answers_data):
            answer_item = answers_data[i]
            
            # Create combined item
            combined_item = {
                "question": question_item.get("question", "") if isinstance(question_item, dict) else str(question_item),
                "answer": answer_item.get("answer", "") if isinstance(answer_item, dict) else str(answer_item),
                "tags": []
            }
            
            # Combine tags from both sources
            question_tags = question_item.get("tags", []) if isinstance(question_item, dict) else []
            answer_tags = answer_item.get("tags", []) if isinstance(answer_item, dict) else []
            
            # Ensure tags are lists
            if not isinstance(question_tags, list):
                question_tags = [question_tags] if question_tags else []
            if not isinstance(answer_tags, list):
                answer_tags = [answer_tags] if answer_tags else []
            
            # Combine and deduplicate tags
            all_tags = list(set(question_tags + answer_tags))
            combined_item["tags"] = all_tags
            
            combined_results.append(combined_item)
    
    return combined_results
