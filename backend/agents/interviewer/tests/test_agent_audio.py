import asyncio, json, pytest, base64
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from backend.agents.interviewer.agent import (
    start_agent_session,
    session_service,
    client_to_agent_messaging,
    agent_to_client_messaging
)
from backend.agents.interviewer.tests.mock_data import recommendedQAs, personalExperience, profile_data

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


@pytest.mark.asyncio
async def test_audio_agent_conversation_with_mock_ws():
    session_id = "mock-audio-session"
    user_id = "test_user_audio"
    workflow_id = "4VpAXA35z1W0rCYDm3eH"

    # Simulate a 1-second silent PCM (16-bit, mono, 16kHz)
    fake_pcm_audio = bytes([0] * 32000)

    live_events, request_queue, session = await start_agent_session(
        session_id, user_id, workflow_id, duration_minutes=5, is_audio=True
    )

    mock_ws = MockWebSocket()

    agent_task = asyncio.create_task(agent_to_client_messaging(mock_ws, live_events, session))
    client_task = asyncio.create_task(client_to_agent_messaging(mock_ws, request_queue, session))

    await asyncio.sleep(3)  # Wait for any intro message

    # Simulate sending audio blob
    print("[DEBUG] Sending fake audio blob...")
    mock_ws.simulate_user_message("audio/pcm", base64.b64encode(fake_pcm_audio).decode())

    await asyncio.sleep(10)  # Wait for processing

    agent_task.cancel()
    client_task.cancel()
    await asyncio.sleep(1)

    transcript = session.state.get("transcript", [])
    assert len(transcript) >= 2, f"Expected at least 2 transcript entries, got {len(transcript)}"
    print("Audio-based interaction succeeded with transcript:")
    for entry in transcript:
        role = entry.get("role", "unknown")
        msg = entry.get("message", "")
        blob = entry.get("audio_blob", None)
        print(f"{role}: {msg} [audio: {"yes" if blob else "no"}]")
