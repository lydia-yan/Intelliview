from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.genai import types
from datetime import datetime, timezone, timedelta
import asyncio, json, os, sys, re
from .prompt import build_instruction
from backend.data.database import firestore_db  # Adjust this path if needed
from backend.data.schemas import Interview
from google.adk.runners import Runner, RunConfig
from google.adk.agents import LiveRequestQueue
from google.genai.types import Content, Part, Blob
import base64
from backend.agents.interview_judge.agent import _run_judge_from_session
from backend.agents.coding_judge.agent import _run_coding_judge_from_session
from backend.coordinator.session_manager import session_service


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
# Import unified config
from backend.config import set_google_cloud_env_vars

# Load environment variables
set_google_cloud_env_vars()

APP_NAME = "MockInterviewerAgent"


# a custom agent inherited from Llmagent
class MockInterviewAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="MockInterviewAgent",
            model="gemini-2.0-flash-live-preview-04-09",
            description="Generates thoughtful follow-up interview questions based on user responses.",
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3, max_output_tokens=300
            ),
        )
        self.instruction = ""


async def start_agent_session(
    session_id,
    user_id,
    duration_minutes,
    is_audio,
    mode = "general", #Fallback
    workflow_id=None,
):
    """Starts an agent session with a dynamic instruction prompt"""
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=session_id,
    )

    # store mode in state
    session.state["mode"] = mode
    session.state.setdefault("transcript", [])
    # Set up session timer
    setup_duration(session, duration_minutes)

    # defaults so build_instruction always has values
    problem = None
    code = ""
    language = "python"
    claimed_time = None
    claimed_space = None
    personal_experience = None
    recommend_qas = None

    # general context
    if mode == "general":
        personal_experience = (
            firestore_db.get_personal_experience(user_id, workflow_id) or {}
        )
        recommend_qas = firestore_db.get_recommended_qas(user_id, workflow_id) or []
        session.state["workflow_id"] = workflow_id
        session.state["personal_experience"] = personal_experience
        session.state["recommend_qas"] = recommend_qas
    if mode == "coding":
        res = firestore_db.get_code_submission(user_id, session_id)
        if res["data"]:
            problem_res = firestore_db.get_coding_problems(res["data"]["problem_id"])
            problem = problem_res["data"] if problem_res and problem_res.get("data") else None
            code = res["data"]["code"]
            language= res["data"]["language"]
            claimed_time = res["data"].get("claimed_time", None)
            claimed_space = res["data"].get("claimed_space", None)
        else:
            print(f"[ERROR] No code submission found for user {user_id}, session {session_id}")
        session.state.update(
            {
                "problem": problem,
                "code": code,
                "language": language,
                "claimed_time": claimed_time,
                "claimed_space": claimed_space,
            }
        )
    system_instruction = build_instruction(
        mode,
        problem,
        language,
        code,
        claimed_time,
        claimed_space,
        personal_experience,
        recommend_qas,
    )
    # Create agent with session-specific instruction
    agent = MockInterviewAgent()
    agent.instruction = system_instruction

    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )

    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])
    live_request_queue = LiveRequestQueue()

    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )

    # kickoff message differs by mode (NOTE: kickoff is from USER)
    # init the agent to start
    if mode == "coding":
        kickoff = (
            "Let's discuss my submitted solution. "
            "Please start by summarizing my approach in one sentence, "
            "then ask me to state/defend time & space, "
            "ask for 3 edge cases, and probe one likely weak spot. "
            "One question per turn."
        )
    else:
        kickoff = (
            "Please start the mock interview. Ask me to do a self introduction first."
        )

    intro_content = Content(role="user", parts=[Part(text=kickoff)])
    live_request_queue.send_content(content=intro_content)
    session.state["transcript"].append({"role": "AI", "message": kickoff})

    return live_events, live_request_queue, session


async def agent_to_client_messaging(websocket, live_events, session):
    """Agent to client communication"""
    if not session:
        print(f"[ERROR] Session {session.id} not found")
    try:
        response_buffer = []  # Buffer to collect text parts
        while True:
            if is_session_expired(session):
                print(f"[SESSION ENDED] Session {session.id} expired (agent)")
                # Send a final message to user before closing
                goodbye_message = {
                    "mime_type": "text/plain",
                    "data": "⏰ Time's up! Thank you for participating in the mock interview. We'll save your transcript now.",
                }
                await websocket.send_text(json.dumps(goodbye_message))

                end_message = {
                    "type": "end",
                    "data": "Conversation ended. Thank you for participating!",
                }
                await websocket.send_text(json.dumps(end_message))
                print("[AGENT TO CLIENT]: Final end message sent.")

                start_time = session.state.get("start_time")
                end_time = datetime.now(timezone.utc)
                duration = int((end_time - start_time).total_seconds() / 60)
                session.state["duration"] = duration
                await websocket.close(code=1000)

                save_transcript(session)

                # Generate feedback
                try:
                    await mode_aware_judge(session)
                    print(
                        f"[FEEDBACK]: Feedback generated for session {session.id} in mode {session.state.get('mode')} during agent"
                    )
                except Exception as e:
                    print(f"[ERROR]: Failed to generate feedback: {e}")

                break

            async for event in live_events:
                # Send turn completion/interruption notice
                if event.turn_complete or event.interrupted:
                    message = {
                        "turn_complete": event.turn_complete,
                        "interrupted": event.interrupted,
                    }
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: {message}")

                    # Store full response in transcript when complete, if not already stored
                    if event.turn_complete and response_buffer:
                        full_response = response_buffer[-1].strip()
                        session.state["transcript"].append(
                            {"role": "AI", "message": full_response}
                        )
                    response_buffer.clear()  # Clear buffer
                    continue

                # Read the Content and its first Part
                part: Part = (
                    event.content and event.content.parts and event.content.parts[0]
                )
                if not part:
                    continue

                # Handle audio response
                if part.inline_data and part.inline_data.mime_type.startswith(
                    "audio/pcm"
                ):
                    audio_data = part.inline_data.data
                    if audio_data:
                        message = {
                            "mime_type": "audio/pcm",
                            "data": base64.b64encode(audio_data).decode("ascii"),
                        }
                        await websocket.send_text(json.dumps(message))
                        print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                        session.state["transcript"].append(
                            {"role": "AI", "message": "[audio response sent]"}
                        )
                    continue

                # Handle partial text response
                if part.text:
                    response_buffer.append(part.text)
                    message = {"mime_type": "text/plain", "data": part.text}
                    await websocket.send_text(json.dumps(message))
                    print(f"[AGENT TO CLIENT]: text/plain: {message}")

    except Exception as e:
        print(f"[ERROR] agent_to_client_messaging failed: {e}")


async def client_to_agent_messaging(websocket, live_request_queue, session):
    try:
        if not session:
            print(f"[ERROR] Session {session.id} not found")

        while True:
            message_json = await websocket.receive_text()
            message = json.loads(message_json)
            mime_type = message["mime_type"]
            data = message["data"]

            try:
                control = json.loads(data)
                if (
                    isinstance(control, dict)
                    and control.get("type") == "control"
                    and control.get("action") == "end_interview"
                ):
                    print(
                        "[CLIENT TO AGENT]: Received end_interview control, generating feedback and closing..."
                    )

                    if session.state["mode"] == "general":
                        # Calculate duration
                        start_time = session.state.get("start_time")
                        end_time = datetime.now(timezone.utc)
                        duration = int((end_time - start_time).total_seconds() / 60)
                        session.state["duration"] = duration
                        # Save transcript
                        save_transcript(session)
                        print(f"[SAVE]: Transcript saved for session {session.id}")

                    # Generate feedback
                    try:
                        await mode_aware_judge(session)
                        print(
                            f"[FEEDBACK]: Feedback generated for session {session.id} in mode {session.state.get('mode')} during client"
                        )
                    except Exception as e:
                        print(f"[ERROR]: Failed to generate feedback: {e}")

                    # Close WebSocket
                    await websocket.close(code=1000)
                    break
            except Exception:
                pass

            if mime_type == "text/plain":
                # Send text to agent
                content = Content(role="user", parts=[Part.from_text(text=data)])
                live_request_queue.send_content(content=content)
                print(f"[CLIENT TO AGENT]: {data}")

                # Record user message in session transcript
                session.state["transcript"].append({"role": "user", "message": data})

            elif mime_type == "audio/pcm":
                # Decode audio and send to agent
                decoded_data = base64.b64decode(data)
                live_request_queue.send_realtime(
                    Blob(data=decoded_data, mime_type=mime_type)
                )
                print(f"[CLIENT TO AGENT]: [audio data] {len(decoded_data)} bytes")

                # Record audio event in transcript
                session.state["transcript"].append(
                    {"role": "user", "message": "[audio message]"}
                )
            else:
                raise ValueError(f"Mime type not supported: {mime_type}")
    except Exception as e:
        print(f"[ERROR] client_to_agent_messaging failed: {e}")


def is_session_expired(session):
    start = session.state.get("start_time")
    duration = session.state.get("duration_minutes")
    if not start:
        return False
    return datetime.now(timezone.utc) > start + timedelta(minutes=duration)


def setup_duration(session, duration_minutes: int):
    """Set the start time and allowed duration for a session."""
    session.state["start_time"] = datetime.now(timezone.utc)
    session.state["duration_minutes"] = duration_minutes


def save_transcript(session):
    transcript = session.state.get("transcript", [])
    workflowId = session.state.get("workflow_id")

    interview_data = Interview(
        transcript=transcript, duration_minutes=session.state.get("duration")
    )

    firestore_db.create_interview(
        user_id=session.user_id,
        session_id=session.id,
        workflow_id=workflowId,
        interview_data=interview_data,
    )


async def mode_aware_judge(session):
    """
    Branch judging by mode.
    - general: keep your existing judge behavior via _run_judge_from_session
    - coding: call your sandboxed reviewer/runner, then store results
    """
    mode = session.state.get("mode", "general")
    if mode == "coding":
        # Example: call a reviewer tool/service that runs code, produces JSON
        # Input payload (already in state from start_agent_session)
        await _run_coding_judge_from_session(session)
    else:
        # your existing judge flow for general interviews
        await _run_judge_from_session(session)
