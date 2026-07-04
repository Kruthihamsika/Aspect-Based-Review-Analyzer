from __future__ import annotations

from typing import Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.aspect_sentiment import AspectSentiment
from app.models.detected_aspect import DetectedAspect
from app.models.review import Review
from app.models.uploaded_file import UploadedFile
from app.nlp.sentiment_analyzer import analyze_sentiment


class SentimentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def analyze_for_upload(self, upload_id: str) -> dict[str, Any]:

        # Convert string UUID to UUID object
        try:
            upload_uuid = uuid.UUID(upload_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid upload_id format.",
            )

        uploaded_file = (
            self.db.query(UploadedFile)
            .filter(UploadedFile.id == upload_uuid)
            .first()
        )

        if not uploaded_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Upload not found.",
            )

        aspects = (
            self.db.query(DetectedAspect)
            .join(Review, Review.id == DetectedAspect.review_id)
            .filter(Review.uploaded_file_id == uploaded_file.id)
            .all()
        )

        if not aspects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No detected aspects found for the provided upload.",
            )

        processed_aspects = 0
        positive = 0
        negative = 0
        neutral = 0

        for detected_aspect in aspects:

            existing = (
                self.db.query(AspectSentiment)
                .filter(
                    AspectSentiment.detected_aspect_id == detected_aspect.id
                )
                .first()
            )

            if existing:
                continue

            review = (
                self.db.query(Review)
                .filter(Review.id == detected_aspect.review_id)
                .first()
            )

            if review is None:
                continue

            sentiment = analyze_sentiment(review.review_text or "")

            if sentiment == "Positive":
                positive += 1
            elif sentiment == "Negative":
                negative += 1
            else:
                neutral += 1

            new_record = AspectSentiment(
                detected_aspect_id=detected_aspect.id,
                sentiment=sentiment,
                confidence_score=0.0,
            )

            self.db.add(new_record)

            processed_aspects += 1

        self.db.commit()

        return {
            "message": "Sentiment analysis completed",
            "upload_id": str(uploaded_file.id),
            "processed_aspects": processed_aspects,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        }