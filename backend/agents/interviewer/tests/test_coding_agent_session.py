import asyncio, json, pytest, os
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from backend.agents.interviewer.agent import (
    start_agent_session,
    client_to_agent_messaging,
    agent_to_client_messaging,
)
from backend.data.database import firestore_db
from backend.data.schemas import CodeSubmission
from backend.agents.coding_judge.agent import _run_coding_judge_from_session

fake_problem = {
    "id": "11",
    "title": "Container With Most Water",
    "slug": "container-with-most-water",
    "category": "Algorithms",
    "difficulty": "Medium",
    "statement": {
        "description": "Given an array height, find two lines forming a container with max water.",
        "constraints": [
            "n == height.length",
            "2 <= n <= 1e5",
            "0 <= height[i] <= 1e4",
        ],
        "examples": [
            {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49"},
            {"input": "height = [1,1]", "output": "1"},
        ],
    },
    "hints": [
        "Naive O(n^2) is too slow.",
        "Use two-pointers, move the smaller one.",
        "Compute area at each step.",
    ],
    "links": {"problem": "https://leetcode.com/problems/container-with-most-water"},
    "solutions": {
        "python": "class Solution:\n def maxArea(self, h: List[int]) -> int: ..."
    },
    "topics": ["Array", "Two Pointers", "Greedy"],
}


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
@patch("backend.agents.interviewer.agent.firestore_db.get_code_submission")
@patch("backend.agents.interviewer.agent.firestore_db.get_coding_problems")
async def test_coding_mode_conversation(mock_get_coding_problems, mock_get_code_submission):
    session_id = "coding-session-test"
    user_id = "test_user_github"
    duration = 5  # shorter for test

    fake_code = "class MinStack { ... }"
    fake_lang = "java"

    # Mock Firestore lookups
    mock_get_code_submission.return_value = {
        "data": {
            "problem_id": fake_problem["id"],
            "code": fake_code,
            "language": fake_lang,
            "claimed_time": "O(n)",
            "claimed_space": "O(1)",
        }
    }
    mock_get_coding_problems.return_value = {"data": fake_problem}


    # Start in coding mode
    live_events, live_queue, session = await start_agent_session(
        session_id,
        user_id,
        duration,
        is_audio=False,
        mode="coding",
    )

    assert session.state["mode"] == "coding"
    assert session.state["problem"] == fake_problem
    assert session.state["code"] == fake_code
    assert session.state["language"] == fake_lang

    mock_ws = MockWebSocket()

    agent_task = asyncio.create_task(
        agent_to_client_messaging(mock_ws, live_events, session)
    )
    client_task = asyncio.create_task(
        client_to_agent_messaging(mock_ws, live_queue, session)
    )

    # Wait for agent's kickoff
    await asyncio.sleep(5)

    # Simulate user sending message
    mock_ws.simulate_user_message("text/plain", "Here is how I think about edge cases.")
    await asyncio.sleep(5)

    # Cancel tasks gracefully
    agent_task.cancel()
    client_task.cancel()
    await asyncio.sleep(1)

    transcript = session.state.get("transcript", [])
    assert any(
        "edge cases" in entry["message"]
        for entry in transcript
        if entry["role"] == "user"
    )
    print("\n✅ Transcript captured coding user message")
    for entry in transcript:
        print(entry)


@pytest.mark.asyncio
@patch("backend.agents.interviewer.agent.save_transcript")
@patch("backend.agents.interviewer.agent.firestore_db.get_code_submission")
@patch("backend.agents.interviewer.agent.firestore_db.get_coding_problems")
async def test_coding_mode_saves_on_expiry(mock_save_transcript, mock_get_code_submission, mock_get_coding_problems):
    session_id = "coding-timeout-test"
    user_id = "test_user_github"

    fake_code = "print('hello')"
    fake_lang = "python"

    mock_get_code_submission.return_value = {
        "data": {
            "problem_id": fake_problem["id"],
            "code": fake_code,
            "language": fake_lang,
            "claimed_time": "O(n)",
            "claimed_space": "O(1)",
        }
    }
    mock_get_coding_problems.return_value = {"data": fake_problem}


    live_events, live_queue, session = await start_agent_session(
        session_id,
        user_id,
        duration_minutes=5,
        is_audio=False,
        mode="coding",
    )

    # Simulate expired session
    session.state["start_time"] = datetime.now(timezone.utc) - timedelta(minutes=6)

    mock_ws = MockWebSocket()
    agent_task = asyncio.create_task(
        agent_to_client_messaging(mock_ws, live_events, session)
    )

    await asyncio.sleep(2)

    agent_task.cancel()

    mock_save_transcript.assert_called_once()
    print("✅ save_transcript called after coding session expiry")

@pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Firestore integration skipped in CI"
)
@pytest.mark.asyncio
async def test_integration_coding_mode_with_db():
    session_id = "coding-session-integration"
    user_id = "test_user_123"
    fake_problem_id = fake_problem["id"]
    duration = 2 # the default time is set from the api call

    # --- 2) Seed Firestore with a code submission ---
    submission = CodeSubmission(
        code="print('hello world')",
        language="python",
        claimed_time="O(n)",
        claimed_space="O(1)",
    )
    firestore_db.save_code_submission(user_id, session_id, fake_problem_id, submission)

    # --- 3) Start a coding session ---
    live_events, live_queue, session = await start_agent_session(
        session_id,
        user_id,
        duration_minutes=duration,
        is_audio=False,
        mode="coding",
    )

    # --- 4) Simulate conversation ---
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

    ws = MockWebSocket()
    agent_task = asyncio.create_task(agent_to_client_messaging(ws, live_events, session))
    client_task = asyncio.create_task(client_to_agent_messaging(ws, live_queue, session))

    # Wait for agent to kick off
    await asyncio.sleep(3)

    # User sends a message
    ws.simulate_user_message("text/plain", "I think this runs in O(n).")
    await asyncio.sleep(3)

    # Cancel tasks gracefully
    agent_task.cancel()
    client_task.cancel()
    await asyncio.sleep(1)

    # --- 5) Check that transcript was written to session state ---
    transcript = session.state.get("transcript", [])
    assert any("O(n)" in entry["message"] for entry in transcript if entry["role"] == "user")

    # --- 6) Verify DB has the submission ---
    saved = firestore_db.get_code_submission(user_id, session_id)
    assert saved["data"]["language"] == "python"
    print("✅ Firestore submission + transcript integration worked")

    # --- 7) Run the judge to generate review and save to Firestore ---
    result = await _run_coding_judge_from_session(session)

    assert "scores" in result
    assert result["problem_slug"] == fake_problem["slug"]

    saved_review = firestore_db.get_coding_review(user_id, session_id)
    assert saved_review["data"] is not None
    assert "scores" in saved_review["data"]
    print("✅ Firestore coding review integration worked")