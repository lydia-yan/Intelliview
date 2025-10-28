from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime
from typing import List, Dict, Optional, Any

# Profile Schema
class Profile(BaseModel):
    name: str = None
    email: EmailStr = None
    photoURL: Optional[str] = None  # Allow empty string or None, backend will set default avatar
    linkedinLink: Optional[HttpUrl] = None  # Still validate URL format, but allow None
    githubLink: Optional[HttpUrl] = None  # Still validate URL format, but allow None
    portfolioLink: Optional[HttpUrl] = None  # Still validate URL format, but allow None
    additionalInfo: str = None
    createAt: datetime = None

# Interview Schema
class TranscriptTurn(BaseModel):
    role: str # "AI" or "user"
    message: str

class Interview(BaseModel):
    transcript: List[Dict[str, Any]] 
    duration_minutes: int
    feedback: Dict[str, Any] = None
    createAt: datetime = None

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


# Coding Problem System Data Schema
class Links(BaseModel):
    problem: Optional[str]
    description: Optional[str]
    solutions: Optional[str]


class Stats(BaseModel):
    acceptance_rate: Optional[float]
    submissions: Optional[int]
    accepted: Optional[int]
    likes: Optional[int]
    dislikes: Optional[int]


class Example(BaseModel):
    input: str
    output: str
    explanation: Optional[str] = None


class Statement(BaseModel):
    description: str
    examples: List[Example]
    constraints: List[str]


class SolutionCode(BaseModel):
    python: Optional[str] = None
    java: Optional[str] = None
    cpp: Optional[str] = None


class Solution(BaseModel):
    approach: str
    time_complexity: Optional[str] = None
    space_complexity: Optional[str] = None
    code: Optional[SolutionCode] = None


class SimilarQuestion(BaseModel):
    title: str
    slug: str
    difficulty: str


class CodingProblems(BaseModel):
    id: str
    title: str
    slug: str
    difficulty: str
    category: Optional[str] = None
    topics: Optional[List[str]] = []

    links: Links
    stats: Stats
    statement: Statement

    hints: Optional[List[str]] = []
    solutions: List[Solution] = []
    best_solution: Optional[Solution] = None
    similar_questions: List[SimilarQuestion] = []