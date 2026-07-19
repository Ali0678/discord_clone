from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from uuid import UUID 

class UserCreate(BaseModel):
    """
    Schema for validating user data.
    """
    email: EmailStr
    username: str = Field(..., max_length = 32)
    password: str = Field(..., min_length = 8)

class UserResponse(BaseModel):
    """
    Schema for serializing data back to the client.
    """
    id: UUID
    email: EmailStr
    username: str
    is_active: bool 
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)