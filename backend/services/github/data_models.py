"""
GitHub Data Models

Data classes for representing GitHub user profiles and repository information.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class GitHubRepository:
    """Represents a GitHub repository"""
    
    name: str
    description: Optional[str]
    language: Optional[str]
    topics: List[str]
    readme_content: Optional[str] = None
    
    @classmethod
    def from_api_response(cls, repo_data: Dict[str, Any]) -> 'GitHubRepository':
        """Create GitHubRepository instance from GitHub API response"""
        return cls(
            name=repo_data.get('name', ''),
            description=repo_data.get('description'),
            language=repo_data.get('language'),
            topics=repo_data.get('topics', [])
        )
    
    def to_summary_text(self) -> str:
        """Convert repository info to human-readable summary text"""
        summary = f"Repository: {self.name}"
        if self.description:
            summary += f" - {self.description}"
        if self.language:
            summary += f" (Language: {self.language})"
        if self.topics:
            summary += f" Topics: {', '.join(self.topics)}"
        return summary


@dataclass 
class GitHubProfile:
    """Represents a GitHub user profile with interview-relevant information"""
    
    username: str
    name: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    
    # Repository lists
    top_repositories: List[GitHubRepository]
    recent_repositories: List[GitHubRepository]
    
    # Aggregated statistics
    primary_languages: List[str] = None
    
    @classmethod
    def from_api_response(cls, user_data: Dict[str, Any]) -> 'GitHubProfile':
        """Create GitHubProfile instance from GitHub API response"""
        return cls(
            username=user_data.get('login', ''),
            name=user_data.get('name'),
            bio=user_data.get('bio'),
            company=user_data.get('company'),
            top_repositories=[],
            recent_repositories=[],
            primary_languages=[]
        )
    
    def calculate_statistics(self):
        """Calculate aggregated statistics from repositories"""
        all_repos = self.top_repositories + self.recent_repositories
        
        # Remove duplicates by name
        unique_repos = {repo.name: repo for repo in all_repos}.values()
        
        # Count languages
        language_count = {}
        for repo in unique_repos:
            if repo.language:
                language_count[repo.language] = language_count.get(repo.language, 0) + 1
        
        # Sort by frequency and take top 3
        self.primary_languages = sorted(language_count.keys(), 
                                      key=lambda x: language_count[x], 
                                      reverse=True)[:3]
    
    def to_summary_text(self) -> str:
        """Convert profile info to human-readable summary text for workflow input"""
        summary_parts = []
        
        # Basic info
        if self.name and self.name != self.username:
            summary_parts.append(f"GitHub Profile: {self.name} (@{self.username})")
        else:
            summary_parts.append(f"GitHub Profile: @{self.username}")
        
        if self.bio:
            summary_parts.append(f"Bio: {self.bio}")
            
        if self.company:
            summary_parts.append(f"Company: {self.company}")
            
        if self.primary_languages:
            summary_parts.append(f"Primary languages: {', '.join(self.primary_languages)}")
        
        # Top repositories (limit to top 3 for interview relevance)
        if self.top_repositories:
            summary_parts.append("\nNotable Repositories:")
            for repo in self.top_repositories[:3]:
                summary_parts.append(f"- {repo.to_summary_text()}")
                if repo.readme_content:
                    # Include first 150 chars of README
                    readme_preview = repo.readme_content[:150].strip()
                    if readme_preview:
                        summary_parts.append(f"  Description: {readme_preview}...")
        
        return "\n".join(summary_parts) 