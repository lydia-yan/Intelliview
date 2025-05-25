"""Resume summarization agent - Convert user's resume content into structured JSON format"""

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
from google.genai import types, Client
from .prompt import SUMMARIZER_PROMPT

# Configure Google AI client
client = Client(
    project="xxx",  # Replace with your project ID
    location="us-central1",
    vertexai=True
)

# Create global agent instance
SUMMARIZER_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="resume_summarizer",
    description="Summarize and organize user's resume and related information",
    instruction=SUMMARIZER_PROMPT,
    tools=[google_search]
)

def summarize_resume(resume_text, linkedin_info, github_info, portfolio_info, additional_info, job_description):
    """
    Analyze and summarize user resume and related information
    
    Args:
        resume_text: Resume text content extracted from PDF
        linkedin_info: LinkedIn link or related information
        github_info: GitHub link or related information
        portfolio_info: Portfolio link or related information
        additional_info: Additional information provided by the user
        job_description: Target job description
        
    Returns:
        dict: Structured resume summary information
    """
    return asyncio.run(_run_summarizer(
        resume_text, linkedin_info, github_info, portfolio_info, additional_info, job_description
    ))

async def _run_summarizer(resume_text, linkedin_info, github_info, portfolio_info, additional_info, job_description):
    """Internal async function that executes the AI call"""
    # Prepare input data
    input_data = f"""
    ## Resume Content
    {resume_text}
    
    ## LinkedIn URL (SEARCH THIS EXACT URL)
    {linkedin_info}
    
    ## GitHub URL (SEARCH THIS EXACT URL)
    {github_info}
    
    ## Portfolio URL (SEARCH THIS EXACT URL)
    {portfolio_info}
    
    ## Additional Information
    {additional_info}
    
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
        # First, try to extract JSON from Markdown code blocks if present
        markdown_json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        markdown_matches = re.findall(markdown_json_pattern, response_text)
        
        if markdown_matches:
            # Use the first JSON code block found
            clean_json_str = markdown_matches[0].strip()
            result = json.loads(clean_json_str)
        else:
            # If no code blocks found, try direct parsing
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
