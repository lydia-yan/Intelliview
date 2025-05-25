# Interview Questions Search Agent

A Gemini-powered agent that searches for common interview questions and experiences based on job descriptions.

## Overview

This agent:
- Takes job description as input
- Searches the web for relevant interview questions
- Categorizes questions (technical, behavioral, etc.)
- Returns a structured JSON with comprehensive interview preparation data

## Project Structure

```
backend/agents/search/
├── __init__.py       # Package initialization
├── agent.py          # Main agent implementation
├── prompt.py         # Prompt templates for the LLM
├── README.md         # This documentation
└── test/             # Test directory
    ├── interactive_test.py  # Interactive testing script
    ├── mock_data.py         # Test data
    └── test.py              # Automated tests
```

## Setup

### Requirements

- Python 3.9+
- Google Cloud project with Vertex AI API enabled
- Google ADK (Agent Development Kit)

### Installation

1. Install dependencies:
```bash
pip install google-cloud-aiplatform google-adk pytest
```

2. Update project ID in `agent.py`:
   - Replace `project="xxx"` with your own Google cloud project ID

## Usage

```python
from backend.agents.search import search_interview_questions

# Search for interview questions based on job description
result = search_interview_questions(
    job_description="Full job posting content..."
)
```

## Testing（Run from the project root directory）

Run the interactive test to see a formatted output:

```bash
python -m backend.agents.search.test.interactive_test
```

Run the automated test:

```bash
python -m backend.agents.search.test.test
```

Or use pytest:

```bash
pytest backend/agents/search/test/test.py
```

## Output Format

The agent returns a JSON object with these fields:

```json
{
  "jobTitle": "String - The job title extracted from the description",
  "industry": "String - The industry or field identified",
  "experienceLevel": "String - The experience level identified",
  "technicalQuestions": [
    {
      "question": "String - The technical question",
      "frequency": "String - How frequently this question appears (if known)",
      "source": "String - Source of this question (optional)"
    }
  ],
  "behavioralQuestions": [
    {
      "question": "String - The behavioral question",
      "frequency": "String - How frequently this question appears (if known)",
      "source": "String - Source of this question (optional)"
    }
  ],
  "situationalQuestions": [
    {
      "question": "String - The situational question",
      "frequency": "String - How frequently this question appears (if known)",
      "source": "String - Source of this question (optional)"
    }
  ],
  "companySpecificQuestions": [
    {
      "question": "String - The company-specific question",
      "frequency": "String - How frequently this question appears (if known)",
      "company": "String - The company this question is associated with",
      "source": "String - Source of this question (optional)"
    }
  ],
  "interviewProcess": {
    "stages": [
      {
        "stageName": "String - Name of the interview stage",
        "description": "String - Description of what happens in this stage",
        "typicalQuestions": ["String - Typical questions in this stage"]
      }
    ],
    "tips": ["String - Tips for succeeding in these interviews"],
    "commonChallenges": ["String - Common challenges candidates face"]
  },
  "searchQueries": ["String - List of search queries used to find this information"]
}
```