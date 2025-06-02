from fastapi import APIRouter, Depends, HTTPException, Body, WebSocket, WebSocketDisconnect, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.tools.firebase_config import auth
from backend.data.database import firestore_db
from backend.data.schemas import Profile
# from backend.agents.interviewer.agent import start_agent_session, client_to_agent_messaging, agent_to_client_messaging
from backend.tools.connection_manager import manager
import asyncio

router = APIRouter()
bearer = HTTPBearer()

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
    if not existing:
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
            "isNew": existing is None
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
    except Exception as e:
        print(f"[ERROR] Client #{session_id} error: {e}")
        manager.disconnect(websocket)
        try:
            await websocket.close()
        except Exception:
            pass