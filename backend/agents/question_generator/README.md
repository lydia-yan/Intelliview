# Question Generator Agent

A Gemini-powered agent that generates personalized interview questions based on candidate background, job requirements, and industry standards.

## Overview

This agent:
- Takes candidate background and job requirements as input
- Combines industry FAQs and general behavioral questions from database
- Generates balanced mix of technical, behavioral, situational, and company-specific questions
- Returns structured questions with smart tagging system

## Project Structure

```
backend/agents/question_generator/
├── __init__.py       # Package initialization
├── agent.py          # Main agent implementation
├── prompt.py         # Prompt templates for the LLM
├── README.md         # This documentation
└── test/             # Test directory
    ├── test.py       # Automated tests
    ├── interactive_test.py  # Interactive testing script
    └── mock_data.py  # Test data
```

## Setup

### Requirements

- Python 3.9+
- Google Cloud project with Vertex AI API enabled
- Google ADK (Agent Development Kit)
- Firebase Admin SDK

### Installation

```bash
pip install google-adk google-genai firebase-admin
```

## Usage

```python
from backend.agents.question_generator.agent import generate_custom_questions

# Generate personalized interview questions
questions = generate_custom_questions(
    personal_summary={
        "title": "Job title from job description",
        "resumeInfo": "Comprehensive resume summary",
        "linkedinInfo": "LinkedIn profile information",
        "githubInfo": "GitHub profile and repositories",
        "portfolioInfo": "Portfolio projects information",
        "additionalInfo": "Other relevant details",
        "jobDescription": "Job requirements summary"
    },
    industry_faqs={
        "technicalQuestions": [...],
        "behavioralQuestions": [...]
    },
    num_questions=10
)
```

## Testing

Run the interactive test to see a formatted output:

```bash
python -m backend.agents.question_generator.test.interactive_test
```

Run the automated test:

```bash
python -m backend.agents.question_generator.test.test
```

Or use pytest:

```bash
pytest backend/agents/question_generator/test/test.py
```

## Output Format

The agent returns a JSON array with structured questions:

```json
[
  {
    "question": "How would you design a scalable API system for high-traffic applications?",
    "answer": "",
    "tags": ["Technical", "API Design", "Scalability", "System Architecture", "Backend"]
  },
  {
    "question": "Tell me about a time you had to learn a new technology quickly to solve a problem.",
    "answer": "",
    "tags": ["Behavioral", "Learning Agility", "Problem Solving", "Adaptability", "Growth Mindset"]
  }
]
```

## Question Types

- **30-40% Technical**: Role-specific technical skills and knowledge
- **30-40% Behavioral**: Past experiences, problem-solving, teamwork
- **15-20% Situational**: Hypothetical scenarios and decision-making
- **10-15% Company-Specific**: Role understanding and motivation

## Tagging System

- **First tag**: Question type (`Technical`, `Behavioral`, `Situational`, `CompanySpecific`)
- **2-4 additional tags**: Relevant skills, topics, or concepts
- **Maximum 5 tags** per question to avoid over-tagging

## Integration

Question Generator output serves as direct input to Answer Generator:

```
Question Generator → Answer Generator → Database Storage
```