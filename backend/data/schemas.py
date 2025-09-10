from pydantic import BaseModel, Field, HttpUrl, EmailStr
from datetime import datetime
from typing import List, Dict, Optional, Any

# Profile Schema
class Profile(BaseModel):
    name: str = None
    email: EmailStr = None
    photoURL: HttpUrl = None
    linkedinLink: HttpUrl = None
    githubLink: HttpUrl = None
    portfolioLink: HttpUrl = None
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


# Coding Problem Data Schema
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
    solutions: Optional[SolutionCode] = None
    similar_questions: List[SimilarQuestion] = []


# Coding Review Data Schema
class ScoreBreakdown(BaseModel):
    correctness: float = Field(..., ge=0, le=100)
    efficiency: float = Field(..., ge=0, le=100)
    robustness: float = Field(..., ge=0, le=100)
    style: float = Field(..., ge=0, le=100)
    efficiency_breakdown: Optional[Dict[str, Dict[str, float]]] = None


class ConversationScores(BaseModel):
    understanding: float = Field(..., ge=0, le=100)
    awareness: float = Field(..., ge=0, le=100)
    defense: float = Field(..., ge=0, le=100)
    clarity: float = Field(..., ge=0, le=100)


class Scores(BaseModel):
    overall: float = Field(..., ge=0, le=100)
    code_score: ScoreBreakdown
    conversation_score: ConversationScores


class CodingFeedback(BaseModel):
    code: Optional[List[str]] = []
    conversation: Optional[List[str]] = []
    strength: str
    opportunity: str
    next_step: Dict[str, List[str]]


class CodingReview(BaseModel):
    problem_slug: Optional[str] = None
    scores: Scores
    feedback: CodingFeedback
    reviewer_result: Dict[str, Any]  # raw JSON from AI reviewer
    optimal_complexity: Dict[str, Any]  # {"time":..., "space":..., "edge_keywords": [...]}
    transcript: List[Dict[str, Any]] 
    createAt: datetime = None

# --- Code submission
class CodeSubmission(BaseModel):
    code: str
    language: str
    claimed_time: str 
    claimed_space: str
    createAt: datetime = None