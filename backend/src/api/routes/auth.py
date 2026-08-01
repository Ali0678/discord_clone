from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_db
from src.core.security import verify_password, create_access_token
from src.models.user import User
from src.schemas.token import Token

router = APIRouter(tags = ["Authentication"])

@router.post("/auth/login", reponse_model = Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession: Depends(get_db)
):
    query = select(User).where(
        (User.email == form_data.username) | (User.username == form_data.username)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Incorrect username/email or password",
            headers = {"WWW-Authenticate":"Bearer"}
        )

        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Incorrect username/email or password",
                headers = {"WWW-Authenticate":"Bearer"}
            )
        
        access_token = create_access_token(data = {"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}