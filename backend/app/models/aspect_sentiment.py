from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.detected_aspect import DetectedAspect
    from app.models.review import Review


class AspectSentiment(BaseModel):
    __tablename__ = "aspect_sentiments"

    detected_aspect_id: Mapped[UUID] = mapped_column(
        ForeignKey("detected_aspects.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    # Additive, migration-safe columns for direct aspect-level sentiment reads.
    # They can be backfilled from detected_aspects before making them non-null.
    review_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    aspect: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    sentiment: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    detected_aspect: Mapped["DetectedAspect"] = relationship(
        back_populates="aspect_sentiments"
    )
    review: Mapped["Review | None"] = relationship()
