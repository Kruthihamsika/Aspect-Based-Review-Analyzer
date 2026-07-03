from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.aspect_sentiment import AspectSentiment
    from app.models.review import Review


class DetectedAspect(BaseModel):
    __tablename__ = "detected_aspects"

    review_id: Mapped[UUID] = mapped_column(
        ForeignKey("reviews.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    aspect_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    category: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)

    review: Mapped["Review"] = relationship(back_populates="detected_aspects")
    aspect_sentiments: Mapped[list["AspectSentiment"]] = relationship(
        back_populates="detected_aspect",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
