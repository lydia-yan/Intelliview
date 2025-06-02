"""Question Generator Agent - Generate customized interview questions based on user background, industry FAQs, and general BQs"""

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
from .prompt import QUESTION_GENERATION_PROMPT
from backend.data.database import firestore_db

# Create global agent instance
QUESTION_GENERATOR_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="question_generator",
    description="Generate customized interview questions based on user background, industry FAQs, and general BQs",
    instruction=QUESTION_GENERATION_PROMPT,
    tools=[],
    output_key="questions_data"
) 

def generate_custom_questions(personal_summary, industry_faqs, num_questions=50):
    """
    Generate customized interview questions based on user background, industry FAQs, and general behavioral questions
    
    Args:
        personal_summary: Output from summarizer agent (dict with resume info)
        industry_faqs: Output from search agent (dict with industry questions)
        num_questions: Number of questions to generate (default: 10)
        
    Returns:
        list: Structured interview questions with customization (RecommendedQA format but without answers)
    """
    return asyncio.run(_run_question_generator(personal_summary, industry_faqs, num_questions))

async def _run_question_generator(personal_summary, industry_faqs, num_questions):
    """Internal async function that executes the AI call"""
    
    # Get general behavioral questions from database
    try:
        general_bqs = firestore_db.get_general_bqs()
        if not general_bqs:
            general_bqs = []
            print("Warning: No general BQs found in database")
    except Exception as e:
        print(f"Warning: Could not fetch general BQs from database: {e}")
        general_bqs = []
    
    # Extract key components for better analysis
    target_job_title = personal_summary.get("title", "Unknown Position")
    job_description = personal_summary.get("jobDescription", "")
    candidate_background = {
        "resumeInfo": personal_summary.get("resumeInfo", ""),
        "additionalInfo": personal_summary.get("additionalInfo", ""),
        "linkedinInfo": personal_summary.get("linkedinInfo", ""),
        "githubInfo": personal_summary.get("githubInfo", ""),
        "portfolioInfo": personal_summary.get("portfolioInfo", "")
    }
    
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
    
    ## INDUSTRY COMMON QUESTIONS (HIGH PRIORITY - focus on "commonly asked" questions)
    {json.dumps(industry_faqs, indent=2)}
    
    ## GENERAL BEHAVIORAL QUESTIONS (from database)
    {json.dumps(general_bqs, indent=2)}
    
    ## TASK REQUIREMENTS
    IMPORTANT: The output JSON array must contain EXACTLY {num_questions} questions(NO MORE, NO LESS).
    """
    
    # Set up ADK runtime environment
    session_service = InMemorySessionService()
    runner = Runner(
        agent=QUESTION_GENERATOR_AGENT,
        app_name="question_generator_app",
        session_service=session_service
    )
    
    # Create session
    session_id = f"session_{hash(input_data)}"
    await session_service.create_session(
        app_name="question_generator_app",
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
        markdown_json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        markdown_matches = re.findall(markdown_json_pattern, response_text)
        
        if markdown_matches:
            clean_json_str = markdown_matches[0].strip()
            result = json.loads(clean_json_str)
        else:
            result = json.loads(response_text)
            
    except json.JSONDecodeError:
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
    
    return result 