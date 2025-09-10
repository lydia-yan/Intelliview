import pytest,os
import json
from starlette.testclient import TestClient
from backend.app import app  # adjust path to where `app = FastAPI()` is
if os.getenv("CI") == "true":
    pytest.skip("Skipping Firestore-dependent tests in CI", allow_module_level=True)

@pytest.fixture
def client():
    return TestClient(app)

def test_websocket_general_mode(client):
    """Test a normal interview websocket session (non-coding)."""
    with client.websocket_connect(
        "/ws/test_session?user_id=test_user&workflow_id=general_workflow&duration=1&is_audio=false"
    ) as websocket:
        # Receive first agent message
        first_msg = websocket.receive_text()
        data = json.loads(first_msg)
        assert isinstance(data, dict)

        # Simulate sending a text message from user
        websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": "Hi interviewer, tell me about the role."
        }))

        # Expect at least 2-3 agent responses
        for _ in range(2):
            reply = websocket.receive_text()
            data = json.loads(reply)
            assert isinstance(data, dict)
            if "mime_type" in data:
                assert "data" in data
            else:
                assert "turn_complete" in data or "interrupted" in data


def test_websocket_coding_mode(client):
    """Test a coding interview websocket session."""
    with client.websocket_connect(
        "/ws/coding_session?user_id=test_user&workflow_id=coding&duration=1&is_audio=false"
    ) as websocket:
        # First system/agent message
        first_msg = websocket.receive_text()
        data = json.loads(first_msg)
        assert isinstance(data, dict)

        # Send a coding submission message
        websocket.send_text(json.dumps({
            "mime_type": "application/json",
            "data": json.dumps({
                "type": "coding_submit",
                "problem_id": "11",
                "language": "python",
                "code": "print('hello world')",
                "claimed_time": "O(n)",
                "claimed_space": "O(1)"
            })
        }))

        # Expect agent to reply with analysis/feedback
        for _ in range(2):
            reply = websocket.receive_text()
            data = json.loads(reply)
            assert isinstance(data, dict)
            if "mime_type" in data:
                assert "data" in data
            else:
                assert "turn_complete" in data or "interrupted" in data