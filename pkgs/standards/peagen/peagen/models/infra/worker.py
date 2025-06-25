from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class Worker(Base, UUIDMixin, TimestampMixin):
    """Execution worker instance."""

    __tablename__ = "workers"

    pool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pools.id"), nullable=False
    )
    host: Mapped[str] = mapped_column(String, nullable=False)
