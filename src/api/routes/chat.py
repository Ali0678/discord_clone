from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from src.websockets.manager import manager
from src.api.dependencies import get_db
from src.core.config import settings
from src.models.user import user

router = APIRouter(tags=["Chat"])

async def get_ws_current_user(
    websocket: WebSocket,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
) -> User:

    """
    Authenticates a WebSocket connection using a query parameter token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms = [settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            await websocket.close(code = 1008)
            return None
        
        user = await db.get(User, user_id)
        if not user:
            await websocket.close(code = 1008)
            return None
        
        return user
    except JWTError:
        await websocket.close(code = 1008)
        return None
    
@router.websocket("/ws/channels/{channel_id}")
async websocket_endpoint(
    websocket: WebSocket,
    channel_id: str,
    current_user: User = Depends(get_ws_current_user)
):
    if not current_user:
        return
    
    await manager.connect(websocket, channel_id)
    
    await manager.broadcast_to_channel(
        channel_id,
        {"type": "system", "content":"f{current_user.username} joined the chat"}
    )

    try:
        while True:
            data = await websocket.receive_text()
            message_payload = {
                "type": "message",
                "author": current_user.username,
                "content": data
            }

            await manager.broadcast_to_channel(channel_id, message_payload)
        
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)
        await manager.broadcast_to_channel(
            channel_id,
            {"type": "system", "content": f'{current_user.username} left the chat'}
        )

