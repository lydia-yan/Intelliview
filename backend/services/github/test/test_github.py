"""
GitHub Analysis Test with Workflow Integration
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
sys.path.insert(0, project_root)

def test_github_functionality():
    """Test core GitHub functionality"""
    print("=== GitHub Functionality Test ===")
    
    try:
        from backend.services.github import GitHubAnalyzer
        
        analyzer = GitHubAnalyzer()
        
        # Test GitHub API connection
        print("1. Testing GitHub API connection...")
        if analyzer.test_github_connection():
            print("   Connection successful")
        else:
            print("   Connection failed")
            return False
        
        # Test GitHub analysis
        print("2. Testing GitHub analysis...")
        test_url = "https://github.com/yoasaaa"
        try:
            summary = analyzer.get_github_summary_for_workflow(test_url)
            if summary and len(summary) > 100:
                print(f"   Analysis successful ({len(summary)} characters)")
                print(f"   Preview: {summary[:200]}...")
                return True
            else:
                print(f"   Analysis failed: {summary}")
                return False
        except Exception as e:
            print(f"   Analysis error: {e}")
            return False
        
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

async def test_workflow_with_github():
    """Test complete workflow with GitHub integration"""
    print("\n=== Workflow Integration Test ===")
    
    try:
        from backend.coordinator.preparation_workflow import run_preparation_workflow
        from backend.services.github import GitHubAnalyzer
        
        # Test GitHub analysis first
        analyzer = GitHubAnalyzer()
        github_url = "https://github.com/yoasaaa"
        github_analysis = analyzer.get_github_summary_for_workflow(github_url)
        
        print(f"GitHub analysis result:\n{github_analysis[:300]}...")
        
        # Mock workflow data
        result = await run_preparation_workflow(
            user_id="test_user_github",
            resume_text="""
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
            job_description="""
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
            github_link=github_url,
            linkedin_link="",
            additional_info="Passionate about software development and Human-Computer Interaction",
            num_questions=10
        )
        
        print(f"\nWorkflow completed!")
        print(f"Success: {result.get('success', False)}")
        print(f"User ID: {result.get('user_id')}")
        print(f"Session ID: {result.get('session_id')}")
        
        if result.get('success'):
            print("Check Firestore database for saved results:")
            print("- Collection: personal_experiences")
            print("- Collection: recommended_qas") 
            return True
        else:
            print(f"Workflow failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_rate_limit():
    """Check GitHub API rate limit status"""
    print("=== Rate Limit Check ===")
    
    try:
        from backend.services.github import GitHubAnalyzer
        import os
        
        # Check if token is loaded
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            print(f"GitHub token loaded: {github_token[:8]}...")
        else:
            print("No GitHub token found in environment")
        
        analyzer = GitHubAnalyzer()
        rate_limit = analyzer.get_rate_limit_info()
        
        if rate_limit:
            core = rate_limit.get('resources', {}).get('core', {})
            limit = core.get('limit', 'Unknown')
            remaining = core.get('remaining', 'Unknown')
            
            print(f"Rate limit: {remaining}/{limit}")
            
            if limit == 5000:
                print("Using authenticated requests (5000/hour)")
            elif limit == 60:
                print("Using unauthenticated requests (60/hour)")
                print("Tip: Set GITHUB_TOKEN in backend/.env for higher limits")
            else:
                print(f"Using authenticated requests ({limit}/hour)")
        else:
            print("Could not get rate limit info")
            
    except Exception as e:
        print(f"Error checking rate limit: {e}")

async def main():
    """Main test function"""
    check_rate_limit()
    print()
    
    # Test basic GitHub functionality
    github_success = test_github_functionality()
    
    if github_success:
        print("\nGitHub functionality tests passed!")
        
        # Test workflow integration
        workflow_success = await test_workflow_with_github()
        
        if workflow_success:
            print("\nAll tests passed! Check database for results.")
        else:
            print("\nWorkflow integration test failed")
    else:
        print("\nGitHub functionality test failed")

if __name__ == "__main__":
    asyncio.run(main()) 