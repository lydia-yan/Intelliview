from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime
from typing import List, Dict, Optional, Any

# Profile Schema
class Profile(BaseModel):
    name: str
    email: EmailStr = None
    photoURL: HttpUrl = None
    linkedinLink: HttpUrl = None
    githubLink: HttpUrl = None
    portfolioLink: HttpUrl = None
    additionalInfo: str = None
    createAt: datetime = None

# Interview Schema
class TranscriptTurn(BaseModel):
    speaker: str # "AI" or "user"
    text: str

class Interview(BaseModel):
    transcript: List[Dict[str, Any]]  = None
    feedback: Dict[str, Any] = None
    createAt: datetime = None
    workflowId: str = None #assign it after creation 

# Feedback Schema (nested within Interview)
class FeedbackImprovementArea(BaseModel):
    topic: str
    example: str
    suggestion: str

class FeedbackResource(BaseModel):
    title: str
    link: str

class Feedback(BaseModel):
    positives: List[str]
    improvementAreas: List[FeedbackImprovementArea]
    resources: List[FeedbackResource]
    reflectionPrompt: List[str]
    tone: str
    overallRating: int
    focusTags: List[str]

# PersonalExperience and RecommendedQA (nested within Workflow)
class PersonalExperience(BaseModel):
    resumeInfo: str
    linkedinInfo: str
    githubInfo: str
    portfolioInfo: str
    additionalInfo: Optional[str]
    jobDescription: str

class RecommendedQA(BaseModel):
    question: str
    answer: str
    tags: List[str]

# Workflow Schema
class Workflow(BaseModel):
    title: str = None
    personalExperience: Dict = None
    recommendedQAs: List[Dict[str, Any]] = None
    createAt: datetime = None
    # Note: personalExperience and recommendedQAs are managed separately in database.py
    # We'll leave them out of the Workflow model to match the database structure
    # personalExperience: PersonalExperience  # Added via set_personal_experience
    # recommendedQAs: List[RecommendedQA]  # Added via set_recommended_qas

# System Data Schema
class GeneralBQ(BaseModel):
    id: str #use for document name and will not include in the data
    question: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None

