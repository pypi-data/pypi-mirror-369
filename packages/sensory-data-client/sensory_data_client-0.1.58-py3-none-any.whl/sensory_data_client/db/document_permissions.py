# sensory_data_client/db/document_permissions.py
from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey, Integer, UniqueConstraint
from typing import List, Optional

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sensory_data_client.db.base import Base

class DocumentPermissionORM(Base):
    __tablename__ = "document_permissions"
    __table_args__ = (UniqueConstraint("doc_id", "user_id", "permission_level", name="uq_document_permissions"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    doc_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission_level: Mapped[int] = mapped_column(Integer, nullable=False)

    document: Mapped["DocumentORM"] = relationship("DocumentORM", back_populates="permissions")
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="permissions")