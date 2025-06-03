"""
GitHub Analysis Exceptions

Custom exceptions for GitHub analysis operations.
"""


class GitHubAnalysisError(Exception):
    """Base exception for GitHub analysis operations"""
    pass


class GitHubAPIError(GitHubAnalysisError):
    """Exception raised when GitHub API calls fail"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class InvalidGitHubURLError(GitHubAnalysisError):
    """Exception raised when GitHub URL is invalid or cannot be parsed"""
    pass


class GitHubRateLimitError(GitHubAPIError):
    """Exception raised when GitHub API rate limit is exceeded"""
    pass


class GitHubUserNotFoundError(GitHubAPIError):
    """Exception raised when GitHub user is not found"""
    pass


class GitHubRepositoryNotFoundError(GitHubAPIError):
    """Exception raised when GitHub repository is not found"""
    pass 