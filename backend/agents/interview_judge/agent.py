"""Answer Generator Agent - Generate personalized interview answers based on questions and user background"""
import json
import os
import asyncio
import sys
import re
import requests
from duckduckgo_search import DDGS
import time

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
from google.adk.tools import google_search



INTERVIEW_JUDGE_AGENT = LlmAgent(
    model="gemini-2.0-flash", 
    name="feedback_generator",
    description="Generate personalized interview feedback based on interview conversation",
    instruction=get_interview_judge_instruction(),
    tools=[google_search]
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
            for resource in feedback_json.get("resources", []):
                link = resource.get("link", "")
                if not is_valid_and_reachable_url(link):
                    print(f"[⚠️ Invalid link]: {link} – Regenerating via DuckDuckGo...")
                    new_resource = search_ddgs(resource.get("title", "interview tips"))
                    resource["title"] = new_resource["title"]
                    resource["link"] = new_resource["link"]
            print("[DEBUG] Feedback is valid")
            feedback_json = deduplicate_resources(feedback_json)
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


def is_valid_and_reachable_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code >= 400:
            return False
        content = response.text.lower()
        if "404" in content or "page not found" in content or "not available" in content:
            return False
        if len(content) < 500:  # arbitrary: prevent empty landing pages
            return False
        return True
    except Exception:
        return False

def deduplicate_resources(feedback_json):
    seen_links = set()
    unique_resources = []
    
    for resource in feedback_json.get("resources", []):
        link = resource.get("link")
        if link and link not in seen_links:
            unique_resources.append(resource)
            seen_links.add(link)
    
    feedback_json["resources"] = unique_resources
    return feedback_json
        

def search_ddgs(topic: str, max_results: int = 1, delay: int = 1) -> dict:
    """
    Use DDGS to get a real search result link for a given topic, with retry and delay to avoid rate limits.
    """
    try:
        with DDGS() as ddgs:
            for result in ddgs.text(topic, max_results=max_results):
                if result and result.get("href", "").startswith("http"):
                    return {
                        "title": result.get("title", "Related resource"),
                        "link": result["href"]
                    }
        # Wait before retrying if no result found
        print(f"[Retry No valid link found. Waiting {delay}s...")
        time.sleep(delay)
    except Exception as e:
        print(f"[Retry Error: {e}. Waiting {delay}s...")
        time.sleep(delay)

    # Fallback if all attempts fail
    print("[Fallback] Using default backup link.")
    return {
        "title": "5 Tips To Ace a Behavioral-Based Interview",
        "link": "https://jobs.gartner.com/life-at-gartner/your-career/5-tips-to-ace-a-behavioral-based-interview/"
    }