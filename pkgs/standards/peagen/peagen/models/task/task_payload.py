from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class TaskPayload(Base, UUIDMixin, TimestampMixin):
    """Stored task payload."""

    __tablename__ = "task_payloads"

    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
