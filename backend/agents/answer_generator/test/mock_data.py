"""Mock data for testing answer generator agent"""


def create_mock_questions_from_generator():
    """Create mock questions data (output from question_generator agent)"""
    return [
        {
            "question": "Describe the benefits and use cases of using AWS Lambda in a backend system, and how it compares to your experience with Django?",
            "answer": "",
            "tags": [
                "Technical",
                "AWS Lambda",
                "Django",
                "Backend",
                "Cloud Computing"
            ]
        },
        {
            "question": "How would you design a scalable and high-performance REST API using Python and Django to handle a large number of concurrent users, considering your experience optimizing database query performance?",
            "answer": "",
            "tags": [
                "Technical",
                "API Design",
                "Scalability",
                "Python",
                "Django"
            ]
        },
        {
            "question": "Tell me about a time you had a conflict with a coworker or manager and how you approached it, especially regarding a technical decision.",
            "answer": "",
            "tags": [
                "Behavioral",
                "Conflict Resolution",
                "Teamwork",
                "Communication",
                "Problem Solving"
            ]
        },
        {
            "question": "Describe a situation where you showed leadership while mentoring junior developers, and what impact did it have on their growth?",
            "answer": "",
            "tags": [
                "Behavioral",
                "Leadership",
                "Mentoring",
                "Teamwork",
                "Communication"
            ]
        },
        {
            "question": "Given your experience with Django, how would you approach implementing API rate limiting to protect against abuse or overuse?",
            "answer": "",
            "tags": [
                "Technical",
                "API Design",
                "Security",
                "Django",
                "Rate Limiting"
            ]
        },
        {
            "question": "Describe a complex problem you solved using Python where a standard approach wasn't sufficient. What was your thought process and what alternative solutions did you consider?",
            "answer": "",
            "tags": [
                "Behavioral",
                "Problem Solving",
                "Python",
                "Algorithms",
                "Critical Thinking"
            ]
        }
    ]


def create_mock_personal_summary():
    """Create mock personal summary data (output from summarizer agent)"""
    return {
        "title": "Amazon Backend Engineer (San Francisco)",
        "resumeInfo": "May Yan is a Software Engineer with expertise in backend development and Python. Currently a Backend Engineer at TechX since 2023, she designs and implements RESTful APIs and optimizes database query performance, utilizing Python and the Django framework. Previously, as a Junior Developer at DataCorp from 2021 to 2023, she participated in developing data analysis tools and maintained existing codebase. May holds a Bachelor of Computer Science degree from the University of California, obtained in 2021. Her technical skills include programming languages such as Python, JavaScript, and SQL, frameworks like Django, Flask, and React, and tools such as Git, Docker, and AWS. She is fluent in English and native in Chinese. May has given presentations at university AI club, mentored junior developers, solved complex problems, published technical articles on Medium about Python best practices and database optimization, and is passionate about open source software and contributing to community projects.",
        "linkedinInfo": "No information",
        "githubInfo": "Ziqi (Lydia) Yan is a new media artist, designer, and media studies researcher with a concentration in human-nonhuman relationships from the ecological perspective, and speculative design for critical thinking in bio-tech development. She completed her B.S. in Interactive Media Arts with an honors degree, and double majored in Humanities (media studies track) at New York University Shanghai. Lydia is currently a candidate for Master of Design Studies in Ecologies Domain at Harvard University Graduate School of Design. Lydia is interested in bio designs, visualizing social and cultural phenomena and creating futuristic visions using new media methods. Lydia enjoys knitting and crocheting in her spare time.",
        "portfolioInfo": "No information",
        "additionalInfo": "Gave presentations at university AI club, mentored junior developers. Skilled at solving complex problems. Has published technical articles on Medium about Python best practices and database optimization. Passionate about open source software and contributing to community projects.",
        "jobDescription": "Amazon Backend Engineer (San Francisco)\nResponsibilities include designing scalable REST APIs, optimizing database performance, collaborating with frontend developers.\nRequirements:\n- Proficient in Python\n- Understanding of API design principles\n- Good teamwork abilities\n- At least 2 years of relevant experience"
    }


def create_mock_company_info():
    """Create mock company information for culture alignment"""
    return {
        "culture": "Amazon's culture is built on customer obsession, ownership, invent and simplify, are right a lot, learn and be curious, hire and develop the best, insist on the highest standards, think big, bias for action, frugality, earn trust, dive deep, have backbone; disagree and commit, deliver results.",
        "values": [
            "Customer Obsession",
            "Ownership",
            "Invent and Simplify",
            "Are Right, A Lot",
            "Learn and Be Curious",
            "Hire and Develop the Best",
            "Insist on the Highest Standards",
            "Think Big",
            "Bias for Action",
            "Frugality",
            "Earn Trust",
            "Dive Deep",
            "Have Backbone; Disagree and Commit",
            "Deliver Results"
        ],
        "mission": "To be Earth's Most Customer-Centric Company, where customers can find and discover anything they might want to buy online, and endeavors to offer its customers the lowest possible prices."
    }
