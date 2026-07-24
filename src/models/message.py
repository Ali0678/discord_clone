import uuid 
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, Text, DateTime 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.db.base_class import Base 

class Message(Base):
    __tablename__ = "messages"

    channel_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("channels.id", ondelete = "CASCADE"),
        nullable = False,
        index = True
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

    channel = relationship("Channel")
    author = relationship("User")
