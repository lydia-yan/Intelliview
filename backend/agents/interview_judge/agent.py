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
from google.genai import types
from .prompt import get_interview_judge_input_data, get_interview_judge_instruction
from backend.data.database import firestore_db
from backend.data.schemas import Feedback
from pydantic import ValidationError
from backend.coordinator.session_manager import session_service



INTERVIEW_JUDGE_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="feedback_generator",
    description="Generate personalized interview feedback based on interview conversation",
    instruction=get_interview_judge_instruction()
)

def run_judge_from_session(session):
    """
    Evaluate an interview by running the InterviewJudgeAgent using an existing session.

    Args:
        session_service: The session service managing state (e.g., InMemorySessionService).
        session_id (str): ID of the session with the context already set.

    Returns:
        dict: JSON feedback from the judge agent.
    """
    return asyncio.run(_run_judge_from_session(session))


async def _run_judge_from_session(session):
    # each session has its own agent
    runner = Runner(
        agent=INTERVIEW_JUDGE_AGENT,
        app_name=session.app_name,
        session_service=session_service
    )

    input_data = get_interview_judge_input_data(
        session.state.get("personal_experience", ""),
        session.state.get("transcript", ""),
        session.state.get("recommend_qas", "")
    )

        # Create input content
    content = types.Content(
        role="user",
        parts=[types.Part(text=input_data)]
    )

    response_text = None
    feedback_json = None
    try: 
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=content 
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break

        print("[DEBUG] Raw Feedback Agent Response:")
        print(response_text)

        result = parse_and_validate_feedback(response_text)
        if result["status"] == "valid":
            feedback_json = result["data"]
            print("[DEBUG] Feedback is valid")
            result = save_feedback_to_db(session,feedback_json)
            if result["message"]: 
                print("[DEBUG] Feedback stored.")
        else:
            print("[ERROR] Feedback invalid or could not be parsed:")
            print(result)
        return feedback_json
    finally:
        try: 
            await session_service.delete_session(
                app_name=session.app_name,
                user_id=session.user_id,
                session_id=session.id
            )
            print(f"[CLEANUP]: Session {session.id} successfully closed.")
        except Exception as e:
            print(f"[CLEANUP ERROR]: Failed to close session {session.id}: {e}")

def parse_and_validate_feedback(response_text):
    """Extracts and validates feedback JSON from agent response."""
    try:
        # Clean response (e.g., remove markdown)
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text)
        json_str = match.group(1).strip() if match else response_text

        # Parse JSON
        parsed = json.loads(json_str)

        # Validate with schema
        validated = Feedback.model_validate(parsed)

        return {"status": "valid", "data": parsed}  #can switch to return the Feedback object

    except ValidationError as ve:
        return {"status": "invalid", "errors": ve.errors(), "raw": response_text}
    except Exception as e:
        return {"status": "error", "message": str(e), "raw": response_text}
    
# assume the json input
def save_feedback_to_db(session, validated):
    """
    Save a Feedback object to Firestore under a specific user and session.

    Args:
        user_id (str): The ID of the user (can be 'user' or UID if you have auth).
        session_id (str): The session ID this feedback relates to.
        feedback (Feedback): Validated Feedback object (Pydantic).
    """
    
    return firestore_db.set_feedback(session.user_id, session.state.get("workflow_id"), session.id, Feedback(**validated))

