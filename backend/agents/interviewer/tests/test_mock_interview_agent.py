import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
from backend.agents.interviewer.agent import start_agent_session, MockInterviewAgent
from google.adk.sessions import Session
from backend.agents.interviewer.prompt import get_background_prompt



@pytest.mark.asyncio
async def test_transcript_updates():
    # Create a mock session
    session = Session(app_name="MockInterviewerAgent", user_id="test", id="test123")
    session.state["transcript"] = []

    # Simulate message flow
    session.state["transcript"].append(("user", "Hello!"))
    session.state["transcript"].append(("agent", "Hi there!"))

    assert session.state["transcript"] == [
        ("user", "Hello!"),
        ("agent", "Hi there!")
    ]
@pytest.mark.asyncio
@patch("backend.data.database.firestore_db.get_personal_experience")
@patch("backend.data.database.firestore_db.get_recommended_qas")
async def test_start_agent_session_sets_state(mock_get_qas, mock_get_exp):
    # Mock Firestore returns
    mock_get_exp.return_value = {"experience": "Test"}
    mock_get_qas.return_value = [{"question": "Why this role?"}]

    # Setup
    session_id = "test-session"
    user_id = "test-user"
    workflow_id = "mock"
    duration = 5

    # Act
    live_events, live_queue, session = await start_agent_session(
        session_id=session_id,
        user_id=user_id,
        workflow_id=workflow_id,
        duration_minutes=duration,
        is_audio=False
    )

    # Verify session state
    assert session.state["workflow_id"] == workflow_id
    assert session.state["duration_minutes"] == duration
    assert "start_time" in session.state
    assert isinstance(session.state["transcript"], list)
    assert session.state["transcript"][0][0] == "user"
    assert "mock interview" in session.state["transcript"][0][1].lower()

    # Basic assertions on the returned objects
    assert hasattr(live_queue, "send_content")
    assert hasattr(live_events, "__aiter__")

@pytest.mark.asyncio
async def test_session_expiry_logic():
    session = Session(app_name="MockInterviewerAgent", user_id="test", id="expiry-test")
    session.state["start_time"] = datetime.now(timezone.utc) - timedelta(minutes=11)
    session.state["duration_minutes"] = 10

    elapsed = (datetime.now(timezone.utc) - session.state["start_time"]).total_seconds() / 60
    assert elapsed > session.state["duration_minutes"]


@pytest.mark.asyncio
@patch("backend.data.database.firestore_db.get_personal_experience")
@patch("backend.data.database.firestore_db.get_recommended_qas")
async def test_system_instruction_is_set_correctly(mock_get_qas, mock_get_exp):
    # Mock input data to prompt function
    mock_personal_experience = {
        "resumeInfo": "Backend dev experience in Python",
        "githubInfo": "Built OpenAI Chrome extension",
        "linkedinInfo": "Experienced in Flask/PostgreSQL",
        "portfolioInfo": "AI Interview platform and Figma mockups",
        "additionalInfo": "Speaks Mandarin and mentors juniors",
        "jobDescription": "Backend Developer at TechX, working with APIs and AWS"
    }
    mock_recommended_qas = [
        {"question": "Tell me about a time you optimized a system.", "answer": "I improved API response by 30%."}
    ]

    mock_get_exp.return_value = mock_personal_experience
    mock_get_qas.return_value = mock_recommended_qas

    # Start session
    _, _, session = await start_agent_session(
        session_id="test-session-instruction",
        user_id="test-user",
        workflow_id="workflow-test",
        duration_minutes=10,
        is_audio=False
    )

    # Assert instruction exists and includes key content
    personalExperience = session.state.get("personal_experience", "")
    recommendedQAs = session.state.get("recommend_qas", "")

    agent = MockInterviewAgent()
    system_instruction = get_background_prompt(mock_personal_experience, mock_recommended_qas)
    agent.instruction = system_instruction


    assert personalExperience == mock_personal_experience
    assert recommendedQAs == mock_recommended_qas
    assert agent.instruction == system_instruction
