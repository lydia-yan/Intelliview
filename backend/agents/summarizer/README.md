# Resume Summarizer Agent

A Gemini-powered agent that converts resume content into structured JSON format and enriches it with information from LinkedIn, GitHub, and portfolio websites.

## Overview

This agent:
- Takes resume text as input
- Extracts and organizes key information
- Searches linked profiles for additional context
- Returns a structured JSON with comprehensive resume details

## Project Structure

```
backend/agents/summarizer/
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
pip install google-cloud-aiplatform google-adk pytest python-dotenv
```

2. **Configure environment variables:**
   
   Create a `.env` file in the `backend/` directory:
   ```bash
   # backend/.env
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   GOOGLE_GENAI_USE_VERTEXAI=True
   ```
   
   Replace `your-actual-project-id` with your Google Cloud project ID.

3. **Authentication:**
   
   Make sure you're authenticated with Google Cloud:
   ```bash
   gcloud auth application-default login
   ```

## Usage

```python
from backend.agents.summarizer import summarize_resume

result = summarize_resume(
    resume_text="Full resume content...",
    linkedin_info="https://www.linkedin.com/in/username/",
    github_info="https://github.com/username",
    portfolio_info="https://portfolio-website.com",
    additional_info="Any other relevant information",
    job_description="Job posting content"
)
```

## Testing

Run the interactive test to see a formatted output:

```bash
python -m backend.agents.summarizer.test.interactive_test
```

Run the automated test:

```bash
python -m backend.agents.summarizer.test.test
```

Or use pytest:

```bash
pytest backend/agents/summarizer/test/test.py
```

## Output Format

The agent returns a JSON object with these fields:

```json
{
  "title": "Job title from job description",
  "resumeInfo": "Comprehensive resume summary",
  "linkedinInfo": "LinkedIn profile information",
  "githubInfo": "GitHub profile and repositories",
  "portfolioInfo": "Portfolio projects information",
  "additionalInfo": "Other relevant details",
  "jobDescription": "Job requirements summary"
}
``` 