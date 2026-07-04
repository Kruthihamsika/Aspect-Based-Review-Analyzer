from __future__ import annotations

from typing import Any

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.uploaded_file import UploadedFile


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
        self.db.add(uploaded_file)
        self.db.flush()

        review_rows = [
            Review(
                uploaded_file_id=uploaded_file.id,
                source=str(row["source"]),
                review_text=str(row["review_text"]),
                cleaned_text=None,
            )
            for _, row in dataframe.iterrows()
        ]
        self.db.add_all(review_rows)
        self.db.commit()
        self.db.refresh(uploaded_file)

        return {
            "message": "File uploaded successfully",
            "upload_id": str(uploaded_file.id),
            "total_reviews": uploaded_file.total_reviews,
            "status": uploaded_file.status,
        }
