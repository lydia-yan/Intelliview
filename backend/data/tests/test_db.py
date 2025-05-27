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
    workflow_title = personalExperience["title"]
    experience_data = {k: v for k, v in personalExperience.items() if k != "title"}

    # Create workflow using the extracted title
    workflow_data = Workflow(title=workflow_title)  #title include the position and company name
    workflow_result = database.firestore_db.create_or_update_workflow(TEST_USER_ID, workflow_data)
    workflow_id = workflow_result["workflowId"]

    experience = PersonalExperience(**experience_data)
    
    result = database.firestore_db.set_personal_experience(TEST_USER_ID, workflow_id, experience)
    assert "successfully" in result["message"]

    qas = [RecommendedQA(**qa) for qa in recommendedQAs]
    result = database.firestore_db.set_recommended_qas(TEST_USER_ID, workflow_id, qas)
    assert "successfully" in result["message"]

    # Create interview
    interview_data = Interview()
    interview_result = database.firestore_db.create_interview(TEST_USER_ID, workflow_id, interview_data)
    interview_id = interview_result["interviewId"]

    turns = [TranscriptTurn(**t) for t in transcript]

    result = database.firestore_db.set_transcript(TEST_USER_ID, interview_id, turns)
    assert "Transcript set" in result["message"]

    feedback_obj = Feedback(**feedback)

    result = database.firestore_db.set_feedback(TEST_USER_ID, interview_id, feedback_obj)
    assert "Feedback set" in result["message"]


    return TEST_USER_ID, workflow_id, interview_id

# ------------------ Test Personal Experience ------------------

def test_set_personal_experience(setup_workflow_and_interview):
    user_id, workflow_id, _ = setup_workflow_and_interview
    workflow_title = personalExperience["title"]
    retrieved = database.firestore_db.get_personal_experience(user_id, workflow_id)
    assert retrieved is not None
    retrieved_w = database.firestore_db.get_workflow(user_id, workflow_id)
    assert retrieved_w["title"] == workflow_title

# ------------------ Test Recommended QAs ------------------

def test_set_recommended_qas(setup_workflow_and_interview):
    user_id, workflow_id, _ = setup_workflow_and_interview
    qas = [RecommendedQA(**qa) for qa in recommendedQAs]

    retrieved = database.firestore_db.get_recommended_qas(user_id, workflow_id)
    assert retrieved is not None
    assert len(retrieved) == len(qas)
    assert retrieved[0]["question"] == qas[0].question

# ------------------ Test Transcript ------------------

def test_set_transcript(setup_workflow_and_interview):
    user_id, _, interview_id = setup_workflow_and_interview
    turns = [TranscriptTurn(**t) for t in transcript]

    retrieved = database.firestore_db.get_transcript(user_id, interview_id)
    assert retrieved is not None
    assert len(retrieved) == len(turns)
    assert retrieved[0]["text"] == turns[0].text

# ------------------ Test Feedback ------------------

def test_set_feedback(setup_workflow_and_interview):
    user_id, _, interview_id = setup_workflow_and_interview
    feedback_obj = Feedback(**feedback)


    retrieved = database.firestore_db.get_feedback(user_id, interview_id)
    assert retrieved is not None
    assert retrieved["overallRating"] == feedback["overallRating"]

# ------------------ Test General BQs ------------------

def test_set_general_bqs():
    bqs = [GeneralBQ(**bq) for bq in generalBQ]

    result = database.firestore_db.set_general_bqs(bqs)
    assert "successfully" in result["message"]

    retrieved = database.firestore_db.get_general_bqs()
    assert retrieved is not None
    assert len(retrieved) == len(bqs)
    assert retrieved[0]["question"] == bqs[0].question

# ------------------ Test Profile ------------------

def test_create_update_profile():
    # Cast URL/email fields to string so Pydantic doesn't use HttpUrl/EmailStr types
    profile = Profile(**profile_data)

    result = database.firestore_db.create_or_update_profile(TEST_USER_ID, profile)
    assert "successfully" in result["message"]

    retrieved = database.firestore_db.get_profile(TEST_USER_ID)
    assert retrieved is not None
    assert retrieved["name"] == profile.name
    assert retrieved["email"] == profile.email

def test_update_profile():
    # Start from the original profile
    original_profile = Profile(**profile_data)

    # Modify the name only
    updated_profile = original_profile.model_copy(update={"name": "Updated Jenny"})

    result = database.firestore_db.create_or_update_profile(TEST_USER_ID, updated_profile)
    assert "successfully" in result["message"]

    retrieved = database.firestore_db.get_profile(TEST_USER_ID)
    assert retrieved["name"] == "Updated Jenny"
    assert retrieved["email"] == "jenny.cheng@example.com"  # old value should still exist
