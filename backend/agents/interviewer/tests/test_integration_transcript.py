import asyncio, json, pytest, os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from backend.agents.interviewer.tests.mock_data import recommendedQAs, personalExperience, profile_data
from backend.agents.interviewer.agent import start_agent_session, session_service, client_to_agent_messaging, agent_to_client_messaging

class MockWebSocket:
    def __init__(self):
        self.sent = []
        self.queue = asyncio.Queue()
        self.closed = False

    async def send_text(self, message):
        self.sent.append(message)

    async def receive_text(self):
        return await self.queue.get()

    async def close(self, code=1000):
        self.closed = True

    def simulate_user_message(self, mime_type, data):
        self.queue.put_nowait(json.dumps({"mime_type": mime_type, "data": data}))

@pytest.mark.skipif(
    os.getenv("CI") == "true", reason="Requires Google Cloud credentials"
)
@pytest.mark.asyncio
async def test_interview_agent_conversation():
    session_id = "manual-session-test"
    user_id = "test_user_123"
    workflow_id = "4VpAXA35z1W0rCYDm3eH"
    duration = 10  # in minutes

    live_events, live_queue, session = await start_agent_session(
        session_id, user_id, workflow_id, duration, is_audio=False
    )

    print("\n--- Initial Session State ---")
    print(f"Transcript: {session.state.get('transcript', 'Not initialized')}")

    mock_ws = MockWebSocket()

    agent_task = asyncio.create_task(agent_to_client_messaging(mock_ws, live_events, session))
    client_task = asyncio.create_task(client_to_agent_messaging(mock_ws, live_queue, session))
    print("[DEBUG] Tasks started. Waiting for agent to begin conversation...")

    # Wait for agent's initial question
    await asyncio.sleep(5)

    print("\n[DEBUG] Sending user message...")
    mock_ws.simulate_user_message("text/plain", "Hi, I'm Jenny and I love solving problems.")
    await asyncio.sleep(10)  # Wait for agent response

    # Cancel tasks gracefully
    agent_task.cancel()
    client_task.cancel()
    await asyncio.sleep(1)

    transcript = session.state.get("transcript", [])
    assert len(transcript) == 4, f"✅ Expected 4 transcript entries, got {len(transcript)}"
    print("\n--- Transcript Content ---")
    transcript = session.state.get("transcript", [])
    for role, message in transcript:
        print(f"{role}: {message}")


# mock the save_transcript() function so no real DB write happen
@pytest.mark.asyncio
@patch("backend.agents.interviewer.agent.save_transcript")
async def test_saves_to_db_after_expiry(mock_save_transcript):
    session_id = "timeout-session-test"
    user_id = "test_user_123"
    workflow_id = "4VpAXA35z1W0rCYDm3eH"
    
    # Start session
    live_events, live_queue, session = await start_agent_session(
        session_id, user_id, workflow_id, duration_minutes=10, is_audio=False
    )

    # Manually set start time to 11 minutes ago to simulate expiry
    session.state["start_time"] = datetime.now(timezone.utc) - timedelta(minutes=11)

    mock_ws = MockWebSocket()
    agent_task = asyncio.create_task(agent_to_client_messaging(mock_ws, live_events, session))

    # Let it run enough to detect expiry
    await asyncio.sleep(2)

    agent_task.cancel()

    # Assert save_transcript was triggered
    mock_save_transcript.assert_called_once()
    print("✅ save_transcript was called after session expiration")

