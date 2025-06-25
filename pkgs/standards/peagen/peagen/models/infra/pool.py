from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class Pool(Base, UUIDMixin, TimestampMixin):
    """Worker pool grouping multiple workers."""

    __tablename__ = "pools"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
