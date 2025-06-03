"""
Web scraping functionality using Playwright for portfolio analysis
"""

import asyncio
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

from backend.config import PortfolioConfig
from .exceptions import PortfolioURLError, PortfolioScrapingError, PortfolioTimeoutError

class PortfolioWebScraper:
    """Web scraper for portfolio websites using Playwright"""
    
    def __init__(self):
        self.config = PortfolioConfig()
        self.browser: Optional[Browser] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self._init_browser()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self._close_browser()
        
    async def _init_browser(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
        except Exception as e:
            raise PortfolioScrapingError("", f"Failed to initialize browser: {str(e)}")
    
    async def _close_browser(self):
        """Close browser and playwright"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    def _validate_url(self, url: str) -> str:
        """
        Validate and normalize URL
        
        Args:
            url: Raw URL string
            
        Returns:
            str: Normalized URL
            
        Raises:
            PortfolioURLError: If URL is invalid
        """
        if not url or not url.strip():
            raise PortfolioURLError(url, "Empty URL provided")
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                raise PortfolioURLError(url, "Invalid URL format")
        except Exception:
            raise PortfolioURLError(url, "Invalid URL format")
        
        return url
    
    async def scrape_portfolio(self, url: str) -> str:
        """
        Scrape portfolio website and return raw HTML content
        
        Args:
            url: Portfolio website URL
            
        Returns:
            str: Raw HTML content of the portfolio
            
        Raises:
            PortfolioURLError: If URL is invalid
            PortfolioTimeoutError: If scraping times out
            PortfolioScrapingError: If scraping fails
        """
        normalized_url = self._validate_url(url)
        
        if not self.browser:
            raise PortfolioScrapingError(url, "Browser not initialized")
        
        page: Optional[Page] = None
        try:
            page = await self.browser.new_page()
            
            # Set user agent
            await page.set_extra_http_headers({
                "User-Agent": self.config.USER_AGENT
            })
            
            # Navigate to portfolio URL with timeout
            try:
                await page.goto(
                    normalized_url,
                    timeout=self.config.TIMEOUT * 1000,
                    wait_until='domcontentloaded'
                )
            except PlaywrightTimeoutError:
                raise PortfolioTimeoutError(url, self.config.TIMEOUT)
            
            # Wait for page to fully load
            await page.wait_for_load_state('networkidle', timeout=5000)
            
            # Get page content
            content = await page.content()
            
            if not content or len(content.strip()) < 100:
                raise PortfolioScrapingError(url, "Portfolio page appears to be empty or too small")
            
            # Limit content size
            if len(content) > self.config.MAX_CONTENT_SIZE:
                content = content[:self.config.MAX_CONTENT_SIZE]
            
            return content
            
        except (PortfolioTimeoutError, PortfolioScrapingError):
            raise
        except Exception as e:
            raise PortfolioScrapingError(url, f"Failed to scrape portfolio: {str(e)}")
        finally:
            if page:
                await page.close()

async def scrape_portfolio_url(url: str) -> str:
    """
    Convenience function to scrape a portfolio URL
    
    Args:
        url: Portfolio website URL
        
    Returns:
        str: Raw HTML content
    """
    async with PortfolioWebScraper() as scraper:
        return await scraper.scrape_portfolio(url) 