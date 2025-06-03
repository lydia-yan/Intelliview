"""
Main portfolio analysis service
Coordinates web scraping and content extraction
"""

import asyncio
from typing import Optional

from .web_scraper import scrape_portfolio_url
from .content_extractor import PortfolioContentExtractor
from .data_models import PortfolioData
from .exceptions import PortfolioAnalysisError, PortfolioURLError, PortfolioScrapingError, PortfolioContentError

class PortfolioAnalyzer:
    """Main service for analyzing portfolio websites"""
    
    def __init__(self):
        self.content_extractor = PortfolioContentExtractor()
    
    async def analyze_url(self, url: str) -> PortfolioData:
        """
        Analyze a portfolio URL and extract structured information
        
        Args:
            url: Portfolio website URL
            
        Returns:
            PortfolioData: Extracted portfolio information
            
        Raises:
            PortfolioAnalysisError: If analysis fails at any stage
        """
        try:
            # Scrape the portfolio website
            html_content = await scrape_portfolio_url(url)
            
            # Extract structured content
            portfolio_data = self.content_extractor.extract_portfolio_data(html_content, url)
            
            return portfolio_data
            
        except (PortfolioURLError, PortfolioScrapingError, PortfolioContentError):
            raise
        except Exception as e:
            raise PortfolioAnalysisError(f"Unexpected error during portfolio analysis: {str(e)}", url)

# Global analyzer instance
_analyzer_instance: Optional[PortfolioAnalyzer] = None

def get_analyzer() -> PortfolioAnalyzer:
    """Get or create global analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = PortfolioAnalyzer()
    return _analyzer_instance

async def analyze_portfolio_url(url: str) -> str:
    """
    Convenience function to analyze a portfolio URL and return formatted content
    
    Args:
        url: Portfolio website URL
        
    Returns:
        str: Formatted portfolio content suitable for LLM consumption
    """
    if not url or not url.strip():
        return "No portfolio information available."
    
    try:
        analyzer = get_analyzer()
        portfolio_data = await analyzer.analyze_url(url.strip())
        
        if not portfolio_data.has_content():
            return "Portfolio website was found but no meaningful content could be extracted."
        
        return portfolio_data.to_formatted_string()
        
    except PortfolioURLError as e:
        return f"Portfolio URL error: {e.message}"
    except PortfolioScrapingError as e:
        return f"Portfolio scraping failed: {e.message}"
    except PortfolioContentError as e:
        return f"Portfolio content extraction failed: {e.message}"
    except PortfolioAnalysisError as e:
        return f"Portfolio analysis failed: {e.message}"
    except Exception as e:
        return f"Unexpected portfolio analysis error: {str(e)}"

async def analyze_portfolio_url_detailed(url: str) -> PortfolioData:
    """
    Analyze a portfolio URL and return detailed PortfolioData object
    
    Args:
        url: Portfolio website URL
        
    Returns:
        PortfolioData: Detailed portfolio information object
        
    Raises:
        PortfolioAnalysisError: If analysis fails
    """
    analyzer = get_analyzer()
    return await analyzer.analyze_url(url) 