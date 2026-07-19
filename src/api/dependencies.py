from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession 
from src.db.database import AsyncSessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAUTH2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from src.core.config import settings
from src.models.user import User

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to yield database sessions.
    Automatically closes the session after the request finishes,
    returning the connection to the pool.
    """

    session = AsyncSessionLocal()

    try:
        yield session
    
    finally:
        await session.close()

oauth2_scheme = OAUTH2PasswordBearer(tokenUrl = "auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        details = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms = [settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except InvalidTokenError:
        raise credentials_exception
    
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    
    return user
        
