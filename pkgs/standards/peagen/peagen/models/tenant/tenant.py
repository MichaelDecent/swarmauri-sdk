from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class Tenant(Base, UUIDMixin, TimestampMixin):
    """Organization or namespace grouping repositories and users."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
