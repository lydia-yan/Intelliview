# Interview Preparation Workflow

The interview preparation workflow using Google's ADK SequentialAgent to generate personalized interview questions and answers based on user background and target job requirements.

## Architecture Overview

### Workflow Components

The system uses ADK `SequentialAgent` to orchestrate four specialized agents:

1. **SummarizerAgent**: Analyzes resume, LinkedIn, GitHub, portfolio, and job description
2. **SearchAgent**: Searches for industry-specific common interview questions  
3. **QuestionGeneratorAgent**: Creates customized interview questions with quantity control
4. **AnswerGeneratorAgent**: Generates personalized answers and saves to database

### Data Flow with Session Management

```
User Input → SequentialAgent → Session State Management:
1. SummarizerAgent → output_key="personal_summary" → session.state
2. SearchAgent → reads {personal_summary} → output_key="industry_faqs" → session.state  
3. QuestionGeneratorAgent → reads {personal_summary} + {industry_faqs} → output_key="questions_data" → session.state
4. AnswerGeneratorAgent → reads {personal_summary} + {questions_data} → output_key="answers_data" → Database
```

### Key Features:
- **State Injection**: Automatic data passing via `{key}` syntax in agent prompts
- **Session Management**: `InMemorySessionService` with auto-generated session IDs
- **Database Integration**: Automatic saving of `PersonalExperience` and `RecommendedQA` objects
    - **PersonalExperience**: Saved by SummarizerAgent with structured resume analysis
    - **RecommendedQA**: Saved by AnswerGeneratorAgent with questions and answers
    - **Session Tracking**: Each workflow identified by unique `session_id` serving as `workflow_id`

## Legacy Agent Impact
With the new ADK SequentialAgent workflow:
- **Individual agent functions** (`summarize_resume()`, `generate_custom_questions()`, etc.) are now **obsolete** for new workflows
- **ADK handles execution automatically** through unified session management
- **Manual JSON parsing** replaced by ADK's automatic `output_key` system
- **State management** simplified - no need for separate session creation per agent
- **Legacy functions preserved** for backward compatibility but not used in SequentialAgent workflow

## Usage

### Basic Workflow Execution

```python
from backend.coordinator.preparation_workflow import run_preparation_workflow

# Execute workflow
result = await run_preparation_workflow(
    user_id="user@example.com",           # Required: from frontend login
    resume_text="Resume content...",      # Required
    job_description="Job description...", # Required
    linkedin_link="https://...",          # Optional
    github_link="https://...",            # Optional  
    portfolio_link="https://...",         # Optional
    additional_info="Additional info...", # Optional
    num_questions=50,                     # Optional: default 50
    session_id=None                       # Optional: auto-generated if None
)

# Check results
if result['success']:
    print(f"Generated {len(json.loads(result['questions_data']))} questions")
    print(f"Session ID: {result['session_id']}")
else:
    print(f"Error: {result['error']}")
```

### Response Format

```python
{
    "success": True,
    "user_id": "user@example.com",
    "session_id": "auto_generated_id",
    "workflow_id": "same_as_session_id",
    "completed_agents": ["agent1", "agent2", "agent3", "agent4"],
    "session_state": {...},               # Full session state
    "personal_summary": "{}",             # JSON string
    "industry_faqs": "{}",                # JSON string  
    "questions_data": "[]",               # JSON string
    "final_answers": "[]"                 # JSON string
}
```

## Testing

```bash
cd backend/coordinator/test
python test_workflow.py
```

## File Structure

```
backend/coordinator/
├── preparation_workflow.py     # Main ADK SequentialAgent orchestrator
├── test/
│   ├── test_workflow.py       # Test execution script
│   └── mock_data.py           # Test data provider
└── README.md                  # This documentation

Modified Agent Files:
backend/agents/*/agent.py       # Updated with ADK SequentialAgent compatibility
backend/agents/*/prompt.py      # Enhanced with quantity control and state injection
```

## Environment Requirements

- Google ADK (AI Development Kit) 1.0.0+
- Google GenAI API access
- Firebase Admin SDK for database operations
- Python 3.8+

Environment setup handled by `backend.config.set_google_cloud_env_vars()`.

## Known Issues

### Large Quantity Generation (50+ Questions)
**Problem**: When generating 50+ questions, the system may encounter:
- JSON output truncation due to LLM response limits
- Malformed JSON causing parsing failures
- Inconsistent question counts (49-51 instead of exact 50)

**Current Status**: 
- 15 questions: Reliable generation and database saving
- 50 questions: Inconsistent results (~70% success rate)

**Proposed Solutions** (for future implementation):
1. **Batch Processing**: Split large requests into smaller chunks (e.g., 4×15)
2. **Model Optimization**: Switch to higher-limit models
3. **Compressed Output**: Reduce JSON verbosity for large responses
4. **Hybrid Strategy**: Combine approaches with retry mechanisms