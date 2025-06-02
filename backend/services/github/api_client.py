"""
GitHub API Client

Handles all GitHub REST API interactions with proper error handling,
rate limiting, and authentication.
"""

import requests
import time
import base64
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import os
from pathlib import Path
from dotenv import load_dotenv

from .exceptions import (
    GitHubAPIError, 
    GitHubRateLimitError, 
    GitHubUserNotFoundError,
    InvalidGitHubURLError
)


class GitHubAPIClient:
    """Client for interacting with GitHub REST API"""
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client
        
        Args:
            token: Optional GitHub personal access token for higher rate limits
        """
        # Load environment variables from backend/.env file
        backend_dir = Path(__file__).parent.parent.parent
        env_file_path = backend_dir / ".env"
        if env_file_path.exists():
            load_dotenv(env_file_path)
        
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            'Accept': 'application/vnd.github+json',
            'User-Agent': 'GitHub-Profile-Analyzer/1.0',
            'X-GitHub-Api-Version': '2022-11-28'
        })
        
        if self.token:
            self.session.headers['Authorization'] = f'token {self.token}'
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """
        Make authenticated request to GitHub API with error handling
        
        Args:
            endpoint: API endpoint (e.g., '/users/username')
            params: Optional query parameters
            
        Returns:
            dict: JSON response from API
            
        Raises:
            GitHubAPIError: For various API errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.get(url, params=params)
            
            # Handle rate limiting
            if response.status_code == 403:
                if 'rate limit exceeded' in response.text.lower():
                    reset_time = response.headers.get('X-RateLimit-Reset')
                    if reset_time:
                        wait_time = int(reset_time) - int(time.time())
                        raise GitHubRateLimitError(
                            f"Rate limit exceeded. Resets in {wait_time} seconds",
                            status_code=403
                        )
                    else:
                        raise GitHubRateLimitError("Rate limit exceeded", status_code=403)
            
            # Handle not found
            if response.status_code == 404:
                if '/users/' in endpoint:
                    raise GitHubUserNotFoundError(
                        f"User not found: {endpoint}",
                        status_code=404
                    )
            
            # Handle other HTTP errors
            if not response.ok:
                error_data = response.json() if response.content else {}
                raise GitHubAPIError(
                    f"GitHub API error: {response.status_code} - {error_data.get('message', 'Unknown error')}",
                    status_code=response.status_code
                )
            
            return response.json()
            
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error when calling GitHub API: {str(e)}")
    
    def get_user(self, username: str) -> Dict[str, Any]:
        """
        Get user profile information
        
        Args:
            username: GitHub username
            
        Returns:
            dict: User profile data from GitHub API
        """
        return self._make_request(f"/users/{username}")
    
    def get_user_repos(self, username: str, sort: str = "updated", per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Get user's public repositories
        
        Args:
            username: GitHub username
            sort: Sort order ('created', 'updated', 'pushed', 'full_name')
            per_page: Number of repos per page (max 100)
            
        Returns:
            list: List of repository data from GitHub API
        """
        params = {
            'sort': sort,
            'per_page': per_page,
            'type': 'owner'  # Only repos owned by user, not forks
        }
        return self._make_request(f"/users/{username}/repos", params=params)
    
    def get_repository(self, owner: str, repo_name: str) -> Dict[str, Any]:
        """
        Get detailed repository information
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            dict: Repository data from GitHub API
        """
        return self._make_request(f"/repos/{owner}/{repo_name}")
    
    def get_repository_readme(self, owner: str, repo_name: str) -> Optional[str]:
        """
        Get repository README content
        
        Args:
            owner: Repository owner username
            repo_name: Repository name
            
        Returns:
            str: README content in plain text, or None if not found
        """
        try:
            readme_data = self._make_request(f"/repos/{owner}/{repo_name}/readme")
            
            # Decode base64 content
            content = readme_data.get('content', '')
            if content:
                # Remove newlines and decode base64
                content = content.replace('\n', '')
                decoded_content = base64.b64decode(content).decode('utf-8')
                return decoded_content
                
        except (GitHubAPIError):
            # README not found or other error, return None
            pass
        
        return None
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """
        Get current rate limit status
        
        Returns:
            dict: Rate limit information
        """
        return self._make_request("/rate_limit")
    
    @staticmethod
    def parse_github_url(url: str) -> tuple[str, Optional[str]]:
        """
        Parse GitHub URL to extract username and optional repository name
        
        Args:
            url: GitHub URL (e.g., 'https://github.com/username' or 'https://github.com/username/repo')
            
        Returns:
            tuple: (username, repo_name) where repo_name can be None
            
        Raises:
            InvalidGitHubURLError: If URL is not a valid GitHub URL
        """
        if not url:
            raise InvalidGitHubURLError("URL cannot be empty")
        
        # Handle URLs without protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            
            # Check if it's a GitHub URL
            if parsed.netloc.lower() not in ('github.com', 'www.github.com'):
                raise InvalidGitHubURLError(f"Not a GitHub URL: {url}")
            
            # Parse path
            path_parts = [p for p in parsed.path.split('/') if p]
            
            if len(path_parts) == 0:
                raise InvalidGitHubURLError("No username found in GitHub URL")
            elif len(path_parts) == 1:
                # Just username: https://github.com/username
                return path_parts[0], None
            elif len(path_parts) >= 2:
                # Username and repo: https://github.com/username/repo
                return path_parts[0], path_parts[1]
            else:
                raise InvalidGitHubURLError(f"Invalid GitHub URL format: {url}")
                
        except Exception as e:
            if isinstance(e, InvalidGitHubURLError):
                raise
            raise InvalidGitHubURLError(f"Failed to parse GitHub URL: {url}")
    
    def test_connection(self) -> bool:
        """
        Test if the API client can successfully connect to GitHub
        
        Returns:
            bool: True if connection is successful
        """
        try:
            self.get_rate_limit_status()
            return True
        except Exception:
            return False 