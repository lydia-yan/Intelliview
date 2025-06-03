import pytest
import json
from unittest.mock import patch
from backend.data.tests.mock_data import personalExperience, recommendedQAs, transcript
from backend.agents.interview_judge.agent import _run_judge_from_session
from backend.data.schemas import Feedback
from backend.coordinator.session_manager import session_service  # Global service used in your code

@pytest.mark.asyncio
async def test_run_judge_from_session_valid_output():
    # Setup test data
    app_name = "interview_judge_app"
    user_id = "test_user"
    session_id = "test_interview_judge_session"

    # Prepare session state in global session_service
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state={
            "personal_experience": personalExperience,
            "recommend_qas": recommendedQAs,
            "transcript": transcript
        }
    )

    # Get the session
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )


    with patch("backend.data.database.firestore_db.set_feedback") as mock_set_feedback:
        mock_set_feedback.return_value = {"message": "Mocked DB save"}

        result = await _run_judge_from_session(session)

        assert result is not None, "Expected feedback result but got None"
        feedback_obj = Feedback.model_validate(result)

        print("\n[DEBUG] Agent Feedback Output:")
        print(json.dumps(result, indent=2))

        assert isinstance(feedback_obj, Feedback)
        assert isinstance(feedback_obj.positives, list)
        assert isinstance(feedback_obj.overallRating, int)
        mock_set_feedback.assert_called_once_with(user_id, session_id, feedback_obj)