"""
Data models for portfolio analysis service
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class ProjectInfo:
    """Information about a single project in the portfolio"""
    
    name: str
    description: str = ""
    technologies: List[str] = field(default_factory=list)
    url: Optional[str] = None
    
    def __post_init__(self):
        """Ensure technologies is always a list"""
        if self.technologies is None:
            self.technologies = []

@dataclass
class PortfolioData:
    """Complete portfolio information extracted from a website"""
    
    url: str
    title: str = ""
    description: str = ""
    projects: List[ProjectInfo] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    experience: str = ""
    raw_content: str = ""
    extraction_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize default values and timestamp"""
        if self.projects is None:
            self.projects = []
        if self.skills is None:
            self.skills = []
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()
    
    def to_formatted_string(self) -> str:
        """
        Convert portfolio data to formatted string suitable for LLM input
        
        Returns:
            str: Human-readable portfolio summary
        """
        sections = []
        
        if self.title:
            sections.append(f"Portfolio Title: {self.title}")
            
        if self.description:
            sections.append(f"About: {self.description}")
            
        if self.projects:
            sections.append("Projects:")
            for i, project in enumerate(self.projects, 1):
                project_info = f"{i}. {project.name}"
                if project.description:
                    project_info += f": {project.description}"
                if project.technologies:
                    tech_stack = ", ".join(project.technologies)
                    project_info += f" (Technologies: {tech_stack})"
                if project.url:
                    project_info += f" [Link: {project.url}]"
                sections.append(f"   {project_info}")
                
        if self.skills:
            skills_text = ", ".join(self.skills)
            sections.append(f"Technical Skills: {skills_text}")
            
        if self.experience:
            sections.append(f"Experience Summary: {self.experience}")
            
        # Fallback to raw content if no structured content found
        if not any([self.title, self.description, self.projects, self.skills, self.experience]):
            if self.raw_content:
                truncated_content = self.raw_content[:1000] + "..." if len(self.raw_content) > 1000 else self.raw_content
                sections.append(f"Raw Portfolio Content: {truncated_content}")
            else:
                sections.append("No portfolio content could be extracted from the provided URL.")
        
        return "\n".join(sections)
    
    def has_content(self) -> bool:
        """
        Check if the portfolio data contains any meaningful content
        
        Returns:
            bool: True if portfolio has extractable content
        """
        return any([
            self.title,
            self.description,
            self.projects,
            self.skills,
            self.experience,
            self.raw_content
        ]) 