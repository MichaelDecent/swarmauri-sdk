from __future__ import annotations

import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey, Text, UniqueConstraint


from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class DeployKey(Base, UUIDMixin, TimestampMixin):
    """SSH deploy key bound to a repository."""

    __tablename__ = "deploy_keys"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("repositories.id"), nullable=False
    )
    key: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("repository_id", "id", name="uq_deploy_key_repo_id"),
    )
