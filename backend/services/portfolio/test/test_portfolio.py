"""
Comprehensive tests for portfolio analysis service using mock data
"""

import sys
import os
# Add the project root to Python path for direct execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

# Import the classes we're testing
from backend.services.portfolio.portfolio_analyzer import PortfolioAnalyzer, analyze_portfolio_url, analyze_portfolio_url_detailed
from backend.services.portfolio.web_scraper import PortfolioWebScraper
from backend.services.portfolio.content_extractor import PortfolioContentExtractor
from backend.services.portfolio.data_models import PortfolioData, ProjectInfo
from backend.services.portfolio.exceptions import (
    PortfolioURLError, 
    PortfolioScrapingError, 
    PortfolioTimeoutError,
    PortfolioContentError
)

# Mock data from the coordinator test
MOCK_PORTFOLIO_URL = "https://lydia-yan.github.io/"

MOCK_DATA = {
    "user_id": "test_user_portfolio",
    "resume_text": """
    Yichen Yang - Software Developer
    
    Experience:
    - Frontend Developer Intern at Tech Company (3 months)
    - Full-stack developer with experience in Python, Java, TypeScript, and React
    
    Education:
    - Master's in Software Engineering, University of California, Irvine
    - Bachelor's in Political Science, Fudan University
    
    Skills:
    - Programming: Python, JavaScript, TypeScript, Java, C
    - Frameworks: React, Vue, Django, Flask
    - Cloud: AWS, Google Cloud Platform
    - Databases: PostgreSQL, MySQL, MongoDB
    """,
    
    "job_description": """
    Full-stack Software Engineer - Google
    
    We are looking for a Full-stack Software Engineer to join our team. You will work on:
    - Building web applications using React, TypeScript, and Django
    - Developing mobile applications using React Native and Flutter
    - Collaborating with senior engineers on complex projects
    
    Requirements:
    - Experience with Python, Java, TypeScript, and React
    - Understanding of data structures and algorithms
    - Interest in distributed systems and cloud computing
    """,
    
    "linkedin_link": "www.linkedin.com/in/yichen-yang-5b32912a8",
    "github_link": "https://github.com/yoasaaa",
    "portfolio_link": MOCK_PORTFOLIO_URL,
    "additional_info": "Passionate about software development and Human-Computer Interaction"
}

# Integration test functions for manual testing
async def test_real_portfolio_analysis():
    """Manual test function for real portfolio analysis"""
    print(f"=== Testing Real Portfolio Analysis ===")
    print(f"URL: {MOCK_PORTFOLIO_URL}")
    
    try:
        # Test basic analysis
        result = await analyze_portfolio_url(MOCK_PORTFOLIO_URL)
        print(f"Result length: {len(result)} characters")
        print("Formatted content:")
        print("-" * 40)
        print(result)
        
        # Test detailed analysis
        portfolio_data = await analyze_portfolio_url_detailed(MOCK_PORTFOLIO_URL)
        print(f"\nDetailed analysis:")
        print(f"Title: {portfolio_data.title}")
        print(f"Projects: {len(portfolio_data.projects)}")
        print(f"Skills: {len(portfolio_data.skills)}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

async def test_full_workflow_integration():
    """Manual test function for full workflow integration"""
    print(f"\n=== Testing Full Workflow Integration ===")
    
    try:
        from backend.coordinator.preparation_workflow import run_preparation_workflow
        
        result = await run_preparation_workflow(
            user_id=MOCK_DATA["user_id"],
            resume_text=MOCK_DATA["resume_text"],
            job_description=MOCK_DATA["job_description"],
            linkedin_link=MOCK_DATA["linkedin_link"],
            github_link=MOCK_DATA["github_link"],
            portfolio_link=MOCK_DATA["portfolio_link"],
            additional_info=MOCK_DATA["additional_info"],
            num_questions=3,
            session_id=""
        )
        
        print(f"Workflow success: {result.get('success', False)}")
        print(f"Session ID: {result.get('session_id', 'N/A')}")
        print(f"Completed agents: {result.get('completed_agents', [])}")
        
        if result.get('success'):
            print("✅ Portfolio analysis successfully integrated with workflow!")
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# Manual test runner
async def run_manual_tests():
    """Run manual integration tests"""
    print("Portfolio Analysis Integration Tests")
    print("=" * 50)
    
    # Test portfolio analysis
    portfolio_success = await test_real_portfolio_analysis()
    
    # Test workflow integration
    workflow_success = await test_full_workflow_integration()
    
    print("\n" + "=" * 50)
    print(f"Portfolio Analysis: {'✅ PASS' if portfolio_success else '❌ FAIL'}")
    print(f"Workflow Integration: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    print("Tests completed!")

if __name__ == "__main__":
    # Run manual tests when executed directly
    asyncio.run(run_manual_tests()) 