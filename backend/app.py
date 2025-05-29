from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import asyncio
from backend.agents.interviewer.agent import start_agent_session, client_to_agent_messaging, agent_to_client_messaging


app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

manager = ConnectionManager()


@app.get("/")
async def root():
    return {"message": "Mock Interview Agent API is running!"}

# example send back: ws://localhost:8000/ws/s1234?user_id=abc&workflow_id=w001&duration=10&is_audio=true

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    user_id: str = Query(...),
    workflow_id: str = Query(...),
    duration: int = Query(10),
    is_audio: str = Query("true")
):    
    """Client WebSocket endpoint to interact with real-time interview agent."""

    # Wait for client connection
    await manager.connect(websocket)
    print(f"Client #{session_id} connected, audio mode: {is_audio}")

    try: 
        # Start agent session
        live_events, live_request_queue, session = await start_agent_session(session_id, user_id, workflow_id, duration, is_audio == "true")

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


