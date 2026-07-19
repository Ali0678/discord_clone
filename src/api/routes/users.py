from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from src.api.dependencies import get_db
from src.schemas.user import UserCreate, UserResponse
from src.models.user import User 
from src.core.security import get_password_hash 

router = APIRouter(
    prefix = "/users",
    tags=["Users"]
)

@router.post("/register", response_model = UserResponse, status_code = status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)  #Runs get_db function and passes the session into db
):
    """
    Register a new user in the system.
    """
    query = select(User).where((User.email == user_in.email) | (User.username == user_in.username))
    result = await db.execute(query)
    existing_user = result.scalars().first()  #scalars() extracts User(...) from the result

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "A user with this email or username already exists"
        )
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email = user_in.email,
        username = user_in.username,
        password_hash = hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.get("/@me", response_model = UserResponse)
async def get_me(
    curr_user: User = Depends(get_current_user)
):
    return curr_user

