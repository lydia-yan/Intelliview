"""Test data module providing mock data for development and testing"""

# Create test data
def create_mock_data():
    """Create mock data for testing"""
    mock_data = {
        "resume_text": """
        May Yan 
        Software Engineer | Backend Developer | Python Expert
        
        Work Experience:
        - TechX, Backend Engineer (2023-present)
          * Design and implement RESTful APIs
          * Optimize database query performance
          * Work with Python and Django framework
        
        - DataCorp, Junior Developer (2021-2023)
          * Participate in developing data analysis tools
          * Maintain existing codebase
        
        Education:
        - Bachelor of Computer Science, University of California, 2021
        
        Skills:
        - Programming Languages: Python, JavaScript, SQL
        - Frameworks: Django, Flask, React
        - Tools: Git, Docker, AWS
        - Languages: English (Fluent), Chinese (Native)
        """,
        
        "linkedin_info": "https://www.linkedin.com/in/mayyan/",
        "github_info": "https://github.com/lydia-yan",
        "portfolio_info": "https://jenny-cheng.dev",
        
        "additional_info": """
        Gave presentations at university AI club, mentored junior developers. Skilled at solving complex problems.
        Has published technical articles on Medium about Python best practices and database optimization.
        Passionate about open source software and contributing to community projects.
        """,
        
        "job_description": """
        TechX Backend Engineer (San Francisco)
        Responsibilities include designing scalable REST APIs, optimizing database performance, collaborating with frontend developers.
        Requirements:
        - Proficient in Python
        - Understanding of API design principles
        - Good teamwork abilities
        - At least 2 years of relevant experience
        """
    }
    
    return mock_data 