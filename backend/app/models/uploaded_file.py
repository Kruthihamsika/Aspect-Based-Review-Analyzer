from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.analysis_job import AnalysisJob
    from app.models.review import Review


class UploadedFile(BaseModel):
    __tablename__ = "uploaded_files"

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    upload_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    total_reviews: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

    reviews: Mapped[list["Review"]] = relationship(
        back_populates="uploaded_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analysis_jobs: Mapped[list["AnalysisJob"]] = relationship(
        back_populates="uploaded_file",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
