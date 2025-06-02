"""
GitHub Profile Analyzer

Main business logic for analyzing GitHub profiles and repositories.
Simplified for interview preparation workflow.
"""

import asyncio
from typing import Optional, List
import logging

from .api_client import GitHubAPIClient
from .data_models import GitHubProfile, GitHubRepository
from .exceptions import (
    GitHubAnalysisError,
    InvalidGitHubURLError,
    GitHubUserNotFoundError,
)

logger = logging.getLogger(__name__)


class GitHubAnalyzer:
    """Analyzes GitHub profiles and repositories for interview preparation workflow"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub analyzer
        
        Args:
            github_token: Optional GitHub personal access token for higher rate limits
        """
        self.api_client = GitHubAPIClient(token=github_token)
        
    async def analyze_github_profile(self, github_url: str) -> GitHubProfile:
        """
        Analyze a GitHub profile from URL and return profile data
        
        Args:
            github_url: GitHub profile URL (e.g., 'https://github.com/username')
            
        Returns:
            GitHubProfile: Profile analysis for interview preparation
        """
        try:
            # Parse URL to extract username
            username, repo_name = self.api_client.parse_github_url(github_url)
            
            if repo_name:
                logger.warning(f"Repository URL provided, extracting user: {username}")
            
            logger.info(f"Starting analysis for GitHub user: {username}")
            
            # Get user profile
            user_data = self.api_client.get_user(username)
            profile = GitHubProfile.from_api_response(user_data)
            
            # Get repositories
            await self._fetch_repositories(profile)
            
            # Calculate aggregated statistics
            profile.calculate_statistics()
            
            logger.info(f"Successfully analyzed GitHub profile for {username}")
            return profile
            
        except (InvalidGitHubURLError, GitHubUserNotFoundError):
            raise
        except Exception as e:
            logger.error(f"Error analyzing GitHub profile: {str(e)}")
            raise GitHubAnalysisError(f"Failed to analyze GitHub profile: {str(e)}")
    
    async def _fetch_repositories(self, profile: GitHubProfile):
        """
        Fetch and categorize repositories for the profile
        
        Args:
            profile: GitHubProfile to populate with repository data
        """
        try:
            # Get user repositories
            repos_data = self.api_client.get_user_repos(
                profile.username, 
                sort="updated",
                per_page=50  # Reduced for efficiency
            )
            
            if not repos_data:
                logger.warning(f"No repositories found for user {profile.username}")
                return
            
            # Convert to GitHubRepository objects
            repositories = [
                GitHubRepository.from_api_response(repo_data) 
                for repo_data in repos_data
            ]
            
            # Get top repositories by language diversity (limit to 5)
            profile.top_repositories = repositories[:5]
            
            # Get recent repositories (limit to 3)
            profile.recent_repositories = sorted(
                [repo for repo in repositories if hasattr(repo, 'name')],
                key=lambda repo: repo.name,  # Simple sort by name as fallback
                reverse=True
            )[:3]
            
            # Fetch README content for top 2 repositories only
            await self._fetch_readme_content(profile.top_repositories[:2])
            
        except Exception as e:
            logger.error(f"Error fetching repositories for {profile.username}: {str(e)}")
    
    async def _fetch_readme_content(self, repositories: List[GitHubRepository]):
        """
        Fetch README content for repositories
        
        Args:
            repositories: List of repositories to fetch README for
        """
        async def fetch_single_readme(repo: GitHubRepository):
            """Fetch README for a single repository"""
            try:
                readme_content = self.api_client.get_repository_readme(
                    repo.name.split('/')[0] if '/' in repo.name else repo.name,
                    repo.name.split('/')[-1] if '/' in repo.name else repo.name
                )
                if readme_content:
                    # Limit README content size for workflow efficiency
                    repo.readme_content = readme_content[:500]
                    logger.debug(f"Fetched README for {repo.name}")
            except Exception as e:
                logger.warning(f"Could not fetch README for {repo.name}: {str(e)}")
                repo.readme_content = None
        
        # Fetch README content for repositories concurrently
        if repositories:
            tasks = [fetch_single_readme(repo) for repo in repositories]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_github_summary_for_workflow(self, github_url: str) -> str:
        """
        Get GitHub profile summary formatted for workflow input
        
        Args:
            github_url: GitHub profile URL
            
        Returns:
            str: Formatted summary text for workflow
        """
        try:
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in a running loop, create a new thread for asyncio.run
                import concurrent.futures
                
                def run_analysis():
                    return asyncio.run(self.analyze_github_profile(github_url))
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_analysis)
                    profile = future.result(timeout=30)  # 30 second timeout
                    
            except RuntimeError:
                # No running event loop, safe to use asyncio.run
                profile = asyncio.run(self.analyze_github_profile(github_url))
            
            return profile.to_summary_text()
            
        except InvalidGitHubURLError as e:
            logger.warning(f"Invalid GitHub URL provided: {str(e)}")
            return f"GitHub URL provided but invalid: {github_url}"
            
        except GitHubUserNotFoundError as e:
            logger.warning(f"GitHub user not found: {str(e)}")
            return f"GitHub profile not found: {github_url}"
            
        except GitHubAnalysisError as e:
            logger.error(f"GitHub analysis failed: {str(e)}")
            return f"GitHub analysis failed for: {github_url}"
            
        except Exception as e:
            logger.error(f"Unexpected error in GitHub analysis: {str(e)}")
            return f"Could not analyze GitHub profile: {github_url}"
    
    def test_github_connection(self) -> bool:
        """
        Test if GitHub API is accessible
        
        Returns:
            bool: True if connection successful
        """
        try:
            return self.api_client.test_connection()
        except Exception:
            return False
    
    def get_rate_limit_info(self) -> dict:
        """
        Get current GitHub API rate limit status
        
        Returns:
            dict: Rate limit information
        """
        try:
            return self.api_client.get_rate_limit_status()
        except Exception as e:
            logger.error(f"Could not get rate limit info: {str(e)}")
            return {} 