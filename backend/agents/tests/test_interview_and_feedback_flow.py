import asyncio, json, pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from backend.data.tests.mock_data import recommendedQAs, personalExperience, transcript
from backend.agents.interviewer.agent import start_agent_session, session_service, client_to_agent_messaging, agent_to_client_messaging
from unittest.mock import AsyncMock, patch, MagicMock
from backend.agents.interview_judge.agent import _run_judge_from_session
from backend.data.database import firestore_db


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
@patch("backend.agents.interviewer.agent._run_judge_from_session", new_callable=AsyncMock)
@patch("backend.agents.interviewer.agent.save_transcript")
async def test_feedback_is_generated_and_stored(
    mock_save_transcript,
    mock_judge_run,
):


    session_id = "feedback-session"
    user_id = "test_user_999"
    workflow_id = "test_workflow"

    # Simulated agent output
    mock_judge_run.return_value = {"score": "great", "comments": ["Very clear answers!"]}

    # Start session
    live_events, live_queue, session = await start_agent_session(
        session_id=session_id,
        user_id=user_id,
        workflow_id=workflow_id,
        duration_minutes=10,
        is_audio=False,
    )

    # Trigger timeout by setting start time in the past
    session.state["start_time"] = datetime.now(timezone.utc) - timedelta(minutes=11)
    mock_ws = MockWebSocket()

    # Run agent-to-client messaging to simulate end of session
    agent_task = asyncio.create_task(agent_to_client_messaging(mock_ws, live_events, session))
    await asyncio.sleep(2)
    agent_task.cancel()

    # Assertions
    mock_save_transcript.assert_called_once()
    mock_judge_run.assert_awaited_once()

    print("Feedback and transcript were both generated and stored correctly.")

@pytest.mark.asyncio
async def test_full_interview_to_feedback_flow():
    session_id = "integration-session"
    user_id = "test_user_integration"
    workflow_id = "test_workflow"
    duration = 10
    is_audio = False

    # Step 1: Start session
    live_events, live_queue, session = await start_agent_session(
        session_id=session_id,
        user_id=user_id,
        workflow_id=workflow_id,
        duration_minutes=duration,
        is_audio=is_audio
    )

    # Step 2: Populate session state with mock transcript + QA
    session.state["personal_experience"] = personalExperience
    session.state["recommend_qas"] = recommendedQAs
    session.state["transcript"] = transcript
    session.state["start_time"] = datetime.now(timezone.utc) - timedelta(minutes=11)  # force timeout

    # Step 3: Mock websocket and run expiration detection
    mock_ws = MockWebSocket()
    agent_task = asyncio.create_task(agent_to_client_messaging(mock_ws, live_events, session))
    await asyncio.sleep(5)

    # Step 4: Call feedback agent directly
    feedback = firestore_db.get_feedback(user_id, workflow_id, session_id)

    print("\n✅ Feedback fetched from DB:")
    print(json.dumps(feedback["data"], indent=2))

    # Basic structure check
    assert "overallRating" in feedback["data"]
    assert "improvementAreas" in feedback["data"]
    assert isinstance(feedback["data"]["positives"], list)


@pytest.mark.asyncio
@patch("backend.agents.interviewer.agent._run_judge_from_session", new_callable=AsyncMock)
@patch("backend.agents.interviewer.agent.save_transcript")
async def test_feedback_on_client_disconnect(
    mock_save_transcript,
    mock_judge_run,
):
    session_id = "disconnect-session"
    user_id = "test_user_disconnect"
    workflow_id = "test_workflow"

    # Simulated judge response
    mock_judge_run.return_value = {
        "overallRating": "good",
        "improvementAreas": ["More specific examples"],
        "positives": ["Strong structure", "Clear speaking"]
    }

    # Step 1: Start session
    live_events, live_queue, session = await start_agent_session(
        session_id=session_id,
        user_id=user_id,
        workflow_id=workflow_id,
        duration_minutes=10,
        is_audio=False,
    )

    # Step 2: Simulate that session started 11 minutes ago (to trigger expiry)
    session.state["start_time"] = datetime.now(timezone.utc) - timedelta(minutes=11)

    # Step 3: Simulate websocket and disconnect before expiration is processed
    mock_ws = MockWebSocket()

    agent_task = asyncio.create_task(agent_to_client_messaging(mock_ws, live_events, session))

    # Step 4: Simulate client disconnection
    await asyncio.sleep(1)
    await mock_ws.close()

    # Step 5: Let agent session process for a bit
    await asyncio.sleep(2)
    agent_task.cancel()

    # Step 6: Assertions
    mock_save_transcript.assert_called_once()
    mock_judge_run.assert_awaited_once()
    print("✅ Feedback and transcript were saved correctly after disconnect.")