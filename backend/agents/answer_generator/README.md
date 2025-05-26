# Answer Generator Agent

A Gemini-powered agent that generates personalized interview answers based on candidate background and interview questions.

## Overview

This agent:
- Takes interview questions and candidate background as input
- Generates personalized, compelling answers using clear thinking methodology
- Preserves original tags from question generator
- Returns structured answers compatible with database storage

## Project Structure

```
backend/agents/answer_generator/
├── __init__.py                   # Package initialization
├── agent.py                      # Main agent implementation
├── prompt.py                     # Prompt templates for the LLM
├── README.md                     # This documentation
└── test/                         # Test directory
    ├── __init__.py
    ├── test.py                   # Automated tests
    ├── workflow_test.py          # Workflow test (database integration)
    ├── interactive_test.py       # Interactive test 
    └── mock_data.py              # Test data
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

### Basic Usage

```python
from backend.agents.answer_generator.agent import generate_personalized_answers

# Generate personalized answers
answers = generate_personalized_answers(
    questions_data=[
        {
            "question": "How would you design a scalable API system?",
            "answer": "",
            "tags": ["Technical", "API Design", "Scalability"]
        }
    ],
    personal_summary={
        "title": "Job title from job description",
        "resumeInfo": "Comprehensive resume summary",
        "linkedinInfo": "LinkedIn profile information",
        "githubInfo": "GitHub profile and repositories",
        "portfolioInfo": "Portfolio projects information",
        "additionalInfo": "Other relevant details",
        "jobDescription": "Job requirements summary"
    }
)
```

### Database Integration

```python
from backend.agents.answer_generator.agent import generate_and_save_personalized_answers

# Generate answers and save to database
result = generate_and_save_personalized_answers(
    questions_data=questions_data,
    personal_summary=personal_summary,
    user_id="user_123",
    workflow_id="workflow_123"
)
```

## Testing

### Interactive Test (console output for development)
```bash
python -m backend.agents.answer_generator.test.interactive_test
```

### Unit Tests (for CI/CD)
```bash
python -m backend.agents.answer_generator.test.test
# or with pytest
pytest backend/agents/answer_generator/test/test.py -v
```

### Workflow Test (database integration)
```bash
python -m backend.agents.answer_generator.test.workflow_test
```

After running the test, you can verify the result in Firebase:
User ID: test_user_001
Workflow ID: test_workflow_001
The generated questions and answers will be saved under:
users/test_user_001/workflows/test_workflow_001/recommendedQAs

## Output Format

The agent returns a JSON array with personalized answers:

```json
[
  {
    "question": "Describe the benefits and use cases of using AWS Lambda in a backend system, and how it compares to your experience with Django?",
    "answer": "AWS Lambda offers several benefits: it's serverless, enabling automatic scaling and reduced operational overhead, and it's cost-effective as you only pay for execution time. Common use cases include event-driven tasks like image processing, real-time data streaming, and simple API endpoints. In contrast, Django provides a full-featured framework for building complex web applications with an ORM, templating engine, and more. While at TechX, I've primarily used Django for building our core APIs. However, I see Lambda as ideal for offloading specific, computationally intensive tasks that don't require the full Django stack, such as generating reports. Integrating Lambda with Django via API calls could improve performance and reduce server load on the main application.",
    "tags": [
      "Technical",
      "AWS Lambda",
      "Django",
      "Backend",
      "Cloud Computing"
    ]
  },
  {
    "question": "Describe a complex problem you solved using Python where a standard approach wasn't sufficient. What was your thought process and what alternative solutions did you consider?",
    "answer": "At TechX, we encountered a performance bottleneck when processing large financial datasets for risk analysis. The standard Pandas approach was too slow due to memory limitations. I considered using Dask for parallel processing, but the overhead of distributing the data across multiple cores proved inefficient for our dataset size. Instead, I implemented a custom solution using Python generators and memory mapping. This allowed us to process the data in chunks, minimizing memory usage while still leveraging vectorized operations for performance. I also optimized the data loading process by using binary file formats and reducing data type sizes. This custom approach resulted in a 5x performance improvement compared to the initial Pandas implementation, enabling us to process the data within the required timeframe.",
    "tags": [
      "Behavioral",
      "Problem Solving",
      "Python",
      "Algorithms",
      "Critical Thinking"
    ]
  }
]
```

## Integration

Answer Generator receives input from Question Generator and stores results in database:

```
Question Generator → Answer Generator → Database Storage → Frontend Consumption
```