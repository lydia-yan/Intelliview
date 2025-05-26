"""Mock data for testing question generator agent"""


def create_mock_personal_summary():
    """Create mock personal summary data (output from summarizer agent)"""
    return {
        "title": "TechX Backend Engineer (San Francisco)",
        "resumeInfo": "May Yan is a Software Engineer with expertise in backend development and Python. Currently a Backend Engineer at TechX since 2023, she designs and implements RESTful APIs and optimizes database query performance, utilizing Python and the Django framework. Previously, as a Junior Developer at DataCorp from 2021 to 2023, she participated in developing data analysis tools and maintained existing codebase. May holds a Bachelor of Computer Science degree from the University of California, obtained in 2021. Her technical skills include programming languages such as Python, JavaScript, and SQL, frameworks like Django, Flask, and React, and tools such as Git, Docker, and AWS. She is fluent in English and native in Chinese. May has given presentations at university AI club, mentored junior developers, solved complex problems, published technical articles on Medium about Python best practices and database optimization, and is passionate about open source software and contributing to community projects.",
        "linkedinInfo": "No information",
        "githubInfo": "Ziqi (Lydia) Yan is a new media artist, designer, and media studies researcher with a concentration in human-nonhuman relationships from the ecological perspective, and speculative design for critical thinking in bio-tech development. She completed her B.S. in Interactive Media Arts with an honors degree, and double majored in Humanities (media studies track) at New York University Shanghai. Lydia is currently a candidate for Master of Design Studies in Ecologies Domain at Harvard University Graduate School of Design. Lydia is interested in bio designs, visualizing social and cultural phenomena and creating futuristic visions using new media methods. Lydia enjoys knitting and crocheting in her spare time.",
        "portfolioInfo": "No information",
        "additionalInfo": "Gave presentations at university AI club, mentored junior developers. Skilled at solving complex problems. Has published technical articles on Medium about Python best practices and database optimization. Passionate about open source software and contributing to community projects.",
        "jobDescription": "TechX Backend Engineer (San Francisco)\nResponsibilities include designing scalable REST APIs, optimizing database performance, collaborating with frontend developers.\nRequirements:\n- Proficient in Python\n- Understanding of API design principles\n- Good teamwork abilities\n- At least 2 years of relevant experience"
    }


def create_mock_industry_faqs():
    """Create mock industry FAQs data (output from search agent)"""
    return {
        "jobTitle": "Backend Engineer",
        "companyName": "Amazon",
        "industry": "E-commerce and Cloud Computing",
        "experienceLevel": "2+ years",
        "technicalQuestions": [
            {
                "question": "Explain the difference between synchronous and asynchronous programming, and when would you use each in a backend system?",
                "frequency": "commonly asked",
                "source": "ziprecruiter"
            },
            {
                "question": "How would you design a scalable and high-performance backend system to handle a large number of concurrent users?",
                "frequency": "commonly asked",
                "source": "ziprecruiter"
            },
            {
                "question": "What is the role of a load balancer in a backend architecture, and how does it contribute to scalability and fault tolerance?",
                "frequency": "commonly asked",
                "source": "ziprecruiter"
            },
            {
                "question": "Can you describe the benefits and use cases of using AWS Lambda in a backend system?",
                "frequency": "commonly asked",
                "source": "ziprecruiter"
            },
            {
                "question": "Explain the advantages of using a NoSQL database like Amazon DynamoDB over a traditional relational database for certain backend applications.",
                "frequency": "commonly asked",
                "source": "ziprecruiter"
            },
            {
                "question": "How would you design a warehouse system for Amazon.com?",
                "frequency": "frequently in software development engineer and software development manager interviews",
                "source": "IGotAnOffer"
            },
            {
                "question": "How would you design Amazon.com so it can handle 10x more traffic than today?",
                "frequency": "frequently in software development engineer and software development manager interviews",
                "source": "IGotAnOffer"
            },
            {
                "question": "How would you design Amazon.com's database (customers, orders, products, etc.)?",
                "frequency": "frequently in software development engineer and software development manager interviews",
                "source": "IGotAnOffer"
            },
            {
                "question": "Design a URL shortening service.",
                "frequency": "Varying versions of this question came up frequently in the interview reports from Amazon.",
                "source": "IGotAnOffer"
            },
            {
                "question": "How would you design the e-commerce website using microservices? How will you handle transactions?",
                "frequency": "Not found",
                "source": "Webflow"
            },
            {
                "question": "Give an overview of the Amazon technology stack.",
                "frequency": "Not found",
                "source": "foundit.in"
            },
            {
                "question": "Design a task execution service, which accepts tasks from clients and runs them and returns result.",
                "frequency": "Not found",
                "source": "foundit.in"
            },
            {
                "question": "Implementing load balancing to distribute traffic across multiple server instances so no single messaging server becomes a bottleneck.",
                "frequency": "Not found",
                "source": "vertexaisearch.cloud.google.com"
            },
            {
                "question": "Using a distributed database or data store to persist messages and maintain consistency.",
                "frequency": "Not found",
                "source": "vertexaisearch.cloud.google.com"
            },
            {
                "question": "Implementing caching mechanisms to reduce latency and improve performance.",
                "frequency": "Not found",
                "source": "vertexaisearch.cloud.google.com"
            },
            {
                "question": "Ensure high availability and fault tolerance by introducing redundancy and failover.",
                "frequency": "Not found",
                "source": "vertexaisearch.cloud.google.com"
            },
            {
                "question": "How to design an API rate limiter?",
                "frequency": "Not found",
                "source": "Webflow"
            },
            {
                "question": "Choosing an appropriate messaging protocol or framework that can handle a very large number of concurrent users (for example, long polling vs. WebSockets vs.)",
                "frequency": "Not found",
                "source": "vertexaisearch.cloud.google.com"
            }
        ],
        "behavioralQuestions": [
            {
                "question": "Tell me about a time you had a conflict with a coworker or manager and how you approached it.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you disagreed with your team and convinced them to change their position.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you had a conflict with your team but decided to go ahead with their proposal.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time your work was criticized.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you had to change your approach because you were going to miss a deadline.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you had to make a decision with incomplete information. How did you make it and what was the outcome?",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time when you launched a feature with known risks.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you broke a complex problem into simple sub-parts.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me how you deal with ambiguity.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Describe a time you made a mistake.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you applied judgment to a decision when data was not available.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a time you had very little information about a project but still had to move forward.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about a project in which you had to deep dive into analysis.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Tell me about the most complex problem you have worked on.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Describe an instance when you used a lot of data in a short period of time.",
                "frequency": "Not found",
                "source": "IGotAnOffer"
            },
            {
                "question": "Describe a time you had to use outside the box thinking to simplify a task.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time when you didn't know what to do or how to solve a problem.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Describe a situation where you had several options and needed to pick one.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Why do you want to work for Amazon?",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time you dived deep into a problem.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time you could not meet a commitment.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "When you're working on a team, what roles do you gravitate toward and why?",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Describe a time you identified and implemented improvements to your work.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Give examples of what you have accomplished in the past, and relate them to what you can achieve in the future.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about an idea you implemented.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Give an example of a time you went above and beyond a request that was asked of you.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "What is your most challenging project?",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time you improved the moral productivity of your team",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time you missed a deadline",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time when you faced a complex problem when a standard approach was not going to work",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time when you left a company better than you came to it",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Why did you choose a certain language or technology for a particular project",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me about a time when you responded to a critical feedback and what did you learn",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Tell me a time when you face a conflict.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "What is a time you've had a challenge working with others and how did you deal with it?",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "What is a project you are most proud about",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "How do you handle a situation that didn't go as plan",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "Describe a time you were presented with a conflict and how you resolved it.",
                "frequency": "Not found",
                "source": "Reddit"
            },
            {
                "question": "If you're running behind a deadline for a project, how would you proceed?",
                "frequency": "Not found",
                "source": "Reddit"
            }
        ],
        "situationalQuestions": [
            {
                "question": "They give you a real-time problem and ask you \"How had you handled this situation?\"",
                "frequency": "Not found",
                "source": "Quora"
            }
        ],
        "companySpecificQuestions": [
            {
                "question": "What leadership principles do you relate to most?",
                "frequency": "Not found",
                "company": "Amazon",
                "source": "Not found"
            },
            {
                "question": "Give me an example of when you demonstrated [insert leadership principle here]",
                "frequency": "Not found",
                "company": "Amazon",
                "source": "Not found"
            }
        ],
        "interviewProcess": {
            "stages": [
                {
                    "stageName": "Phone Screen",
                    "description": "Initial call with a recruiter to discuss the position and your background.",
                    "typicalQuestions": [
                        "Discussion about your background",
                        "AWS tools that you have experience with"
                    ]
                },
                {
                    "stageName": "Online Assessment",
                    "description": "90 minutes to complete two technical questions, 20 minutes of Systems Design scenarios, and an 8-minute multiple-choice Work Style Survey related to the Leadership Principles.",
                    "typicalQuestions": [
                        "Coding Problems",
                        "System Design Scenarios",
                        "Work Style Survey"
                    ]
                },
                {
                    "stageName": "On-site Interview (4-5 rounds)",
                    "description": "Four to five back-to-back interviews, each lasting 45-55 minutes. Focus on technical competencies (coding, system design) and behavioral questions based on Amazon's Leadership Principles.",
                    "typicalQuestions": [
                        "Coding questions (data structures and algorithms)",
                        "System design questions",
                        "Behavioral questions (Leadership Principles)"
                    ]
                }
            ],
            "tips": [
                "Prepare using the STAR method for behavioral questions.",
                "Practice coding on Livecode.",
                "Familiarize yourself with Amazon's Leadership Principles and be ready to give examples.",
                "Ask clarifying questions and narrow down the problem.",
                "Remember to communicate clearly.",
                "Align your answers with Amazon's Leadership Principles"
            ],
            "commonChallenges": [
                "Difficulty with system design questions.",
                "Not providing specific examples for behavioral questions.",
                "Rushing into coding without fully understanding the problem.",
                "Not checking for edge cases in code.",
                "Effectively communicating design trade-offs"
            ]
        },
        "searchQueries": [
            "Amazon Backend Engineer interview questions San Francisco",
            "Amazon Backend Engineer Python interview questions San Francisco",
            "Amazon Backend Engineer API design interview questions San Francisco",
            "Amazon Backend Engineer system design interview questions",
            "Amazon Backend Engineer behavioral interview questions San Francisco",
            "Amazon Backend Engineer interview experiences San Francisco"
        ]
    }


def create_mock_data():
    """Create complete mock data for testing"""
    return {
        "personal_summary": create_mock_personal_summary(),
        "industry_faqs": create_mock_industry_faqs(),
        "num_questions": 8
    }