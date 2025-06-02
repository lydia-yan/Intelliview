import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app import app
from unittest.mock import patch, MagicMock, AsyncMock
from backend.api.routes import verify_token



client = TestClient(app)


# Fake token response
def override_verify_token():
    return {
        "uid": "user123",
        "email": "user@example.com",
        "name": "Test User",
        "picture": "http://photo.url"
    }

# Apply once for all tests
app.dependency_overrides[verify_token] = override_verify_token

# ---- TESTS ----

def test_public_route():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"success": True, "data": None}


def test_init_user_profile_new_user():
    with patch("backend.data.database.firestore_db.get_profile", return_value=None), \
         patch("backend.data.database.firestore_db.create_or_update_profile", return_value={"message": "ok", "data": {
             "name": "Test User",
             "email": "user@example.com",
             "photoURL": "http://photo.url"
         }}):
        
        response = client.post("/auth/init", headers={"Authorization": "Bearer fake-token"})

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["email"] == "user@example.com"
        assert res["data"]["isNew"] is True

def test_get_user_info():
    mock_profile = {
        "name": "Test User",
        "email": "user@example.com",
        "photoURL": "http://photo.url"
    }

    with patch("backend.data.database.firestore_db.get_profile", return_value={
        "message": "ok",
        "data": mock_profile
    }):
        response = client.get("/user", headers={"Authorization": "Bearer test-token"})

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["name"] == "Test User"



def test_update_user_info():
    mock_profile_data = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "photoURL": "http://new.photo.url",
        "createAt": "2024-01-01T00:00:00Z"
    }

    mock_return_value = {
        "message": "Profile for user user123 created/updated successfully",
        "data": mock_profile_data
    }

    with patch("backend.data.database.firestore_db.create_or_update_profile", return_value=mock_return_value):
        payload = {
            "name": "Updated Name",
            "email": "updated@example.com",
            "photoURL": "http://new.photo.url"
        }

        response = client.put("/user", headers={"Authorization": "Bearer test-token"}, json=payload)

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert res["data"]["name"] == "Updated Name"

def test_get_all_workflows():
    mock_workflows = [
        {
            "workflowId": "wf_001",
            "title": "Backend SWE at Google",
            "personalExperience": {}
        },
        {
            "workflowId": "wf_002",
            "title": "Frontend SWE at Meta",
            "personalExperience": {}
        }
    ]

    with patch("backend.data.database.firestore_db.get_workflows_for_user", return_value={
        "message": "ok",
        "data": mock_workflows
    }):
        response = client.get("/workflows", headers={"Authorization": "Bearer test-token"})

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) == 2
        assert res["data"][0]["workflowId"] == "wf_001"


def test_get_workflows_no_data():
    with patch("backend.data.database.firestore_db.get_workflows_for_user", return_value={
        "message": "Found 0 workflows successfully",
        "data": []
    }):
        response = client.get("/workflows", headers={"Authorization": "Bearer test-token"})

        assert response.status_code == 200
        res = response.json()

        assert res["success"] is False
        assert res["data"] == []


def test_get_recommended_qas():
    workflow_id = "wf_001"
    mock_qas = [
        {"question": "Tell me about yourself", "answer": "I’m Jenny..."},
        {"question": "Why do you want this job?", "answer": "Because..."}
    ]

    with patch("backend.data.database.firestore_db.get_recommended_qas", return_value={
        "message": "ok",
        "data": mock_qas
    }):
        url = f"/workflows/{workflow_id}/recommended-qa"
        response = client.get(url, headers={"Authorization": "Bearer test-token"})

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert isinstance(res["data"], list)
        assert res["data"][0]["question"] == "Tell me about yourself"


def test_get_all_interviews_for_workflow():
    workflow_id = "wf_001"
    mock_interviews = [
        {
            "interviewId": "int_001",
            "createAt": "2024-05-01T10:00:00Z",
            "feedback": None,
            "transcript": [],
        },
        {
            "interviewId": "int_002",
            "createAt": "2024-05-02T11:00:00Z",
            "feedback": {"score": 4},
            "transcript": [{"speaker": "user", "text": "hello"}],
        }
    ]

    with patch("backend.data.database.firestore_db.get_interviews_for_workflow", return_value={
        "message": "Found 2 interviews",
        "data": mock_interviews
    }):
        response = client.get(
            f"/workflows/{workflow_id}/interviews",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is True
        assert len(res["data"]) == 2
        assert res["data"][0]["interviewId"] == "int_001"


def test_get_all_interviews_for_workflow_empty():
    workflow_id = "wf_999"

    with patch("backend.data.database.firestore_db.get_interviews_for_workflow", return_value={
        "message": "Retrieve successfully",
        "data": []
    }):
        response = client.get(
            f"/workflows/{workflow_id}/interviews",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        res = response.json()
        assert res["success"] is False
        assert res["data"] == []