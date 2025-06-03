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
    duration: int = 15 #can set the default value here
    is_audio: bool = False
