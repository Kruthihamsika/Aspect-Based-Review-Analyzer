from __future__ import annotations

from typing import Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.detected_aspect import DetectedAspect
from app.models.review import Review
from app.models.uploaded_file import UploadedFile
from app.services.aspect_extractor import extract_aspects


class AspectService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def extract_for_upload(self, upload_id: str) -> dict[str, Any]:
        # Convert string upload_id to UUID
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

        reviews = (
            self.db.query(Review)
            .filter(Review.uploaded_file_id == uploaded_file.id)
            .all()
        )

        if not reviews:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reviews found for the provided upload.",
            )

        processed_reviews = 0
        total_aspects = 0

        for review in reviews:
            # Skip reviews that already have extracted aspects
            existing_aspects = (
                self.db.query(DetectedAspect)
                .filter(DetectedAspect.review_id == review.id)
                .count()
            )

            if existing_aspects > 0:
                continue

            cleaned_text = review.cleaned_text or ""
            aspects = extract_aspects(cleaned_text)

            if not aspects:
                continue

            for aspect_name in aspects:
                detected_aspect = DetectedAspect(
                    review_id=review.id,
                    aspect_name=aspect_name,
                    aspect=aspect_name,
                    category=None,
                )

                self.db.add(detected_aspect)
                total_aspects += 1

            processed_reviews += 1

        self.db.commit()

        return {
            "message": "Aspect extraction completed",
            "upload_id": str(uploaded_file.id),
            "processed_reviews": processed_reviews,
            "total_aspects": total_aspects,
        }
