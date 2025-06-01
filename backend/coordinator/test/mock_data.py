"""Test data module providing mock data for development and testing"""

# Create test data for workflow testing
def create_mock_workflow_data():
    """Create mock data for workflow testing"""
    mock_data = {
        "user_id": "yichen@example.com",
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
        "portfolio_link": "",
        "additional_info": "Passionate about software development and Human-Computer Interaction"
    }
    
    return mock_data