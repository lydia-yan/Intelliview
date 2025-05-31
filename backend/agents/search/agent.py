"""Interview questions search agent - Search the Internet for common interview questions and experiences"""

import json
import os
import asyncio
import sys
import re

# Add the project root to the Python path if necessary
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from .prompt import SEARCH_PROMPT

# Import unified config
from backend.config import set_google_cloud_env_vars

# Load environment variables
set_google_cloud_env_vars()

# Create global agent instance
SEARCH_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="interview_questions_searcher",
    description="Search for common interview questions and experiences for specific job positions",
    instruction=SEARCH_PROMPT,
    tools=[google_search],
    output_key="industry_faqs"
)

def search_interview_questions(job_description):
    """
    Search for common interview questions and experiences based on job description
    
    Args:
        job_description: The complete job description text
        
    Returns:
        dict: Structured interview questions and experiences
    """
    return asyncio.run(_run_searcher(job_description))

async def _run_searcher(job_description):
    """Internal async function that executes the AI call"""
    # Prepare input data
    input_data = f"""
    ## Job Description
    {job_description}
    """
    
    # Set up ADK runtime environment
    session_service = InMemorySessionService()
    runner = Runner(
        agent=SEARCH_AGENT,
        app_name="interview_questions_searcher_app",
        session_service=session_service
    )
    
    # Create session
    session_id = f"session_{hash(input_data)}"
    await session_service.create_session(
        app_name="interview_questions_searcher_app",
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
        # If still not valid JSON, try to extract JSON part using braces
        try:
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
