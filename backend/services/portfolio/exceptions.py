"""
Custom exceptions for portfolio analysis service
"""

class PortfolioAnalysisError(Exception):
    """Base exception for portfolio analysis errors"""
    
    def __init__(self, message: str, url: str = ""):
        self.message = message
        self.url = url
        super().__init__(self.message)

class PortfolioURLError(PortfolioAnalysisError):
    """Exception raised for invalid or inaccessible URLs"""
    
    def __init__(self, url: str, message: str = "Invalid or inaccessible URL"):
        super().__init__(message, url)

class PortfolioScrapingError(PortfolioAnalysisError):
    """Exception raised when web scraping fails"""
    
    def __init__(self, url: str, message: str = "Failed to scrape portfolio content"):
        super().__init__(message, url)

class PortfolioTimeoutError(PortfolioAnalysisError):
    """Exception raised when portfolio analysis times out"""
    
    def __init__(self, url: str, timeout: int = 30):
        message = f"Portfolio analysis timed out after {timeout} seconds"
        super().__init__(message, url)

class PortfolioContentError(PortfolioAnalysisError):
    """Exception raised when portfolio content cannot be extracted or processed"""
    
    def __init__(self, url: str, message: str = "Failed to extract portfolio content"):
        super().__init__(message, url) 