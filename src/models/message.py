import uuid 
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Text, DateTime, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_class import Base 

class Message(Base):
    __tablename__ = "messages"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete = "CASCADE"),
        nullable = False,
    )

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete = "CASCADE"),
        nullable = False,
        index = True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable = False
    )

    attachment_url: Mapped[str | None] = mapped_column(
        String(255),
        nullable = True
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone = True),
        onupdate = lambda: datetime.now(timezone.utc),
        nullable = True
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone = True),
        nullable = True
    )

    channel = relationship("Channel")
    author = relationship("User")
    
    __table_args__ = (
        Index(
            "ix_messages_channel_id_created_at_desc",
            "channel_id",
            text("created_at DESC")
        ),
    )
