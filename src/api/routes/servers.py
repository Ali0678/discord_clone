from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from src.api.dependencies import get_db, get_current_user
from src.schemas.server import ServerCreate, ServerResponse
from src.models.server import Server, ServerMember
from src.models.user import User

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
