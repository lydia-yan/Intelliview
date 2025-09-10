from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class InterviewPrepareRequest(BaseModel):
    resumeFileName: str
    resumeContent: str
    linkedinUrl: Optional[HttpUrl] = None
    githubUrl: Optional[HttpUrl] = None
    portfolioUrl: Optional[HttpUrl] = None
    additionalInfo: Optional[str] = None
    jobDescription: str


class InterviewStartRequest(BaseModel):
    workflow_id: str
    duration: int | None = None #can set the default value here
    is_audio: bool = False

class CodingSubmitRequest(BaseModel):
    problem_id: str   # or whole problem JSON, depending on how you store
    code: str
    language: str
    claimed_time: str | None = None
    claimed_space: str | None = None
    is_audio: bool = False
