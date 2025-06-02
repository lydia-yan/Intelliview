import pytest
import json
from starlette.testclient import TestClient
from backend.app import app  # adjust path to where `app = FastAPI()` is

@pytest.fixture
def client():
    return TestClient(app)

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Mock Interview Agent" in response.text or response.json()["message"]

def test_websocket_text_interaction(client):
    with client.websocket_connect(
        "/ws/test123?user_id=test_user&workflow_id=test_workflow&duration=1&is_audio=false"
    ) as websocket:
        # Initial message from agent (usually "please introduce yourself")
        message = websocket.receive_text()
        print("Agent says:", message)

        # Send a user text message
        websocket.send_text(json.dumps({
            "mime_type": "text/plain",
            "data": "Hi, can you ask me a product design question?"
        }))

        # Read agent replies
        # after reading 3 replies, your test loop ends and the with block which automatically closes the WebSocket.
        for _ in range(3):
            reply = websocket.receive_text()
            print("Reply:", reply)

            data = json.loads(reply)

            # Only assert on structured agent response (text/audio)
            if "mime_type" in data:
                assert "data" in data
            else:
                # It's a status update like turn_complete/interrupted
                assert "turn_complete" in data or "interrupted" in data