"""
Preparation Workflow Coordinator - Using ADK SequentialAgent with state injection
"""

import os
import sys
import asyncio
import json
import traceback
import time
import secrets
import string
from typing import Optional

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from google.adk.agents import SequentialAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

# Import config
from backend.config import set_google_cloud_env_vars

# Import agents
from backend.agents.summarizer.agent import SUMMARIZER_AGENT
from backend.agents.search.agent import SEARCH_AGENT
from backend.agents.question_generator.agent import QUESTION_GENERATOR_AGENT
from backend.agents.answer_generator.agent import ANSWER_GENERATOR_AGENT

# Load environment variables
set_google_cloud_env_vars()

# Global session service for workflow
_session_service = InMemorySessionService()

def generate_session_id(input_data: str = ""):
    """Generate a random session ID similar to Firestore document IDs"""
    alphabet = string.ascii_letters + string.digits
    session_id = ''.join(secrets.choice(alphabet) for _ in range(20))
    return session_id

def extract_json_from_response(response_text: str) -> dict:
    """
    Extract JSON data from LLM response text that may contain markdown code blocks
    
    Args:
        response_text: Raw response text from LLM
        
    Returns:
        dict: Parsed JSON data, or empty dict if extraction fails
    """
    if not response_text:
        return {}
        
    try:
        import re
        # Extract JSON from markdown code blocks if present
        markdown_json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        markdown_matches = re.findall(markdown_json_pattern, response_text)
        
        if markdown_matches:
            clean_json_str = markdown_matches[0].strip()
            return json.loads(clean_json_str)
        else:
            return json.loads(response_text)

    except json.JSONDecodeError:
        try:
            start_index = response_text.find('{')
            end_index = response_text.rfind('}') + 1
            if start_index >= 0 and end_index > start_index:
                json_str = response_text[start_index:end_index]
                return json.loads(json_str)
            else:
                raise ValueError("Could not find valid JSON in the response")
        except Exception as e:
            return {
                "error": f"Error parsing response: {str(e)}",
                "raw_response": response_text
            }

def create_preparation_workflow():
    """Create and configure the SequentialAgent workflow"""
    return SequentialAgent(
        sub_agents=[
            SUMMARIZER_AGENT,
            SEARCH_AGENT,
            QUESTION_GENERATOR_AGENT,
            ANSWER_GENERATOR_AGENT
        ],
        name="interview_preparation_workflow",
        description="Interview preparation workflow including resume summarizer, search, question generator, and answer generator."
    )

async def run_preparation_workflow(
    user_id: str,
    resume_text: str,
    job_description: str,
    linkedin_link: str = "",
    github_link: str = "", 
    portfolio_link: str = "",
    additional_info: str = "",
    num_questions: int = 50,
    session_id: Optional[str] = None,
    
):
    """
    Run the complete interview preparation workflow using ADK SequentialAgent
    
    Args:
        user_id: User ID from frontend login system
        resume_text: Resume content (required)
        job_description: Target job description (required)
        linkedin_link: LinkedIn profile URL (optional)
        github_link: GitHub profile URL (optional)
        portfolio_link: Portfolio URL (optional)
        additional_info: Additional user information (optional)
        num_questions: Number of questions to generate (default: 50)
        session_id: Session ID (optional, will auto-generate if not provided, serves as workflow_id)
    
    Returns:
        dict: Result with workflow completion status, generated session_id, and any errors
    """
    try:
        # Auto-generate session_id if not provided
        if not session_id:
            input_signature = f"{user_id}{resume_text[:100]}{job_description[:100]}{time.time()}"
            session_id = generate_session_id(input_signature)
        
        workflow_id = session_id  # session_id serves as workflow_id
        
        # Create workflow
        preparation_workflow = create_preparation_workflow()
        
        # Create runner
        runner = Runner(
            agent=preparation_workflow,
            app_name="interview_preparation_app",
            session_service=_session_service
        )
        
        # Create session
        await _session_service.create_session(
            app_name="interview_preparation_app",
            user_id=user_id,
            session_id=session_id
        )
        
        # Prepare input for SUMMARIZER_AGENT (include num_questions in the input)
        summarizer_input = f"""
        ##CRITICAL WORKFLOW CONFIGURATION
        Number of questions to generate: {num_questions}
        IMPORTANT: This workflow MUST generate exactly {num_questions} interview questions
        
        ## Resume Content
        {resume_text}
        
        ## LinkedIn URL (SEARCH THIS EXACT URL)
        {linkedin_link}
        
        ## GitHub URL (SEARCH THIS EXACT URL)  
        {github_link}
        
        ## Portfolio URL (SEARCH THIS EXACT URL)
        {portfolio_link}
        
        ## Additional Information
        {additional_info}
        
        ## Job Description
        {job_description}
        
        ## 🎯 REMINDER: EXACT QUESTION COUNT REQUIRED 🎯
        The question generator MUST produce exactly {num_questions} questions.
        Number of questions to generate: {num_questions}
        """
        
        # Create input content
        content = types.Content(
            role="user",
            parts=[types.Part(text=summarizer_input)]
        )
        
        # Run ADK SequentialAgent workflow
        print("=== Starting ADK SequentialAgent workflow ===")
        
        event_count = 0
        completed_agents = []
        
        # Process all events
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            event_count += 1
            
            print(f"\n--- Event {event_count}: {event.author} ---")
            
            if hasattr(event, 'content') and event.content:
                content_text = event.content.parts[0].text
                print(f"Content preview: {content_text[:100]}...")
                
                if event.is_final_response():
                    completed_agents.append(event.author)
                    print(f"=== {event.author} completed ===")
        
        print(f"\n=== ADK workflow completed ===")
        print(f"Total events: {event_count}")
        print(f"Completed agents: {completed_agents}")
        
        # Get final session state
        session = await _session_service.get_session(
            app_name="interview_preparation_app",
            user_id=user_id,
            session_id=session_id
        )
        
        print(f"Final session state keys: {list(session.state.keys())}")
        
        # Extract and process results
        session_state_updates = {}
        for key in ['personal_summary', 'industry_faqs', 'questions_data', 'answers_data']:
            if key in session.state:
                raw_data = session.state[key]
                if isinstance(raw_data, str):
                    session_state_updates[key] = extract_json_from_response(raw_data)
                else:
                    session_state_updates[key] = raw_data
        
        # Save to database
        await _save_workflow_results_to_database(user_id, session_id, session_state_updates)
        
        return {
            "success": True,
            "user_id": user_id,
            "session_id": session_id,
            "workflow_id": session_id,
            "completed_agents": completed_agents,
            "session_state": dict(session.state),
            "personal_summary": json.dumps(session_state_updates.get("personal_summary", {}), ensure_ascii=False),
            "industry_faqs": json.dumps(session_state_updates.get("industry_faqs", {}), ensure_ascii=False),
            "questions_data": json.dumps(session_state_updates.get("questions_data", []), ensure_ascii=False),
            "final_answers": json.dumps(session_state_updates.get("answers_data", []), ensure_ascii=False)
        }
        
    except Exception as e:
        print(f"Error in run_preparation_workflow: {e}")
        print(traceback.format_exc())
        return {
            "success": False,
            "error": str(e),
            "user_id": user_id,
            "session_id": session_id,
            "workflow_id": workflow_id
        }

async def _save_workflow_results_to_database(user_id, session_id, session_state_updates):
    """Save workflow results to database without re-executing agent logic"""
    try:
        # Save PersonalExperience if summarizer completed successfully
        personal_summary = session_state_updates.get("personal_summary", {})
        if personal_summary and isinstance(personal_summary, dict) and "error" not in personal_summary:
            try:
                from backend.data.schemas import PersonalExperience
                from backend.data.database import firestore_db
                
                # Convert to PersonalExperience object for database storage
                personal_experience = PersonalExperience(
                    
                    resumeInfo=personal_summary.get("resumeInfo", ""),
                    linkedinInfo=personal_summary.get("linkedinInfo", ""),
                    githubInfo=personal_summary.get("githubInfo", ""),
                    portfolioInfo=personal_summary.get("portfolioInfo", ""),
                    additionalInfo=personal_summary.get("additionalInfo", ""),
                    jobDescription=personal_summary.get("jobDescription", "")
                )
                
                # Save to database
                firestore_db.set_personal_experience(user_id, session_id, personal_experience)
                print(f"Saved personal experience to database for user {user_id}, workflow {session_id}")
                
            except Exception as e:
                print(f"Warning: Could not save PersonalExperience to database: {e}")
        
        # Save RecommendedQAs if answer generator completed successfully  
        final_answers = session_state_updates.get("answers_data", [])
        if final_answers and isinstance(final_answers, list) and len(final_answers) > 0:
            try:
                # Check if questions have answers (indicating answer generator ran)
                sample_question = final_answers[0] if final_answers else {}
                if isinstance(sample_question, dict) and sample_question.get("answer"):
                    from backend.data.schemas import RecommendedQA
                    from backend.data.database import firestore_db
                    
                    # Convert to RecommendedQA objects for database storage
                    recommended_qas = []
                    for item in final_answers:
                        if isinstance(item, dict):
                            validated_item = {
                                "question": item.get("question", ""),
                                "answer": item.get("answer", ""),
                                "tags": item.get("tags", [])
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
                    if recommended_qas:
                        firestore_db.set_recommended_qas(user_id, session_id, recommended_qas)
                        print(f"Saved {len(recommended_qas)} recommended QAs to database for user {user_id}, workflow {session_id}")
                else:
                    print(f"Warning: Sample question doesn't have answer field or answer is empty.")
            except Exception as e:
                print(f"Warning: Could not save RecommendedQAs to database: {e}")
        else:
            print(f"Warning: No valid answers_data found for database storage.")
                
    except Exception as e:
        print(f"Error in database save operations: {e}")

def run_preparation_workflow_sync(*args, **kwargs):
    """
    Synchronous wrapper for the async workflow function
    """
    return asyncio.run(run_preparation_workflow(*args, **kwargs)) 