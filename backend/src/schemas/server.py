from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

class ServerCreate(BaseModel):
    name: str = Field(...,min_length = 2, max_length = 50)

class ServerResponse(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    model_config = ConfigDict(from_attributes=True)