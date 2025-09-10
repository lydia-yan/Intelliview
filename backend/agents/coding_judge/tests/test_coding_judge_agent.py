from unittest.mock import patch, AsyncMock
import pytest
import json, os
from backend.agents import coding_judge
from backend.agents.coding_judge.tests.mock_data import state
from backend.coordinator.session_manager import session_service  # Global service used in your code
from backend.data.schemas import CodingProblems, CodingReview, Scores, ConversationScores
from backend.agents.coding_judge.agent import _run_coding_judge_from_session

@pytest.mark.skipif(
    os.getenv("CI") == "true",reason="Requires Google Cloud credentials"
)
@pytest.mark.asyncio
async def test_run_judge_from_session_valid_output():
    # Setup test data
    user_id = "test_user"
    session_id = "session_1"
    app_name = "coding_judge_app"

    # Prepare session state in global session_service
    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state = state
    )

    # Get the session
    session = await session_service.get_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )


    with patch("backend.data.database.firestore_db.set_coding_review") as mock_set_feedback:
        mock_set_feedback.return_value = {"message": "Mocked DB save"}

        result = await _run_coding_judge_from_session(session)

        assert result is not None, "Expected feedback result but got None"
        feedback_obj = CodingReview.model_validate(result)

        print("\n[DEBUG] Agent Feedback Output:")
        print(json.dumps(result, indent=2))

        assert isinstance(feedback_obj, CodingReview)
        assert isinstance(feedback_obj.transcript, list)
        assert isinstance(feedback_obj.scores, Scores)
        assert isinstance(feedback_obj.scores.breakdown, dict)
        assert isinstance(feedback_obj.scores.conversation_score, dict | ConversationScores)
        mock_set_feedback.assert_called_once_with(user_id, session_id, feedback_obj)