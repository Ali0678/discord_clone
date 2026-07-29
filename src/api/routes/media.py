from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from src.api.dependencies import get_db, get_current_user
from src.services.storage import process_and_save_upload
from src.models.user import User 

router = APIRouter(tags = ["Media"])

@router.post("/users/me/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_url = await process_and_save_upload(file)

    current_user.avatar_url = file_url
    await db.commit()

    return {"avatar_url": file_irl}