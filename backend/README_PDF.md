# PDF Processing for Mocker Interview Preparation

A PDF-based workflow starter system for interview preparation.

## Overview

This system allows authenticated users to upload PDF resumes which are processed to extract text and automatically start the interview preparation workflow (summarizer, search, question_generator, answer generator).

## Features

- **PDF Text Extraction**: Uses PyMuPDF for text extraction
- **Firebase Authentication**: Secure user authentication
- **Workflow Integration**: Direct integration with interview preparation workflow
- **Basic Validation**: File size, type, and format validation
- **Simple Text Cleaning**: Basic whitespace normalization
- **Memory Processing**: No file storage, immediate cleanup
- **Error Handling**: Error messages for common issues

## Architecture

```
Auth Token → PDF Upload → Validation → Text Extraction → Workflow Processing → Results
```

## API Endpoints

All endpoints require Firebase authentication token in Authorization header.

### 1. Start Workflow with PDF Resume

```http
POST /workflows/start-with-pdf
Authorization: Bearer <firebase_token>
```

Upload PDF resume and automatically start the complete interview preparation workflow.

**Input**:

- PDF file (required)
- job_description (required)
- linkedin_link (optional)
- github_link (optional)
- portfolio_link (optional)
- additional_info (optional)
- num_questions (optional, default: 50)
- session_id (optional, auto-generated if not provided)

**Output**:

```json
{
  "success": true,
  "session_id": "abc123",
  "workflow_id": "abc123",
  "user_id": "firebase_uid",
  "completed_agents": [
    "resume_summarizer",
    "interview_questions_searcher",
    "question_generator",
    "answer_generator"
  ],
  "processing_time": 75.2
}
```

### 2. Start Workflow with Text Resume

```http
POST /workflows/start-with-text
Authorization: Bearer <firebase_token>
```

Start workflow with pre-extracted resume text.

**Input**:

- resume_text (required)
- job_description (required)
- linkedin_link (optional)
- github_link (optional)
- portfolio_link (optional)
- additional_info (optional)
- num_questions (optional, default: 50)
- session_id (optional, auto-generated if not provided)

**Output**:

```json
{
  "success": true,
  "session_id": "abc123",
  "workflow_id": "abc123",
  "user_id": "firebase_uid",
  "completed_agents": [
    "resume_summarizer",
    "interview_questions_searcher",
    "question_generator",
    "answer_generator"
  ],
  "processing_time": 75.2
}
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install pymupdf fastapi uvicorn python-multipart firebase-admin
```

### 2. Setup Firebase (Required)

Ensure Firebase configuration is available in `backend/tools/firebase_config.py`

### 3. Verify Entry File

Make sure `backend/app.py` exists and is correctly configured.

### 4. Start Server

```bash
# From project root directory
uvicorn backend.app:app --reload --port 8001
```

### 5. Access API Documentation

Open browser: `http://localhost:8001/docs`

## Testing Guide

### Method 1: Swagger UI with Authentication

1. Start server: `uvicorn backend.app:app --reload --port 8001`
2. Open: `http://localhost:8001/docs`
3. Authenticate: Click 🔒 icon → Enter Firebase token → Authorize
4. Find "POST /workflows/start-with-pdf"
5. Click "Try it out"
6. Upload PDF and fill form fields:

   ```
   job_description:
        Full-stack Software Engineer - Google
        
        We are looking for a Full-stack Software Engineer to join our team. You will work on:
        - Building web applications using React, TypeScript, and Django
        - Developing mobile applications using React Native and Flutter
        - Collaborating with senior engineers on complex projects
        
        Requirements:
        - Experience with Python, Java, TypeScript, and React
        - Understanding of data structures and algorithms
        - Interest in distributed systems and cloud computing
        
   num_questions: 50

   delete "string" in session_id field
   ```

7. Click "Execute"

### Method 2: Automated Tests

Run the test suite to verify all functionality:

```bash
# From project root directory
cd backend
python -m pytest tests/test_api.py -v
```

**Test Coverage:**
- PDF workflow success
- Text workflow success  
- File too large error (413)
- Invalid PDF file error (400)
- Text too short error (400)
- Missing required fields (422)

## Expected Response

### Successful Response

```json
{
  "success": true,
  "session_id": "abc123def456",
  "workflow_id": "abc123def456", 
  "user_id": "firebase_user_uid",
  "completed_agents": [
    "resume_summarizer",
    "interview_questions_searcher", 
    "question_generator",
    "answer_generator"
  ],
  "processing_time": 75.2
}
```

### Error Response

```json
{
  "success": false,
  "error": "File size exceeds 10.0MB limit",
  "user_id": "firebase_user_uid",
  "processing_time": 0.1
}
```

## Configuration

Default settings in `backend/config.py`:

- **Max file size**: 10MB
- **Allowed format**: PDF only
- **Min text length**: 30 characters
- **Max pages**: 50 pages
- **Text quality thresholds**: 50 chars, 5 words

## Error Handling

### HTTP Status Codes

- **200**: Success
- **400**: Invalid file type, corrupted PDF, empty text, validation error
- **401**: Authentication failed (invalid/expired token)
- **413**: File too large
- **422**: Validation error (missing required fields)
- **500**: Internal processing error

### Common Errors

1. **"Invalid or expired token"** → Refresh Firebase token
2. **"File size exceeds 10.0MB limit"** → Use smaller PDF
3. **"Only .pdf files are supported"** → Check file extension
4. **"PDF file is empty or contains no text"** → Use text-based PDF
5. **"Resume text is too short"** → Ensure PDF has sufficient content

## File Structure

```
backend/
├── api/
│   └── routes.py              # Main authenticated API endpoints
├── services/pdf/
│   ├── __init__.py           # Package exports
│   ├── pdf_processor.py      # Core PDF processing
│   ├── text_cleaner.py       # Text normalization
│   ├── file_validator.py     # File validation  
│   └── exceptions.py         # Custom exceptions
├── tests/
│   └── test_api.py           # PDF workflow tests
├── config.py                 # Configuration management
└── app.py                    # FastAPI application
```
