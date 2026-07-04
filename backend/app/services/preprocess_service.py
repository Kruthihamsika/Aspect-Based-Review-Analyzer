from __future__ import annotations

from typing import Any
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.uploaded_file import UploadedFile
from app.utils.text_cleaner import clean_text


class PreprocessService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def preprocess_upload(self, upload_id: str) -> dict[str, Any]:
        # Convert string to UUID
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

        for review in reviews:
            review.cleaned_text = clean_text(review.review_text)

        self.db.commit()

        return {
            "message": "Preprocessing completed",
            "upload_id": str(uploaded_file.id),
            "processed_reviews": len(reviews),
        }