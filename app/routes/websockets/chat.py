from fastapi import HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
from ...oauth2 import verify_access_token
from ...database import SessionLocal
from ... import models


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, ws: WebSocket):
        await ws.accept()
        self.active_connections[username] = ws
    
    async def disconnect(self, username):
        if username in self.active_connections:
            del self.active_connections[username]

    async def send_dm(self, username: str, recipient: str, message: str, ws: WebSocket):
        if recipient in self.active_connections:
            await self.active_connections[recipient].send_json({
                "sender": username,
                "message": message
            })
        else:
            await ws.send_json({
                "system_message":f"{recipient} is not online"
            })

manager = ConnectionManager()
 
credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="unauthorized"
)

router = APIRouter(
    prefix="/ws",
    tags=['ws']
)

@router.websocket("/chat")
async def chat(ws: WebSocket):
    db = SessionLocal()
    try:    
        token = ws.query_params.get("token")
    except:
        ws.close(1008)
    try:
        user_data = verify_access_token(token, credential_exception)
        username = user_data.username
        user_id = user_data.id
        user_role = user_data.role
    except HTTPException:
        ws.close(1008)
    
    await manager.connect(username, ws)

    try:
        while True:
            data: dict = await ws.receive_json()
            message = data.get("message")
            recipient = data.get("recipient")
            recipient_query = db.query(models.Users).where(models.Users.username==recipient).first()
            if recipient_query is None:
                await ws.send_json({
                    "system_message": f"{recipient} does not exist"
                })
            else:
                new_message = models.Messages(
                    sender_id = user_id,
                    recipient_id = recipient_query.id,
                    content = message
                )
                db.add(new_message)
                db.commit()
                await manager.send_dm(username, recipient, message, ws)

    except WebSocketDisconnect:
        await manager.disconnect(username) 

    finally:
        db.close()
