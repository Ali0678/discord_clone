from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean
from src.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255),
        unique = True,
        nullable = False,
        index = True
    )

    username: Mapped[str] = mapped_column(
        String(32),
        unique = True,
        nullable = False,
        index = True
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable = False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean(),
        default = True,
        nullable = False
    )

    owned_servers = relationship("Server", back_populates = "owner")
