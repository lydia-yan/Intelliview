# GitHub Analysis Integration

This feature automatically extracts and processes information from users' GitHub profiles URL.

## Features

- **Profile Information**: Extracts name, bio, company information
- **Repository Analysis**: Analyzes repositories by language diversity and recency
- **Technical Stack**: Identifies primary programming languages used
- **README Content**: Extracts and includes relevant project documentation
- **Workflow Integration**: Pre-processes GitHub URL before workflow execution
- **Text-based Input**: Provides structured text analysis to agents, not URLs
- **Error Handling**: Gracefully handles invalid URLs and API failures

## Architecture

```
services/github/
├── __init__.py            # Module exports
├── github_analyzer.py     # Main GitHub analysis business logic
├── api_client.py          # GitHub REST API client
├── data_models.py         # Profile/repository data structures
├── exceptions.py          # Custom exception handling
├── test/
│   └── test_github.py     # Test data provider
└── README_GITHUB.md       # Documentation
```

## Testing

### GitHub Token Setup (Optional)

For higher rate limits (5000/hour vs 60/hour):

1. Log in to your GitHub account and go to:
Settings → Developer settings → Personal access tokens → Tokens (classic)

2. Click "Generate new token (classic)"

3. Select the following scopes:

    - public_repo — to read public repositories

    - read:user — to read user profile information

4. Generate and copy the token.

5. Add to `backend/.env`

```env
GITHUB_TOKEN=ghp_your_token_here
```

### Unit Tests
```bash
cd backend
python -m pytest services/github/test/ -v
```

### Interactive Tests
```bash
cd backend
python services/github/test/test_github.py
```