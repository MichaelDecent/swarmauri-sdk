from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative class for all models."""


class UUIDMixin:
    """Mixin providing a UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class TimestampMixin:
    """Mixin adding creation and modification timestamps."""

    date_created: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True), default=dt.datetime.utcnow
    )
    last_modified: Mapped[dt.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        default=dt.datetime.utcnow,
        onupdate=dt.datetime.utcnow,
    )
