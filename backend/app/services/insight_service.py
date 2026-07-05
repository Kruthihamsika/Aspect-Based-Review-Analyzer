from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import case, desc, func
from sqlalchemy.orm import Query, Session

from app.models.aspect_sentiment import AspectSentiment
from app.models.detected_aspect import DetectedAspect
from app.models.review import Review


class InsightService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def generate_insights(
        self,
        upload_id: str | UUID | None = None,
        limit: int = 10,
    ) -> dict[str, Any]:
        rows = (
            self._aggregated_aspect_query(upload_id)
            .order_by(desc("mention_count"))
            .limit(limit)
            .all()
        )

        aspect_insights = [self._build_aspect_insight(row) for row in rows]
        recommendations = self._build_recommendations(aspect_insights)

        return {
            "insights": aspect_insights,
            "recommendations": recommendations,
        }

    def _aggregated_aspect_query(
        self,
        upload_id: str | UUID | None = None,
    ) -> Query:
        aspect = self._aspect_label()
        confidence = self._confidence_value()

        query = self.db.query(AspectSentiment).join(
            DetectedAspect,
            AspectSentiment.detected_aspect_id == DetectedAspect.id,
        )

        if upload_id is not None:
            upload_uuid = self._parse_uuid(upload_id)
            query = query.join(Review, Review.id == DetectedAspect.review_id).filter(
                Review.uploaded_file_id == upload_uuid
            )

        return query.with_entities(
            aspect.label("aspect"),
            func.count(AspectSentiment.id).label("mention_count"),
            func.sum(self._sentiment_count("Positive")).label("positive_count"),
            func.sum(self._sentiment_count("Negative")).label("negative_count"),
            func.sum(self._sentiment_count("Neutral")).label("neutral_count"),
            func.avg(confidence).label("average_confidence"),
        ).group_by(aspect)

    def _build_aspect_insight(self, row: Any) -> dict[str, Any]:
        mention_count = int(row.mention_count or 0)
        positive_count = int(row.positive_count or 0)
        negative_count = int(row.negative_count or 0)
        neutral_count = int(row.neutral_count or 0)

        sentiment_percentages = {
            "positive": self._percentage(positive_count, mention_count),
            "negative": self._percentage(negative_count, mention_count),
            "neutral": self._percentage(neutral_count, mention_count),
        }
        dominant_sentiment = max(
            sentiment_percentages,
            key=lambda sentiment: sentiment_percentages[sentiment],
        )

        return {
            "aspect": str(row.aspect),
            "mention_count": mention_count,
            "dominant_sentiment": dominant_sentiment.title(),
            "dominant_percentage": sentiment_percentages[dominant_sentiment],
            "sentiment_distribution": sentiment_percentages,
            "average_confidence": round(float(row.average_confidence or 0.0), 4),
        }

    def _build_recommendations(
        self,
        aspect_insights: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []

        for insight in aspect_insights:
            negative_percentage = float(
                insight["sentiment_distribution"]["negative"]
            )

            if negative_percentage < 50.0:
                continue

            aspect = str(insight["aspect"])
            recommendations.append(
                {
                    "aspect": aspect,
                    "priority": self._priority(negative_percentage),
                    "reason": (
                        f"{negative_percentage:.0f}% of mentions are negative."
                    ),
                    "recommendation": self._recommendation_for_aspect(aspect),
                }
            )

        return recommendations

    def _recommendation_for_aspect(self, aspect: str) -> str:
        normalized = aspect.lower()

        if "camera" in normalized or "photo" in normalized:
            return "Improve camera quality, especially low-light photography."
        if "battery" in normalized or "charge" in normalized:
            return "Improve battery life, charging speed, and power efficiency."
        if "price" in normalized or "cost" in normalized:
            return "Review pricing, discounts, and perceived value."
        if "performance" in normalized or "speed" in normalized:
            return "Optimize performance, responsiveness, and load times."
        if "delivery" in normalized or "shipping" in normalized:
            return "Improve delivery reliability, tracking, and packaging."
        if "support" in normalized or "service" in normalized:
            return "Improve support response quality and resolution time."

        return f"Investigate recurring negative feedback about {aspect}."

    def _aspect_label(self) -> Any:
        return func.coalesce(AspectSentiment.aspect, DetectedAspect.aspect_name)

    def _confidence_value(self) -> Any:
        return func.coalesce(
            AspectSentiment.confidence,
            AspectSentiment.confidence_score,
        )

    def _sentiment_count(self, sentiment: str) -> Any:
        return case(
            (AspectSentiment.sentiment == sentiment, 1),
            else_=0,
        )

    def _percentage(self, count: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return round((count / total) * 100, 2)

    def _priority(self, negative_percentage: float) -> str:
        if negative_percentage >= 75.0:
            return "high"
        if negative_percentage >= 60.0:
            return "medium"
        return "low"

    def _parse_uuid(self, upload_id: str | UUID) -> UUID:
        if isinstance(upload_id, UUID):
            return upload_id
        return UUID(upload_id)
