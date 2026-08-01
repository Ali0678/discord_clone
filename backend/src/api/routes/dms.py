from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.channel import Channel, ChannelType, dm_participants
from src.models.user import User
from src.api.dependencies import get_db

router = APIRouter()

@router.post("/users/@me/dms")
async def get_or_create_dm(
    target_user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if str(current_user.id) == target_user.id:
        raise HTTPException(status_code = 400, detail = "Cannot DM yourself.")

    target = await db.get(User, target_user_id)
    if not target:
        raise HTTPException(status_code = 404, detail = "User not found")

    stmt = (
        select(Channel)
        .join(dm_participants)
        .where(Channel.type == ChannelType.DIRECT_MESSAGE)
        .where(dm_participants.c.user_id.in_([current_user.id, target_user_id]))
        .group_by(Channel.id)
        .having(func.count(dm_participants.c.user_id) == 2)
    )

    result = await db.execute(stmt)
    existing_dm = result.scalars().first()

    if existing_dm:
        return {"status": "success", "channel_id": existing_dm.id}
    
    new_dm = Channel(
        type = ChannelType.DIRECT_MESSAGE,
        server_id = None,
        name = None
    )
    new_dm.participants.extend([current_user, target])

    db.add(new_dm)
    await db.commit()
    await db.refresh(new_dm)

    return {"status": "success", "channel_id": new_dm.id}

