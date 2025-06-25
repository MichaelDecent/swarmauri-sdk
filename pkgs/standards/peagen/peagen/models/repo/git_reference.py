from __future__ import annotations
import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class GitReference(Base, UUIDMixin, TimestampMixin):
    """Git branch or tag reference."""

    __tablename__ = "git_references"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False
    )
    ref: Mapped[str] = mapped_column(String, nullable=False)
