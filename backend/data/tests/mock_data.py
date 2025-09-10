profile_data = {
    "name": "Jenny ABC",
    "email": "jenny.cheng@example.com",
    "photoURL": "https://example.com/photo.jpg",
    "linkedinLink": "https://www.linkedin.com/in/jennycheng",
    "githubLink": "https://github.com/jennycheng",
    "portfolioLink": "https://jennycheng.dev",
    "additionalInfo": "MSWE @ UC Irvine | AI Hackathon Winner | Open Source Contributor"
}

personalExperience = {
    "title": "TechX_Backend Developer",  # company_position name
    "resumeInfo": "Jenny Cheng is a software engineer with 2 years of backend development experience, primarily using Python, Flask, and PostgreSQL. She previously interned at ACompany, where she built API integrations and optimized system performance by 30%.",
    "linkedinInfo": "She has experience in backend development, API design, database management, and has contributed to open-source Python tools. She also participated in a hackathon and led a student developer team at UC Irvine.",
    "githubInfo": "GitHub profile includes contributions to Python-based backend tools and a Chrome extension project using OpenAI API.",
    "portfolioInfo": "Parsed from online portfolio site: Highlights include AI interview platform, visual task planner app, and design docs with Figma mockups.",
    "additionalInfo": "Fluent in English and Mandarin; has presented at university AI clubs and mentored junior developers.",
    "jobDescription": "Backend Developer at TechX (San Francisco, CA). Responsibilities include designing scalable REST APIs, working with cloud infrastructure (AWS), and collaborating with cross-functional teams. Requirements: 2+ years of experience in backend development, Python proficiency, and familiarity with PostgreSQL and CI/CD pipelines."
}

# Fix: Convert from set to list format
recommendedQAs = [
    {
        "question": "Tell me about a time you optimized a system.",
        "answer": "At my last internship, I improved API response time by 30%...",
        "tags": ["optimization", "system design"] 
    },
    {
        "question": "How do you handle tight deadlines?",
        "answer": "I prioritize based on impact and break the tasks into deliverable chunks...",
        "tags": ["time management"]
    }
]

# Fix: Convert from set to list format
transcript = [
    {
      "role": "AI",
      "message": "Tell me about a time you had to learn something quickly."
    },
    {
      "role": "user",
      "message": "When I joined my internship, I had to learn GraphQL within two days...and "
    },
    {
      "role": "AI",
      "message": "Great. How did that affect your work?"
    },
    {
      "role": "user",
      "message": "It helped me build the feature in half the time and reduced backend support."
    }
]

feedback = {
  "positives": [
    "You presented your experience clearly and stayed focused on key responsibilities.",
    "You demonstrated strong alignment with the role's technical requirements, especially in backend system design."
  ],
  "improvementAreas": [
    {
      "topic": "Quantifying Results",
      "example": "In your STAR response, you described your actions well but didn't share the outcome or measurable impact.",
      "suggestion": "Try adding metrics like 'improved API response time by 30%' to emphasize your contribution."
    },
    {
      "topic": "Self-Reflection",
      "example": "When asked about a challenge, you explained the situation but missed reflecting on what you learned.",
      "suggestion": "Use closing lines like 'What I took away from that experience was...' to show growth."
    }
  ],
  "resources": [
    {
      "title": "Improving Behavioral Interview Answers",
      "link": "https://example.com/star-tips"
    },
    {
      "title": "Effective Communication in Interviews",
      "link": "https://example.com/interview-communication"
    }
  ],
  "reflectionPrompt": [
    "What impact did your actions have in the example you shared?",
    "How would you approach the same situation differently today?"
  ],
  "tone": "respectful",
  "overallRating": 4,
  "focusTags": ["clarity", "impact", "self-reflection"]
}

# Fix: Convert from set to list format
generalBQ = [
    {
        "id": "bq001",
        "question": "Tell me about a time you failed and how you handled it.",
        "category": "Failure",
        "tags": ["resilience", "accountability", "growth"]
    },
    {
        "id": "bq002",
        "question": "Describe a situation where you showed leadership.",
        "category": "Leadership",
        "tags": ["initiative", "influence", "decision-making"]
    },
    {
        "id": "bq003",
        "question": "How do you handle tight deadlines?",
        "category": "Time Management",
        "tags": ["prioritization", "pressure", "organization"]
    },
    {
        "id": "bq004",
        "question": "Give me an example of a time you had a conflict at work. What did you do?",
        "category": "Conflict Resolution",
        "tags": []
    }
]

coding_submission = {
    "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i",
    "language": "python",
    "claimed_time": "O(n)",
    "claimed_space": "O(n)",
}

coding_review = {
    "problem_slug": "two-sum",
    "scores": {
        "overall": 82.5,
        "breakdown": {
            "code": {
                "correctness": 95.0,
                "efficiency": 70.0,
                "robustness": 60.0,
                "style": 80.0,
            },
            "conversation": {
                "understanding": 75.0,
                "awareness": 40.0,
                "defense": 65.0,
                "clarity": 80.0,
            },
        },
        "code_score": {
            "correctness": 95.0,
            "efficiency": 70.0,
            "robustness": 60.0,
            "style": 80.0,
            "efficiency_breakdown": {
                "claim_vs_actual": {"time": 80.0, "space": 100.0},
                "actual_vs_optimal": {"time": 70.0, "space": 90.0},
            },
        },
        "conversation_score": {
            "understanding": 75.0,
            "awareness": 40.0,
            "defense": 65.0,
            "clarity": 80.0,
        },
    },
    "feedback": {
        "strength": "🌟 Strongest area: Correctness (95.0).",
        "opportunity": "🎯 Biggest opportunity: Awareness (40.0).",
        "details": [
            "💻 Code feedback: - Time gap vs optimal",
            "🗣️ Conversation feedback: - Missed large input edge case",
        ],
        "next_step": "✅ Next step: Practice explicitly stating edge cases before coding.",
        "code": ["💻 Code feedback: - Time gap vs optimal"],
        "conversation": ["🗣️ Conversation feedback: - Missed large input edge case"],
    },
    "reviewer_result": {
        "compile_status": "ok",
        "tests": [
            {"name": "case1", "input": "[2,7,11,15], target=9", "expected": "[0,1]", "output": "[0,1]", "status": "pass"},
            {"name": "case2", "input": "[3,2,4], target=6", "expected": "[1,2]", "output": "[1,2]", "status": "pass"},
        ],
    },
    "optimal_complexity": {
        "time": "O(n)",
        "space": "O(n)",
        "edge_keywords": ["empty input", "duplicates", "large input"],
    },
    "transcript": [
        {"role": "user", "message": "My solution uses a hash map."},
        {"role": "AI", "message": "Good. What's the time complexity?"},
        {"role": "user", "message": "O(n)."},
    ],
}