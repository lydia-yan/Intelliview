from backend.data.schemas import (
    Profile, Interview, Workflow, Feedback,
    PersonalExperience, RecommendedQA, TranscriptTurn, GeneralBQ
)
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import HttpUrl, EmailStr
import os
from dotenv import load_dotenv 
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

# Resolve the path to the Firebase key relative to the backend/ directory
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # backend/
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
if not firebase_key_path:
    raise ValueError("FIREBASE_KEY_PATH environment variable not set")

# Construct the absolute path to the Firebase key
firebase_key = os.path.join(backend_dir, firebase_key_path)
if not os.path.exists(firebase_key):
    raise FileNotFoundError(f"Firebase key file not found at {firebase_key}")

# Initialize Firebase (only if not already initialized)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key)
    firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

class FirestoreDB:
    def __init__(self,db):
        """Initialize Firestore client."""
        self.db = db

    # --- Profile Operations ---
    def create_or_update_profile(self, user_id: str, profile_data: Profile) -> Dict[str, str]:
        """Create or update profile fields directly in the user's document."""
        user_ref = self.db.collection('users').document(user_id)

        # Ensure timestamp is set
        if not profile_data.createAt:
            profile_data.createAt = datetime.now(timezone.utc)

        # Convert to dictionary and cast URL fields to strings
        profile_dict = profile_data.model_dump(exclude_unset=True)
        for key, value in profile_dict.items():
            if isinstance(value, (HttpUrl, EmailStr)):
                profile_dict[key] = str(value)

        user_ref.set(profile_dict, merge=True)  # Store fields at root of the user doc
        return {"message": f"Profile for user {user_id} created/updated successfully"}

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def delete_profile(self, user_id: str) -> Dict[str, str]:
        """Clear profile fields by setting them to delete sentinel."""
        user_ref = self.db.collection('users').document(user_id)
        user_ref.update({
            "name": firestore.DELETE_FIELD,
            "email": firestore.DELETE_FIELD,
            "photoURL": firestore.DELETE_FIELD,
            "linkedinLink": firestore.DELETE_FIELD,
            "githubLink": firestore.DELETE_FIELD,
            "portfolioLink": firestore.DELETE_FIELD,
            "additionalInfo": firestore.DELETE_FIELD,
            "createAt": firestore.DELETE_FIELD,
        })
        return {"message": f"Profile fields for user {user_id} deleted successfully"}

    # --- Interview Operations ---
    def create_interview(self, user_id: str, workflow_id: str, interview_data: Interview) -> Dict[str, str]:
        """Create a new interview record with a unique interviewId."""
        interviews_ref = self.db.collection('users').document(user_id).collection('interviews')
        doc_ref = interviews_ref.document() 

        interview_id = doc_ref.id
        interview_data.workflowId = workflow_id
        interview_data.createAt = datetime.now(timezone.utc)

        doc_ref.set(interview_data.model_dump(), merge=True)
        return {
            "message": f"Interview {interview_id} created for user {user_id}",
            "interviewId": interview_id
        }


    def get_interview(self, user_id: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an interview record."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(interview_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def delete_interview(self, user_id: str, interview_id: str) -> Dict[str, str]:
        """Delete an interview record."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(interview_id)
        doc_ref.delete()
        return {"message": f"Interview {interview_id} for user {user_id} deleted successfully"}

    # --- Workflow Operations ---
    def create_or_update_workflow(self, user_id: str, workflow_data: Workflow) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document()
        workflow_id = doc_ref.id
        
        workflow_data.createAt = datetime.now(timezone.utc)
        doc_ref.set(workflow_data.model_dump(), merge = True)

        return {"message": f"Workflow {workflow_id} created", "workflowId": workflow_id}

    def get_workflow(self, user_id: str, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a workflow record."""
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def delete_workflow(self, user_id: str, workflow_id: str) -> Dict[str, str]:
        """Delete a workflow record."""
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc_ref.delete()
        return {"message": f"Workflow {workflow_id} for user {user_id} deleted successfully"}

    # --- Personal Experience in Workflow ---
    def set_personal_experience(self, user_id: str, workflow_id: str, experience: PersonalExperience) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc_ref.set({"personalExperience": experience.model_dump()}, merge=True)
        return {"message": f"Personal experience for user {user_id}, workflow {workflow_id} set successfully"}

    def get_personal_experience(self, user_id: str, workflow_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("personalExperience")
        return None

    # --- Recommended QAs in Workflow ---
    def set_recommended_qas(self, user_id: str, workflow_id: str, qas: List[RecommendedQA]) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc_ref.set({"recommendedQAs": [qa.model_dump() for qa in qas]}, merge=True)
        return {"message": f"Recommended QAs for user {user_id}, workflow {workflow_id} set successfully"}

    def get_recommended_qas(self, user_id: str, workflow_id: str) -> Optional[List[Dict[str, Any]]]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("recommendedQAs")
        return None

    # --- Transcript Operations ---
    def set_transcript(self, user_id: str, interview_id: str, transcript: List[TranscriptTurn]) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(interview_id)
        doc_ref.set({"transcript": [turn.model_dump() for turn in transcript]}, merge=True)
        return {"message": f"Transcript set for interview {interview_id}"}

    def get_transcript(self, user_id: str, interview_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve transcript of an interview."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(interview_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("transcript", [])
        return None

    # --- Feedback Operations ---
    def set_feedback(self, user_id: str, interview_id: str, feedback: Feedback) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(interview_id)
        doc_ref.set({"feedback": feedback.model_dump()}, merge=True)
        return {"message": f"Feedback set for interview {interview_id}"}
    
    def get_feedback(self, user_id: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve feedback of an interview."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(interview_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get("feedback", None)
        return None

    # --- General Behavioral Questions Operations ---
    def set_general_bqs(self, bqs: List[GeneralBQ]) -> Dict[str, str]:
        """Set general behavioral questions."""
        doc_ref = self.db.collection("bqs")
        for bq in bqs:
            doc_ref.document(bq.id).set(bq.model_dump(exclude={"id"}))
        return {"message": "General behavioral questions set successfully"}

    def get_general_bqs(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve general behavioral questions."""
        docs = list(self.db.collection("bqs").stream())
        if not docs:
            return None
        return [doc.to_dict() for doc in docs]
    

    def delete_general_bqs(self) -> Dict[str, str]:
        """Delete system data (general questions)."""
        docs = list(self.db.collection("bqs").stream())
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1

        return {"message": f"Deleted {deleted_count} behavioral questions from 'bqs' collection."}
# Create shared FirestoreDB instance
firestore_db = FirestoreDB(db)