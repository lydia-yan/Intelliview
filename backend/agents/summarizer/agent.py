"""Resume summarization agent - Convert user's resume content into structured JSON format"""

import json
import os
import asyncio
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

# Import unified config
from backend.config import set_google_cloud_env_vars

# Load environment variables
set_google_cloud_env_vars()

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from .prompt import SUMMARIZER_PROMPT

# Create global agent instance
SUMMARIZER_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="resume_summarizer",
    description="Summarize and organize user's resume and related information",
    instruction=SUMMARIZER_PROMPT,
    tools=[google_search]
)

def summarize_resume(resume_text, linkedinLink, githubLink, portfolioLink, additionalInfo, job_description):
    """
    Analyze and summarize user resume and related information
    
    Args:
        resume_text: Resume text content extracted from PDF
        linkedinLink: LinkedIn link or related information
        githubLink: GitHub link or related information
        portfolioLink: Portfolio link or related information
        additionalInfo: Additional information provided by the user
        job_description: Target job description
        
    Returns:
        dict: Structured resume summary information
    """
    return asyncio.run(_run_summarizer(
        resume_text, linkedinLink, githubLink, portfolioLink, additionalInfo, job_description
    ))

async def _run_summarizer(resume_text, linkedinLink, githubLink, portfolioLink, additionalInfo, job_description):
    """Internal async function that executes the AI call"""
    # Prepare input data
    input_data = f"""
    ## Resume Content
    {resume_text}
    
    ## LinkedIn URL (SEARCH THIS EXACT URL)
    {linkedinLink}
    
    ## GitHub URL (SEARCH THIS EXACT URL)
    {githubLink}
    
    ## Portfolio URL (SEARCH THIS EXACT URL)
    {portfolioLink}
    
    ## Additional Information
    {additionalInfo}
    
    ## Job Description
    {job_description}
    """
    
    # Set up ADK runtime environment
    session_service = InMemorySessionService()
    runner = Runner(
        agent=SUMMARIZER_AGENT,
        app_name="resume_summarizer_app",
        session_service=session_service
    )
    
    # Create session
    session_id = f"session_{hash(input_data)}"
    await session_service.create_session(
        app_name="resume_summarizer_app",
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
