from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import HttpUrl, EmailStr
from firebase_admin import firestore

from backend.data.schemas import (
    Profile, Interview, Workflow, Feedback,
    PersonalExperience, RecommendedQA, GeneralBQ, CodingProblems
)
from backend.tools.firebase_config import db

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
        return {
            "message": f"Profile for user {user_id} created/updated successfully",
            "data": profile_dict
        }


    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection('users').document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return {
                    "message": f"Profile for user {user_id} retrieved successfully",
                    "data": doc.to_dict()
                }
        else:
            return {
                "message": f"Profile for user {user_id} not found",
                "data": None
            }

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
        return {
            "message": f"Profile fields for user {user_id} deleted successfully",
            "data": None
        }

    # --- Interview Operations ---
    def create_interview(self, user_id: str, session_id: str, workflow_id: str, interview_data: Interview) -> Dict[str, str]:
        """Create a new interview record with a unique interviewId."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(workflow_id).collection("sessions").document(session_id)
        interview_data.createAt = datetime.now(timezone.utc)

        doc_ref.set(interview_data.model_dump(),merge=True)
        return {
            "message": f"Interview {session_id} successfully created for user {user_id}",
            "data": None
        }

    def get_interview(self, user_id: str, workflow_id: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an interview record."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(workflow_id).collection("sessions").document(interview_id)
        doc = doc_ref.get()
        if doc.exists:
            return {
                "message": f"Interview {interview_id} retrieved successfully",
                "data": doc.to_dict()
            }
        else:
            return {
                "message": f"Interview {interview_id} not found",
                "data": None
            }
    
    def get_interviews_for_workflow(self, user_id: str, workflow_id: str) -> List[Dict[str, Any]]:
        """
        Get all interview session data under a specific workflow for a user.
        """
        sessions_ref = self.db.collection("users").document(user_id).collection("interviews").document(workflow_id).collection("sessions")

        docs = sessions_ref.stream()
        results = []

        for doc in docs:
            data = doc.to_dict()
            data["interviewId"] = doc.id 
            results.append(data)

        return {
            "message": f"Found {len(results)} interview(s) for workflow {workflow_id} successfully",
            "data": results
        }


    def delete_interview(self, user_id: str, workflow_id: str, interview_id: str) -> Dict[str, str]:
        """Delete an interview record."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(workflow_id).collection("sessions").document(interview_id)
        doc_ref.delete()
        return {
            "message": f"Interview {interview_id} for user {user_id} deleted successfully",
            "data": None
        }
    # --- Workflow Operations ---
    def create_or_update_workflow(self, user_id: str, session_id: str, workflow_data: Workflow) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(session_id)
        workflow_data.createAt = datetime.now(timezone.utc)
        doc_ref.set(workflow_data.model_dump(), merge = True)

        return {
            "message": f"Workflow {session_id} successfully created/update for user {user_id}",
            "data": None
        }
    
    def get_workflow(self, user_id: str, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a workflow record."""
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc = doc_ref.get()
        if doc.exists:
            return {
                "message": f"Workflow {workflow_id} retrieved successfully for user {user_id}",
                "data": doc.to_dict()
            }
        else:
            return {
                "message": f"Workflow {workflow_id} not found for user {user_id}",
                "data": None
            }

    def delete_workflow(self, user_id: str, workflow_id: str) -> Dict[str, str]:
        """Delete a workflow record."""
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc_ref.delete()
        return {
            "message": f"Workflow {workflow_id} for user {user_id} deleted successfully",
            "data": None
        }
    
    def get_workflows_for_user(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get a list of workflow summaries (workflow_id and title) for a user.
        """
        workflows_ref = self.db.collection('users').document(user_id).collection('workflows')
        docs = workflows_ref.stream()
        
        result = []
        for doc in docs:
            data = doc.to_dict()
            data["workflowId"] = doc.id  
            result.append(data)

        return {
            "message": f"Found {len(result)} workflows found for user {user_id} successfully",
            "data": result
        }

    # --- Personal Experience in Workflow ---
    def set_personal_experience(self, user_id: str, workflow_id: str, experience: PersonalExperience) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc_ref.set({"personalExperience": experience.model_dump()}, merge=True)
        return {
            "message": f"Personal experience for user {user_id}, workflow {workflow_id} set successfully",
            "data": None
        }

    def get_personal_experience(self, user_id: str, workflow_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc = doc_ref.get()
        if doc.exists and "personalExperience" in doc.to_dict():
            return {
                "message": f"Personal experience for user {user_id}, workflow {workflow_id} retrieved successfully",
                "data": doc.to_dict().get("personalExperience")
            }
        return {
            "message": f"Personal experience not found for user {user_id}, workflow {workflow_id}",
            "data": None
        }

    # --- Recommended QAs in Workflow ---
    def set_recommended_qas(self, user_id: str, workflow_id: str, qas: List[RecommendedQA]) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc_ref.set({"recommendedQAs": [qa.model_dump() for qa in qas]}, merge=True)
        return {
            "message": f"Recommended QAs for user {user_id}, workflow {workflow_id} set successfully",
            "data": None
        }

    def get_recommended_qas(self, user_id: str, workflow_id: str) -> Optional[List[Dict[str, Any]]]:
        doc_ref = self.db.collection('users').document(user_id).collection('workflows').document(workflow_id)
        doc = doc_ref.get()
        if doc.exists and "recommendedQAs" in doc.to_dict():
            return {
                "message": f"Recommended QAs retrieved for user {user_id}, workflow {workflow_id} successfully",
                "data": doc.to_dict().get("recommendedQAs")
            }
        return {
            "message": f"Recommended QAs not found for user {user_id}, workflow {workflow_id}",
            "data": None
        }

    # --- Transcript Operations ---
    def get_transcript(self, user_id: str, workflow_id: str, interview_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve transcript of an interview."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(workflow_id).collection("sessions").document(interview_id)
        doc = doc_ref.get()
        if doc.exists and "transcript" in doc.to_dict():
            return {
                "message": f"Transcript retrieved for interview {interview_id} successfully",
                "data": doc.to_dict().get("transcript")
            }
        return {
            "message": f"Transcript not found for interview {interview_id}",
            "data": None
        }

    # --- Feedback Operations ---
    def set_feedback(self, user_id: str, workflow_id: str, interview_id: str, feedback: Feedback) -> Dict[str, str]:
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(workflow_id).collection("sessions").document(interview_id)
        doc_ref.set({"feedback": feedback.model_dump()}, merge=True)
        return {
            "message": f"Feedback set for interview {interview_id} successfully",
            "data": None
        }
    
    def get_feedback(self, user_id: str, workflow_id: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve feedback of an interview."""
        doc_ref = self.db.collection('users').document(user_id).collection('interviews').document(workflow_id).collection("sessions").document(interview_id)
        doc = doc_ref.get()
        if doc.exists and "feedback" in doc.to_dict():
            return {
                "message": f"Feedback retrieved for interview {interview_id} successfully",
                "data": doc.to_dict().get("feedback")
            }
        return {
            "message": f"Feedback not found for interview {interview_id}",
            "data": None
        }

    # --- General Behavioral Questions Operations ---
    def set_general_bqs(self, bqs: List[GeneralBQ]) -> Dict[str, str]:
        """Set general behavioral questions."""
        doc_ref = self.db.collection("bqs")
        for bq in bqs:
            doc_ref.document(bq.id).set(bq.model_dump(exclude={"id"}))
        return {
            "message": "General behavioral questions set successfully",
            "data": None
        }

    def get_general_bqs(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieve general behavioral questions."""
        docs = list(self.db.collection("bqs").stream())
        if not docs:
            return {
                "message": "Behavioral questions not found",
                "data": None
            }
        return {
            "message": "Behavioral questions retrieved successfully",
            "data": [doc.to_dict() for doc in docs]
        }
        

    def delete_general_bqs(self) -> Dict[str, str]:
        """Delete system data (general questions)."""
        docs = list(self.db.collection("bqs").stream())
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1

        return {
            "message": f"Deleted {deleted_count} behavioral questions from 'bqs' collection successfully",
            "data": None
        }
    
    # --- Coding Problems Operations ---
    def set_coding_problems(self, problems: List[CodingProblems]) -> Dict[str, str]:
        """Set coding problems."""
        col = self.db.collection("problems")
        BATCH_SIZE = 500
        written = 0
        batches = 0

        for start in range(0, len(problems), BATCH_SIZE):
            batch = self.db.batch()
            for p in problems[start:start + BATCH_SIZE]:
                doc_id = str(p.id)  # ensure string
                data = p.model_dump(exclude={"id"})
                batch.set(col.document(doc_id), data, merge=True)  # merge=False to overwrite
                written += 1
            batch.commit()
            batches += 1

        return {
            "message": "Coding problems written",
            "written": written,
            "batches": batches,
        }


    def get_coding_problems(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single coding problem by ID."""
        doc_ref = self.db.collection("problems").document(problem_id).get()
        if not doc_ref.exists:
            return {
                "message": f"Coding problem with id {problem_id} not found",
                "data": None
            }
        return {
            "message": "Coding problem retrieved successfully",
            "data": doc_ref.to_dict()
        }
        

    def delete_coding_problems(self) -> Dict[str, str]:
        """Delete system data (coding problems)."""
        docs = list(self.db.collection("problems").stream())
        deleted_count = 0
        for doc in docs:
            doc.reference.delete()
            deleted_count += 1

        return {
            "message": f"Deleted {deleted_count} coding problems from 'problems' collection successfully",
            "data": None
        }
    

# Create shared FirestoreDB instance
firestore_db = FirestoreDB(db)
