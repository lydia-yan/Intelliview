from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException, Body, WebSocket, WebSocketDisconnect, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time
from backend.tools.firebase_config import auth
from backend.data.database import firestore_db
from backend.data.schemas import Profile
from backend.agents.interviewer.agent import start_agent_session, client_to_agent_messaging, agent_to_client_messaging, save_transcript
from backend.tools.connection_manager import manager
from backend.api.schemas import InterviewStartRequest
import asyncio
from datetime import datetime, timezone
from backend.coordinator.preparation_workflow import generate_session_id
from backend.agents.interview_judge.agent import _run_judge_from_session
from backend.coordinator.session_manager import session_service

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

router = APIRouter()
bearer = HTTPBearer()

# Initialize PDF processor with configuration
pdf_config = PDFConfig()
pdf_processor = PDFProcessor(pdf_config)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
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

@router.get("/")
def public_route():
    return {"success": True, "data": None}

# auth route
@router.post("/auth/init")
def init_user_profile(user=Depends(verify_token)):
    existing = firestore_db.get_profile(user["uid"])

    # If new user, or want to update on every login
    if not existing["data"]:
        profile_data = Profile(
            name=user.get("name", ""),
            email=user.get("email", ""),
            photoURL=user.get("picture", "")
        )
        firestore_db.create_or_update_profile(user["uid"], profile_data)

    return {
        "success": True,
        "data": {
            "name": user.get("name", ""), 
            "email": user.get("email", ""), # keep this 
            "photoURL": user.get("picture", ""),
            "isNew": existing["data"] is None
        }
    }

# user route
@router.get("/user")
def get_user_info(user=Depends(verify_token)): 
    profile_result = firestore_db.get_profile(user["uid"])
    return {
        "success": True if profile_result["data"] else False,
        "data": profile_result["data"]
    }


@router.put("/user")
def update_user_info(user=Depends(verify_token), updates: Profile = Body(...)):
    updated = firestore_db.create_or_update_profile(user["uid"], updates)
    return {
        "success": True if updated["data"] else False,
        "data": updated["data"]
    }

# workflows routes
@router.get("/workflows")
def get_all_workflows(user=Depends(verify_token)):
    result = firestore_db.get_workflows_for_user(user["uid"])
    return {
        "success": True if len(result["data"])>0 else False,
        "data": result["data"]
    }

@router.get("/workflows/{workflow_id}/recommended-qa")
def get_recommended_qas(workflow_id: str, user=Depends(verify_token)):
    result = firestore_db.get_recommended_qas(user["uid"], workflow_id)
    return {
        "success": True if result["data"] else False,
        "data": result["data"]
    }

@router.get("/workflows/{workflow_id}/interviews")
def get_all_interviews(workflow_id: str, user=Depends(verify_token)):
    result = firestore_db.get_interviews_for_workflow(user["uid"], workflow_id)
    return {
        "success": True if len(result["data"])>0 else False,
        "data": result["data"]
    }

# websocket
@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    user_id: str = Query(...),
    workflow_id: str = Query(...),
    duration: int = Query(10), #change the default duration here
    is_audio: bool = Query(False)
):    
    """Client WebSocket endpoint to interact with real-time interview agent."""

    # Wait for client connection
    await manager.connect(websocket)
    print(f"Client #{session_id} connected, audio mode: {is_audio}")

    try: 
        # Start agent session
        live_events, live_request_queue, session = await start_agent_session(session_id, user_id, workflow_id, duration, is_audio)

        # Start tasks
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events, session)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, live_request_queue, session)
        )
        await asyncio.gather(agent_to_client_task, client_to_agent_task)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"❌ Client #{session_id} disconnected")
        try:
            # Manually expire session
            session.state["duration"] = int(
                (datetime.now(timezone.utc) - session.state.get("start_time")).total_seconds() / 60
            )

            # Save transcript
            save_transcript(session)
            print(f"[SAVE]: Transcript saved for session {session_id}")

            # Generate feedback
            await _run_judge_from_session(session)
            print(f"[FEEDBACK]: Feedback generated for session {session_id}")

            # FINALIZE: close the session
            try:
                await session_service.delete_session(
                    app_name=session.app_name,
                    user_id=session.user_id,
                    session_id=session.id
                )
                print(f"[CLEANUP]: Session {session.id} successfully closed.")
            except Exception as e:
                print(f"[CLEANUP ERROR]: Failed to close session {session.id}: {e}")
        except Exception as e:
            print(f"[ERROR]: Failed to finalize session after disconnect: {e}")
    except Exception as e:
        print(f"[ERROR] Client #{session_id} error: {e}")
        manager.disconnect(websocket)
        try:
            await websocket.close()
        except Exception:
            pass

@router.post("/interviews/start")
async def start_interview(request: InterviewStartRequest, user=Depends(verify_token)):
    session_id = generate_session_id()

    # You might want to store this session info in the database here

    # Format WebSocket parameters
    websocket_parameter = (
        f"?user_id={user['uid']}&workflow_id={request.workflow_id}"
        f"&duration={request.duration}&is_audio={str(request.is_audio).lower()}"
    )

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "websocket_parameter": websocket_parameter
        }
    }

@router.post("/interviews/{workflow_id}/{session_id}/feedback")
async def generate_feedback(workflow_id: str, session_id: str, user=Depends(verify_token)):
    feedback_result = firestore_db.get_feedback(user["uid"], workflow_id, session_id)

    return {
        "success": feedback_result["data"] is not None,
        "data": feedback_result["data"]
    }

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
        
        # Update user profile with provided social links and additional info
        if linkedin_link or github_link or portfolio_link or additional_info:
            try:
                # Get current profile
                current_profile = firestore_db.get_profile(user_id)
                current_data = current_profile.get("data", {}) or {}
                
                # Create updated profile with new social links
                updated_profile = Profile(
                    name=current_data.get("name", user.get("name", "")),
                    email=current_data.get("email", user.get("email", "")),
                    photoURL=current_data.get("photoURL", user.get("picture", "")),
                    linkedinLink=linkedin_link if linkedin_link else current_data.get("linkedinLink"),
                    githubLink=github_link if github_link else current_data.get("githubLink"),
                    portfolioLink=portfolio_link if portfolio_link else current_data.get("portfolioLink"),
                    additionalInfo=additional_info if additional_info else current_data.get("additionalInfo")
                )
                
                # Update profile in database
                firestore_db.create_or_update_profile(user_id, updated_profile)
                print(f"Updated user profile with social links for user {user_id}")
            except Exception as profile_error:
                print(f"Warning: Failed to update user profile: {profile_error}")
                # Continue with workflow even if profile update fails
        
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
        
        # Update user profile with provided social links and additional info
        if linkedin_link or github_link or portfolio_link or additional_info:
            try:
                # Get current profile
                current_profile = firestore_db.get_profile(user_id)
                current_data = current_profile.get("data", {}) or {}
                
                # Create updated profile with new social links
                updated_profile = Profile(
                    name=current_data.get("name", user.get("name", "")),
                    email=current_data.get("email", user.get("email", "")),
                    photoURL=current_data.get("photoURL", user.get("picture", "")),
                    linkedinLink=linkedin_link if linkedin_link else current_data.get("linkedinLink"),
                    githubLink=github_link if github_link else current_data.get("githubLink"),
                    portfolioLink=portfolio_link if portfolio_link else current_data.get("portfolioLink"),
                    additionalInfo=additional_info if additional_info else current_data.get("additionalInfo")
                )
                
                # Update profile in database
                firestore_db.create_or_update_profile(user_id, updated_profile)
                print(f"Updated user profile with social links for user {user_id}")
            except Exception as profile_error:
                print(f"Warning: Failed to update user profile: {profile_error}")
                # Continue with workflow even if profile update fails
        
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
