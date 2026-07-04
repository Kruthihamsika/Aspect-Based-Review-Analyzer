from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.detected_aspect import DetectedAspect
    from app.models.uploaded_file import UploadedFile


class Review(BaseModel):
    __tablename__ = "reviews"

    uploaded_file_id: Mapped[UUID] = mapped_column(
        ForeignKey("uploaded_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    review_text: Mapped[str] = mapped_column(String, nullable=False)
    cleaned_text: Mapped[str | None] = mapped_column(String, nullable=True)

    uploaded_file: Mapped["UploadedFile"] = relationship(back_populates="reviews")
    detected_aspects: Mapped[list["DetectedAspect"]] = relationship(
        back_populates="review",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
