# Portfolio Analysis Service

A service for analyzing portfolio websites and extracting relevant information for interview preparation workflows.

## Features

- **Web Scraping**: Uses Playwright for reliable browser-based content extraction
- **Content Analysis**: Intelligent extraction of projects, skills, and experience
- **Workflow Integration**: Pre-processes portfolio URLs before workflow execution and provides structured text analysis to agents
- **Error Handling**: Gracefully handles invalid URLs and scraping failures

## Architecture

```
services/portfolio/
├── __init__.py                 # Module exports
├── portfolio_analyzer.py       # Main analysis orchestrator
├── web_scraper.py             # Playwright web scraping
├── content_extractor.py       # HTML content extraction
├── data_models.py             # Portfolio data structures
├── exceptions.py              # Custom exception handling
├── test/
│   └── test_portfolio.py      # Comprehensive test suite
└── README_PORTFOLIO.md        # Documentation
```

## Configuration

Portfolio behavior is configured in `backend/config.py`:

```python
class PortfolioConfig:
    TIMEOUT = 30                    # Page loading timeout (seconds)
    MAX_CONTENT_SIZE = 50000        # Maximum content size (characters)
    MAX_PROJECTS = 20               # Maximum projects to extract
    MAX_SKILLS = 50                 # Maximum skills to extract
    USER_AGENT = "Portfolio-Analyzer/1.0"
```

## Dependencies

Added to `requirements.txt`:

```
playwright==1.42.0              # Browser automation
beautifulsoup4==4.12.3           # HTML parsing
```

**Installation:**
```bash
pip install playwright beautifulsoup4
playwright install chromium      # Install browser dependencies
```

## Usage

### Basic Analysis

```python
from backend.services.portfolio import analyze_portfolio_url

# Analyze a portfolio URL
portfolio_content = await analyze_portfolio_url("https://example-portfolio.com")
print(portfolio_content)
```

### Workflow Integration

The service is automatically integrated into the preparation workflow:

```python
from backend.coordinator.preparation_workflow import run_preparation_workflow

result = await run_preparation_workflow(
    user_id="user123",
    resume_text="Resume content...",
    job_description="Job requirements...",
    portfolio_link="https://portfolio.com",  # Automatically analyzed
    num_questions=25
)
```

## Testing

```bash
cd backend
python services/portfolio/test/test_portfolio.py
```