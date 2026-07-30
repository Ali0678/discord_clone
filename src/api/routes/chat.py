from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, File, Form, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError
from src.db.session import async_session_maker
from src.models.message import Message
from src.websockets.manager import manager
from src.api.dependencies import get_db
from src.core.config import settings
from src.models.user import user
from src.services.storage import process_and_save_upload

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
    
    await manager.connect(websocket, channel_id, str(current_user.id))
    
    await manager.broadcast_to_channel(
        channel_id,
        {"type": "system", "content":"f{current_user.username} joined the chat"}
    )

    try:
        while True:
            data = await websocket.receive_text()

            async with async_session_maker() as db:
                new_message = Message(
                    channel_id = channel_id,
                    author_id = current_user.id,
                    content = data
                )
                db.add(new_message)
                await db.commit()
                await db.refresh(new_message)

            message_payload = {
                "id": str(new_message.id),
                "type": "message",
                "author": current_user.username,
                "author_id": str(current_user.id),
                "content": new_message.content,
                "timestamp": new_message.created_at.isoformat()
            }

            await manager.broadcast_to_channel(channel_id, message_payload)
        
    except WebSocketDisconnect:
        await manager.disconnect(websocket, channel_id, str(current_user.id))
        await manager.broadcast_to_channel(
            channel_id,
            {"type": "system", "content": f'{current_user.username} left the chat'}
        )

@router.get("/channels/{channel_id}/messages")
async def get_channel_history(
    channel_id: str,
    limit: int = Query(50, le = 100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch the historical messages for a channel
    """
    stmt = (
        select(Message)
        .where(Message.channel_id == channel_id)
        .order_by(Message_created_at.desc())
        .limit(limit)
    )

    result = await db.execute(stmt)
    messages = results.scalars().all()

    return messages[::-1]

@router.post("/channels/{channel_id}/messages")
async def create_message_with_attachment(
    channel_id: str,
    content: str = Form(""),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handles uploading an image and broadcasting it to the channel.
    """
    try:
        attachment_url = await process_and_save_upload(file)
    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code = 500, detail = "Upload failed")
    
    new_message = Message(
        channel_id = channel_id,
        author_id = current_user.id,
        content = content,
        attachment_url = attachment_url
    )
    db.add(new_message)
    await db.commit()
    await db.refresh(new_message)

    message_payload = {
        "id": str(new_message.id),
        "type": "message",
        "author": current_user.username,
        "author_id": str(current_user.id),
        "content": new_message.content,
        "attachment_url": new_message.attachment_url,
        "timestamp": new_message.create_at.isoformat()
    }
    
    await manager.broadcast_to_channel(channel_id, message_payload)
    return {"status": "success", "message": message_payload}
    
