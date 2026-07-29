import os 
import uuid 
import aiofiles 
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp"
}

UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok = True)

async def process_and_save_upload(file: UploadFile) -> str:
    """
    Validates and saves an uploaded file securely.
    """
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code = 413, detail = "File exceeds 5MB limit")
    
    if file.content_type not in ALLOWED_MIME_TYPES:
        riase HTTPException(status_code = 415, detail "Unsupported media type: Use JPG, PNG, GIF, or WEBP.")
    
    extension = ALLOWED_MIME_TYPES[file.content_type]
    safe_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024*1024):
                await out_file.write(content)
        except Exception as e:
            raise HTTPException(status_code = 500, detail = "Failed to save file.")
        finally:
            await file.close()

    return f"/media/images/{safe_filename}"