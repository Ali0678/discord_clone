from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging
from src.api.dependencies import get_db, get_current_user
from src.schemas.server import ServerCreate, ServerResponse
from src.models.server import Server, ServerMember
from src.models.user import User
from src.schemas.channel import ChannelCreate, ChannelResponse
from src.models.channel import Channel
from src.api.dependencies import require_server_owner
from src.websockets.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix = "/servers",
    tags = ["Servers"]
)

@router.post("/", response_model = ServerResponse, status_code = status.HTTP_201_CREATED)
async def create_server(
    server_in: ServerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = depends
):
    """
    Create a new server and automatically add the creator as the first member.
    """
    new_server = Server(
        name = server_in.name
        owner_id = current_user.id 
    )

    db.add(new_server)
    try:
        await db.flush()

        new_member = ServerMember(
            server_id = new_server.id,
            user_id = current_user.id
        )
        db.add(new_member)
        await db.commit()
        await db.refresh(new_server)

        return new_server

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create server: {e}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = "An error occurred while creating the server."
        )

@router.post("/{server_id}/channels", reponse_model = ChannelResponse, status_code = status.HTTP_201_CREATED)
async def create_server_channel(
    channel_in: ChannelCreate,
    server: Server = Depends(require_server_owner),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new channel inside a specific server.
    """

    new_channel = Channel(
        name = channel_in.name,
        type = channel_in.type,
        server_id = server.id
        position = 0
    )

    db.add(new_channel)
    await db.commit()
    await db.refresh(new_channel)

    return new_channel

@router.get("/{server.id}/members/presence")
async def get_server_members_presence(
    server_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches all members of a server and their current online status.
    """

    stmt = (
        select(User)
        .join(ServerMember, User.id == ServerMember.user_id)
        .where(ServerMember.server_id == server_id)
    )

    result = await db.execute(stmt)
    members = result.scalars().all()

    if not members:
        raise HTTPException(status_code = 404, detail = "Server not found or has no members")
    
    hydrated_members = []
    for member in memers:
        member_id_str = str(member.id)
        hydrated_members.append({
            "id": member_id_str,
            "username": member.username,
            "status": "online" if manager.is_user_online(member_id_str) else "offline"
        })
    
    return hydrated_members