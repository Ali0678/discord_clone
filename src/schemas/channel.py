from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from src.models.channel import ChannelType

class ChannelCreate(BaseModel):
    name: str = Field(..., min_length = 1, max_length = 50)
    type: ChannelType = ChannelType.TEXT

class ChannelResponse(BaseModel):
    id: UUID
    name: str
    type: ChannelType
    server_id: UUID
    position: int

    model_config = ConfigDict(from_attributes = True)