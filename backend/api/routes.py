from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time

# PDF processing imports
from backend.config import PDFConfig
from backend.services.pdf import PDFProcessor
from backend.coordinator.preparation_workflow import run_preparation_workflow
from backend.services.pdf.exceptions import (
    FileTooLargeError,
    InvalidFileTypeError,
    InvalidPDFError,
    EmptyPDFError,
    PDFProcessingError
)

# Firebase auth import
try:
    from backend.tools.firebase_config import auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

router = APIRouter()
bearer = HTTPBearer()

# Initialize PDF processor with configuration
pdf_config = PDFConfig()
pdf_processor = PDFProcessor(pdf_config)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    """Auth verification function (same as route_jenny.py)"""
    if not FIREBASE_AVAILABLE:
        # For development/testing without Firebase
        return {"uid": "test_user_pdf", "email": "testpdf@example.com", "name": "Test User PDF Workflow"}
    
    try:
        decoded_token = auth.verify_id_token(credentials.credentials)
        return {
            "uid": decoded_token["uid"],  
            "email": decoded_token["email"], 
            "name": decoded_token.get("name", ""),
            "picture": decoded_token.get("picture", "")
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# Authenticated workflow APIs
@router.post("/workflows/start-with-pdf")
async def start_workflow_with_pdf(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    linkedin_link: str = Form(""),
    github_link: str = Form(""),
    portfolio_link: str = Form(""),
    additional_info: str = Form(""),
    num_questions: int = Form(50),
    session_id: Optional[str] = Form(None),
    user=Depends(verify_token)
):
    start_time = time.time()
    user_id = user["uid"]
    
    try:
        # Process PDF and extract resume text
        resume_text = await pdf_processor.extract_text_from_upload(file)
        
        if not resume_text or len(resume_text.strip()) < pdf_config.MIN_TEXT_LENGTH:
            raise EmptyPDFError(f"Extracted resume text is too short (less than {pdf_config.MIN_TEXT_LENGTH} characters)")
        
        # Start the preparation workflow
        workflow_result = await run_preparation_workflow(
            user_id=user_id,
            resume_text=resume_text,
            job_description=job_description,
            linkedin_link=linkedin_link,
            github_link=github_link,
            portfolio_link=portfolio_link,
            additional_info=additional_info,
            num_questions=num_questions,
            session_id=session_id
        )
        
        processing_time = time.time() - start_time
        
        # Return workflow results
        if workflow_result.get("success", False):
            return {
                "success": True,
                "session_id": workflow_result.get("session_id"),
                "workflow_id": workflow_result.get("workflow_id"),
                "user_id": user_id,
                "completed_agents": workflow_result.get("completed_agents", []),
                "processing_time": processing_time
            }
        else:
            return {
                "success": False,
                "error": workflow_result.get("error", "Workflow execution failed"),
                "user_id": user_id,
                "processing_time": processing_time
            }
            
    except (FileTooLargeError,) as e:
        raise HTTPException(status_code=413, detail=str(e))
    except (InvalidFileTypeError, InvalidPDFError, EmptyPDFError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@router.post("/workflows/start-with-text")
async def start_workflow_with_text(
    resume_text: str = Form(...),
    job_description: str = Form(...),
    linkedin_link: str = Form(""),
    github_link: str = Form(""),
    portfolio_link: str = Form(""),
    additional_info: str = Form(""),
    num_questions: int = Form(50),
    session_id: Optional[str] = Form(None),
    user=Depends(verify_token)
):
    start_time = time.time()
    user_id = user["uid"]
    
    try:
        # Validate resume text
        if not resume_text or len(resume_text.strip()) < pdf_config.MIN_TEXT_LENGTH:
            raise HTTPException(status_code=400, detail=f"Resume text is too short (less than {pdf_config.MIN_TEXT_LENGTH} characters)")        
        
        # Start the preparation workflow
        workflow_result = await run_preparation_workflow(
            user_id=user_id,
            resume_text=resume_text,
            job_description=job_description,
            linkedin_link=linkedin_link,
            github_link=github_link,
            portfolio_link=portfolio_link,
            additional_info=additional_info,
            num_questions=num_questions,
            session_id=session_id
        )
        
        processing_time = time.time() - start_time
        
        # Return workflow results
        if workflow_result.get("success", False):
            return {
                "success": True,
                "session_id": workflow_result.get("session_id"),
                "workflow_id": workflow_result.get("workflow_id"),
                "user_id": user_id,
                "completed_agents": workflow_result.get("completed_agents", []),
                "processing_time": processing_time
            }
        else:
            return {
                "success": False,
                "error": workflow_result.get("error", "Workflow execution failed"),
                "user_id": user_id,
                "processing_time": processing_time
            }
            
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")