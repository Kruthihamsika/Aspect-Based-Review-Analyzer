from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.detected_aspect import DetectedAspect
from app.models.review import Review
from app.models.uploaded_file import UploadedFile

from app.services.sentiment_service import find_aspect_context


class UploadService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def process_csv(self, file: UploadFile) -> dict[str, Any]:
        if not file.filename or not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CSV files are supported.",
            )

        try:
            contents = file.file.read()
        except Exception as exc:  # pragma: no cover - defensive error handling
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to read uploaded file.",
            ) from exc

        if not contents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded CSV file is empty.",
            )

        try:
            dataframe = pd.read_csv(pd.io.common.BytesIO(contents))
        except Exception as exc:  # pragma: no cover - defensive error handling
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to parse CSV file.",
            ) from exc

        if dataframe.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded CSV file is empty.",
            )

        if "review_text" not in dataframe.columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV must contain a 'review_text' column.",
            )

        dataframe = dataframe.copy()
        if "source" not in dataframe.columns:
            dataframe["source"] = "Unknown"
        else:
            dataframe["source"] = dataframe["source"].fillna("Unknown")

        dataframe["review_text"] = dataframe["review_text"].fillna("")
        dataframe["review_text"] = dataframe["review_text"].astype(str)

        uploaded_file = UploadedFile(
            filename=file.filename,
            total_reviews=len(dataframe),
            status="uploaded",
        )

        try:
            self.db.add(uploaded_file)
            self.db.flush()

            for row_number, (_, row) in enumerate(dataframe.iterrows(), start=1):
                review_text = str(row["review_text"])

                review = Review(
                    uploaded_file_id=uploaded_file.id,
                    source=str(row["source"]),
                    review_text=review_text,
                    cleaned_text=None,
                )
                self.db.add(review)
                self.db.flush()

                detected_aspects = self._build_detected_aspects(
                    review=review,
                    review_text=review_text,
                    row_number=row_number,
                )
                self.db.add_all(detected_aspects)

            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(uploaded_file)

        return {
            "message": "File uploaded successfully",
            "upload_id": str(uploaded_file.id),
            "total_reviews": uploaded_file.total_reviews,
            "status": uploaded_file.status,
        }

    def _build_detected_aspects(
        self,
        review: Review,
        review_text: str,
        row_number: int,
    ) -> list[DetectedAspect]:
        try:
            from app.services.aspect_extractor import extract_aspects
            from app.services.sentiment_service import SentimentService

            aspects = extract_aspects(review_text)
            sentiment_service = SentimentService()
        except Exception as exc:  # pragma: no cover - keeps uploads resilient
            print(f"Aspect extraction failed for review {row_number}: {exc}")
            return []

        print(f"Extracted aspects for review {row_number}: {aspects}")

        detected_aspects: list[DetectedAspect] = []
        for aspect in aspects:
            sentiment_result = self._analyze_aspect_sentiment(
                sentiment_service=sentiment_service,
                review_text=review_text,
                aspect=aspect,
                row_number=row_number,
            )

            detected_aspects.append(
                DetectedAspect(
                    review_id=review.id,
                    aspect_name=aspect,
                    aspect=aspect,
                    sentiment=str(sentiment_result["label"]),
                    confidence=float(sentiment_result["score"]),
                    category=None,
                )
            )

        return detected_aspects

    def _analyze_aspect_sentiment(
        self,
        sentiment_service,
        review_text,
        aspect,
        row_number,
    ):
        context = find_aspect_context(review_text, aspect)

        print(f"\nAspect: {aspect}")
        print(f"Context: {context}")

        result = sentiment_service.analyze_text(context)

        print(f"Sentiment Result: {result}\n")

        return result
