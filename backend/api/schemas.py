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