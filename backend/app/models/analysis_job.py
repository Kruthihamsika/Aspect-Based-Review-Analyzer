from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.uploaded_file import UploadedFile


class AnalysisJob(BaseModel):
    __tablename__ = "analysis_jobs"

    uploaded_file_id: Mapped[UUID] = mapped_column(
        ForeignKey("uploaded_files.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    uploaded_file: Mapped["UploadedFile"] = relationship(back_populates="analysis_jobs")
