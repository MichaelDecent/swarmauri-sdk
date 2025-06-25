from __future__ import annotations

from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class RawBlob(Base, UUIDMixin, TimestampMixin):
    """Unprocessed binary blob associated with a task."""

    __tablename__ = "raw_blobs"

    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
