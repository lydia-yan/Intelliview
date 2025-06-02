from backend.agents.interview_judge.agent import parse_and_validate_feedback, save_feedback_to_db
from backend.data.schemas import Feedback
from unittest.mock import MagicMock, patch
import pytest

def test_parse_and_validate_feedback_valid():
    response_text = """
    ```json
    {
        "positives": ["You communicated clearly."],
        "improvementAreas": [
            {
                "topic": "STAR Format",
                "example": "You skipped the Result part.",
                "suggestion": "Add a quantifiable outcome."
            }
        ],
        "resources": [
            {"title": "STAR Technique", "link": "https://example.com/star"}
        ],
        "reflectionPrompt": ["What did you learn from the experience?"],
        "tone": "respectful",
        "overallRating": 4,
        "focusTags": ["clarity", "structure"]
    }
    ```
    """
    result = parse_and_validate_feedback(response_text)
    assert result["status"] == "valid"
    feedback = Feedback.model_validate(result["data"])
    assert feedback.overallRating == 4

def test_save_feedback_to_db_calls_firestore():
    # Mock session and feedback
    mock_session = MagicMock()
    mock_session.user_id = "test_user"
    mock_session.id = "test_session_id"

    feedback_dict = {
        "positives": ["Clear explanation."],
        "improvementAreas": [],
        "resources": [],
        "reflectionPrompt": [],
        "tone": "respectful",
        "overallRating": 5,
        "focusTags": ["confidence"]
    }

    with patch("backend.data.database.firestore_db.set_feedback") as mock_set:
        mock_set.return_value = {"message": "saved"}
        result = save_feedback_to_db(mock_session, feedback_dict)
        mock_set.assert_called_once_with("test_user", "test_session_id", Feedback(**feedback_dict))
        assert result["message"] == "saved"