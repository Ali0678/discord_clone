import uuid
import enum
from sqlalchemy import ForeignKey, String, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_class import Base

class ChannelType(str, enum.Enum):
    TEXT = "text"
    VOICE = "voice"

class Channel(Base):
    __tablename__ = "channels"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable = False
    )

    server_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("servers.id", ondelete = "CASCADE"),
        nullable = False,
        index = True
    )

    type: Mapped[ChannelType] = mapped_column(
        SQLEnum(ChannelType),
        default = ChannelType.TEXT,
        nullable = False
    )

    position: Mapped[int] = mapped_column(
        Integer,
        default = 0,
        nullable = False
    )

    server = relationship("Server", back_populates = "channels")