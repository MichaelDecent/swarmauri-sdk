from __future__ import annotations


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class Repository(Base, UUIDMixin, TimestampMixin):
    """Git repository tracked by Peagen."""

    __tablename__ = "repositories"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
