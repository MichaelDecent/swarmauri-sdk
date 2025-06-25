from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class AnalysisResult(Base, UUIDMixin, TimestampMixin):
    """Analysis output generated from a run."""

    __tablename__ = "analysis_results"

    task_run_id: Mapped[str] = mapped_column(String, nullable=False)
    details: Mapped[str] = mapped_column(String, nullable=False)
