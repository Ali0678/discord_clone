import uuid
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from src.db.base_class import Base

class RawBase(DeclarativeBase):
    pass

class Server(Base):
    __tablename__ = "servers"

    name: Mapped[str] = mapped_column(
        String(50),
        nullable = False,
        index = True
    )

    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete = "RESTRICT"),
        nullable = False,
        index = True
    )

    owner = relationship("User", back_populates = "owned_servers")

class ServerMember(RawBase):
    __tablename__ = "server_members"

    server_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("servers.id", ondelete = "CASCADE"),
        primary_key = True
        index = True
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete = "CASCADE"),
        primary_key = False,
        index = True
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone = True),
        default = lambda: datetime.now(timezone.utc),
        nullable = False
    )
