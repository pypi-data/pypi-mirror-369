from __future__ import annotations
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CreatedAt

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created: Mapped[CreatedAt]
    groups: Mapped[list["GroupORM"]] = relationship(
        "GroupORM", secondary="user_group_membership", back_populates="users"
    )
    documents_owned: Mapped[list["DocumentORM"]] = relationship("DocumentORM", back_populates="owner")
    permissions: Mapped[list["DocumentPermissionORM"]] = relationship(
        "DocumentPermissionORM", back_populates="user", cascade="all, delete-orphan"
    )