import uuid
import enum
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    String,
    Integer,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_class import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ChannelType(str, enum.Enum):
    SERVER_TEXT = "server_text"
    DIRECT_MESSAGE = "direct_message"
    VOICE = "voice"


dm_participants = Table(
    "dm_participants",
    Base.metadata,
    Column(
        "channel_id",
        String,
        ForeignKey("channels.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        String,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Channel(Base):
    __tablename__ = "channels"

    name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    type: Mapped[ChannelType] = mapped_column(
        SQLEnum(ChannelType),
        default=ChannelType.SERVER_TEXT,
        nullable=False,
    )

    server_id: Mapped[str | None] = mapped_column(
        ForeignKey("servers.id"),
        nullable=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    server = relationship("Server", back_populates="channels")
    messages = relationship(
        "Message",
        back_populates="channel",
        cascade="all, delete-orphan",
    )
    participants = relationship(
        "User",
        secondary=dm_participants,
        back_populates="dm_channels",
        lazy="selectin",
    )