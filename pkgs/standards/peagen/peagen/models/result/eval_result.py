from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from peagen.models.base import Base, UUIDMixin, TimestampMixin


class EvalResult(Base, UUIDMixin, TimestampMixin):
    """Evaluation result for a task run."""

    __tablename__ = "eval_results"

    task_run_id: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[str] = mapped_column(String, nullable=False)
