from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import case, desc, func
from sqlalchemy.orm import Query, Session

from app.models.aspect_sentiment import AspectSentiment
from app.models.detected_aspect import DetectedAspect
from app.models.review import Review


class AnalyticsService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_top_positive_aspects(
        self,
        upload_id: str | UUID | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        rows = (
            self._base_aspect_query(upload_id)
            .filter(AspectSentiment.sentiment == "Positive")
            .group_by(self._aspect_label())
            .order_by(desc(func.count(AspectSentiment.id)))
            .limit(limit)
            .all()
        )

        return [
            {
                "aspect": row.aspect,
                "positive_count": int(row.mention_count),
                "average_confidence": round(float(row.average_confidence or 0.0), 4),
            }
            for row in rows
        ]

    def get_top_negative_aspects(
        self,
        upload_id: str | UUID | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        rows = (
            self._base_aspect_query(upload_id)
            .filter(AspectSentiment.sentiment == "Negative")
            .group_by(self._aspect_label())
            .order_by(desc(func.count(AspectSentiment.id)))
            .limit(limit)
            .all()
        )

        return [
            {
                "aspect": row.aspect,
                "negative_count": int(row.mention_count),
                "average_confidence": round(float(row.average_confidence or 0.0), 4),
            }
            for row in rows
        ]

    def get_most_mentioned_aspects(
        self,
        upload_id: str | UUID | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        rows = (
            self._base_aspect_query(upload_id)
            .group_by(self._aspect_label())
            .order_by(desc(func.count(AspectSentiment.id)))
            .limit(limit)
            .all()
        )

        return [
            {
                "aspect": row.aspect,
                "mention_count": int(row.mention_count),
                "average_confidence": round(float(row.average_confidence or 0.0), 4),
            }
            for row in rows
        ]

    def get_average_sentiment_score(
        self,
        upload_id: str | UUID | None = None,
    ) -> dict[str, Any]:
        query = self._sentiment_query(upload_id)
        row = query.with_entities(
            func.count(AspectSentiment.id).label("total_records"),
            func.avg(self._signed_sentiment_score()).label("average_score"),
        ).one()

        return {
            "average_sentiment_score": round(float(row.average_score or 0.0), 4),
            "total_records": int(row.total_records),
            "score_range": {
                "negative": -1,
                "neutral": 0,
                "positive": 1,
            },
        }

    def get_summary(
        self,
        upload_id: str | UUID | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        return {
            "top_positive_aspects": self.get_top_positive_aspects(upload_id, limit),
            "top_negative_aspects": self.get_top_negative_aspects(upload_id, limit),
            "most_mentioned_aspects": self.get_most_mentioned_aspects(upload_id, limit),
            "average_sentiment_score": self.get_average_sentiment_score(upload_id),
        }

    def _base_aspect_query(self, upload_id: str | UUID | None = None) -> Query:
        confidence = self._confidence_value()

        return self._sentiment_query(upload_id).with_entities(
            self._aspect_label().label("aspect"),
            func.count(AspectSentiment.id).label("mention_count"),
            func.avg(confidence).label("average_confidence"),
        )

    def _sentiment_query(self, upload_id: str | UUID | None = None) -> Query:
        query = self.db.query(AspectSentiment).join(
            DetectedAspect,
            AspectSentiment.detected_aspect_id == DetectedAspect.id,
        )

        if upload_id is not None:
            upload_uuid = self._parse_uuid(upload_id)
            query = query.join(Review, Review.id == DetectedAspect.review_id).filter(
                Review.uploaded_file_id == upload_uuid
            )

        return query

    def _aspect_label(self) -> Any:
        return func.coalesce(AspectSentiment.aspect, DetectedAspect.aspect_name)

    def _confidence_value(self) -> Any:
        return func.coalesce(
            AspectSentiment.confidence,
            AspectSentiment.confidence_score,
        )

    def _signed_sentiment_score(self) -> Any:
        confidence = self._confidence_value()
        return case(
            (AspectSentiment.sentiment == "Positive", confidence),
            (AspectSentiment.sentiment == "Negative", -confidence),
            else_=0.0,
        )

    def _parse_uuid(self, upload_id: str | UUID) -> UUID:
        if isinstance(upload_id, UUID):
            return upload_id
        return UUID(upload_id)
