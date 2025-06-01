import pytest
from backend.data import database
from backend.data.schemas import Interview, Workflow, TranscriptTurn, Feedback, PersonalExperience, RecommendedQA, GeneralBQ, Profile
from backend.data.tests.mock_data import personalExperience, recommendedQAs, transcript, feedback, generalBQ, profile_data

TEST_USER_ID = "test_user_123"
# Cast URL/email fields to string so Pydantic doesn't use HttpUrl/EmailStr types
profile_data = {
    k: str(v) if "Link" in k or k == "photoURL" or k == "email" else v
    for k, v in profile_data.items()
}

@pytest.fixture(scope="module")
def setup_workflow_and_interview():
    #update profile
    # Cast URL/email fields to string so Pydantic doesn't use HttpUrl/EmailStr types
    profile = Profile(**profile_data)
    result = database.firestore_db.create_or_update_profile(TEST_USER_ID, profile)
    assert "successfully" in result["message"]

    # Create workflow
    workflow_session_id = "workflow_session"
    workflow_title = personalExperience["title"]
    experience_data = {k: v for k, v in personalExperience.items() if k != "title"}

    # Create workflow using the extracted title
    workflow_data = Workflow(title=workflow_title)  #title include the position and company name
    workflow_result = database.firestore_db.create_or_update_workflow(TEST_USER_ID, workflow_session_id, workflow_data)
    assert "successfully" in workflow_result["message"]

    experience = PersonalExperience(**experience_data)
    
    result = database.firestore_db.set_personal_experience(TEST_USER_ID, workflow_session_id, experience)
    assert "successfully" in result["message"]

    qas = [RecommendedQA(**qa) for qa in recommendedQAs]
    result = database.firestore_db.set_recommended_qas(TEST_USER_ID, workflow_session_id, qas)
    assert "successfully" in result["message"]

    # Create interview
    interview_session_id = "interview_session"
    interview_data = Interview(
        transcript=transcript,
        duration_minutes=30
    )
    interview_result = database.firestore_db.create_interview(TEST_USER_ID, interview_session_id, workflow_session_id, interview_data)
    assert "successfully" in interview_result["message"]

    feedback_obj = Feedback(**feedback)

    result = database.firestore_db.set_feedback(TEST_USER_ID, workflow_session_id, interview_session_id, feedback_obj)
    assert "Feedback set" in result["message"]


    return TEST_USER_ID, workflow_session_id, interview_session_id

# ------------------ Test Personal Experience ------------------

def test_set_personal_experience(setup_workflow_and_interview):
    user_id, workflow_id, _ = setup_workflow_and_interview
    workflow_title = personalExperience["title"]
    retrieved = database.firestore_db.get_personal_experience(user_id, workflow_id)
    assert retrieved is not None
    retrieved_w = database.firestore_db.get_workflow(user_id, workflow_id)
    assert retrieved_w["data"]["title"] == workflow_title

# ------------------ Test Recommended QAs ------------------

def test_set_recommended_qas(setup_workflow_and_interview):
    user_id, workflow_id, _ = setup_workflow_and_interview
    qas = [RecommendedQA(**qa) for qa in recommendedQAs]

    retrieved = database.firestore_db.get_recommended_qas(user_id, workflow_id)
    assert retrieved is not None
    assert len(retrieved) == len(qas)
    assert retrieved["data"][0]["question"] == qas[0].question

# ------------------ Test Transcript ------------------

def test_set_transcript(setup_workflow_and_interview):
    user_id, workflow_id, interview_id = setup_workflow_and_interview
    turns = [TranscriptTurn(**t) for t in transcript]

    retrieved = database.firestore_db.get_transcript(user_id, workflow_id, interview_id)
    assert retrieved["data"] is not None
    assert len(retrieved["data"]) == len(turns)
    assert retrieved["data"][0]["message"] == turns[0].message

# ------------------ Test Feedback ------------------

def test_set_feedback(setup_workflow_and_interview):
    user_id, workflow_id, interview_id = setup_workflow_and_interview
    feedback_obj = Feedback(**feedback)


    retrieved = database.firestore_db.get_feedback(user_id, workflow_id, interview_id)
    assert retrieved is not None
    assert retrieved["data"]["overallRating"] == feedback["overallRating"]

# ------------------ Test General BQs ------------------

def test_set_general_bqs():
    bqs = [GeneralBQ(**bq) for bq in generalBQ]

    result = database.firestore_db.set_general_bqs(bqs)
    assert "successfully" in result["message"]

    retrieved = database.firestore_db.get_general_bqs()
    assert retrieved["data"] is not None
    assert len(retrieved["data"]) == len(bqs)
    assert retrieved["data"][0]["question"] == bqs[0].question

# ------------------ Test Profile ------------------

def test_create_update_profile():
    # Cast URL/email fields to string so Pydantic doesn't use HttpUrl/EmailStr types
    profile = Profile(**profile_data)

    result = database.firestore_db.create_or_update_profile(TEST_USER_ID, profile)
    assert "successfully" in result["message"]

    retrieved = database.firestore_db.get_profile(TEST_USER_ID)
    assert retrieved["data"] is not None
    assert retrieved["data"]["name"] == profile.name
    assert retrieved["data"]["email"] == profile.email

def test_update_profile():
    # Start from the original profile
    original_profile = Profile(**profile_data)

    # Modify the name only
    updated_profile = original_profile.model_copy(update={"name": "Updated Jenny"})

    result = database.firestore_db.create_or_update_profile(TEST_USER_ID, updated_profile)
    assert "successfully" in result["message"]

    retrieved = database.firestore_db.get_profile(TEST_USER_ID)
    assert retrieved["data"]["name"] == "Updated Jenny"
    assert retrieved["data"]["email"] == "jenny.cheng@example.com"  # old value should still exist

# ------------------ Test Get all workflows  ------------------
def test_get_workflows_for_user(setup_workflow_and_interview):
    user_id, workflow_id, _ = setup_workflow_and_interview
    workflows = database.firestore_db.get_workflows_for_user(user_id)
    
    assert isinstance(workflows["data"], list)
    assert any(w["workflowId"] == workflow_id for w in workflows["data"])


# ------------------ Test Get all interviews ------------------
def test_get_interviews_for_workflow(setup_workflow_and_interview):
    user_id, workflow_id, session_id = setup_workflow_and_interview
    sessions = database.firestore_db.get_interviews_for_workflow(user_id, workflow_id)

    assert isinstance(sessions["data"], list)
    assert any(s["interviewId"] == session_id for s in sessions["data"])