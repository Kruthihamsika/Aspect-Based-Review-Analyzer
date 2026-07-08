from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Float, case, cast, desc, func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.detected_aspect import DetectedAspect
from app.models.review import Review
from app.models.uploaded_file import UploadedFile


router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

SENTIMENTS = ("Positive", "Neutral", "Negative")


@router.get("/aspects", response_model=dict)
def get_aspect_counts(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "aspects": _aspect_counts(db),
    }


@router.get("/aspects/{upload_id}", response_model=dict)
def get_aspect_counts_for_upload(
    upload_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return {
        "aspects": _aspect_counts(db, upload_id=upload_id),
    }


@router.get("/sentiments", response_model=dict)
def get_sentiment_counts(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "sentiments": _sentiment_counts(db),
    }


@router.get("/sentiments/{upload_id}", response_model=dict)
def get_sentiment_counts_for_upload(
    upload_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return {
        "sentiments": _sentiment_counts(db, upload_id=upload_id),
    }


@router.get("/top-positive", response_model=dict)
def get_top_positive_aspects(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "top_positive_aspects": _top_aspects_by_sentiment_percentage(
            db=db,
            sentiment="Positive",
            limit=10,
        ),
    }


@router.get("/top-positive/{upload_id}", response_model=dict)
def get_top_positive_aspects_for_upload(
    upload_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return {
        "top_positive_aspects": _top_aspects_by_sentiment_percentage(
            db=db,
            sentiment="Positive",
            limit=10,
            upload_id=upload_id,
        ),
    }


@router.get("/top-negative", response_model=dict)
def get_top_negative_aspects(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "top_negative_aspects": _top_aspects_by_sentiment_percentage(
            db=db,
            sentiment="Negative",
            limit=10,
        ),
    }


@router.get("/top-negative/{upload_id}", response_model=dict)
def get_top_negative_aspects_for_upload(
    upload_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return {
        "top_negative_aspects": _top_aspects_by_sentiment_percentage(
            db=db,
            sentiment="Negative",
            limit=10,
            upload_id=upload_id,
        ),
    }


@router.get("/dashboard", response_model=dict)
def get_dashboard(db: Session = Depends(get_db)) -> dict[str, Any]:
    return _dashboard_response(db)


@router.get("/dashboard/{upload_id}", response_model=dict)
def get_dashboard_for_upload(
    upload_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return _dashboard_response(db, upload_id=upload_id)


def _dashboard_response(
    db: Session,
    upload_id: UUID | None = None,
) -> dict[str, Any]:
    sentiments = _sentiment_counts(db, upload_id=upload_id)

    return {
        "summary": {
            "total_reviews": _total_reviews(db, upload_id=upload_id),
            "total_aspects": _total_aspects(db, upload_id=upload_id),
            "positive": sentiments["Positive"],
            "negative": sentiments["Negative"],
            "neutral": sentiments["Neutral"],
        },
        "top_mentioned_aspects": _aspect_counts(db, limit=10, upload_id=upload_id),
        "top_positive_aspects": _top_aspects_by_sentiment_percentage(
            db,
            "Positive",
            5,
            upload_id=upload_id,
        ),
        "top_negative_aspects": _top_aspects_by_sentiment_percentage(
            db,
            "Negative",
            5,
            upload_id=upload_id,
        ),
        "sentiment_distribution": sentiments,
    }

@router.get("/aspect/{aspect_name}", response_model=dict)
def get_aspect_details(
    aspect_name: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return _aspect_details(db, aspect_name)


@router.get("/aspect/{upload_id}/{aspect_name}", response_model=dict)
def get_aspect_details_for_upload(
    upload_id: UUID,
    aspect_name: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return _aspect_details(db, aspect_name, upload_id=upload_id)


def _aspect_details(
    db: Session,
    aspect_name: str,
    upload_id: UUID | None = None,
) -> dict[str, Any]:
    rows = (
        _detected_aspect_query(db, upload_id)
        .filter(func.lower(_aspect_label()) == aspect_name.lower())
        .all()
    )

    if not rows:
        return {
            "message": "Aspect not found."
        }

    total = len(rows)

    positive = sum(1 for r in rows if r.sentiment == "Positive")
    negative = sum(1 for r in rows if r.sentiment == "Negative")
    neutral = sum(1 for r in rows if r.sentiment == "Neutral")

    return {
        "aspect": aspect_name,
        "mentions": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positive_percentage": _percentage(positive, total),
        "negative_percentage": _percentage(negative, total),
        "neutral_percentage": _percentage(neutral, total),
    }

@router.get("/recommendations", response_model=dict)
def get_recommendations(
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return _recommendations_response(db)


@router.get("/recommendations/{upload_id}", response_model=dict)
def get_recommendations_for_upload(
    upload_id: UUID,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    _ensure_upload_exists(db, upload_id)
    return _recommendations_response(db, upload_id=upload_id)


def _recommendations_response(
    db: Session,
    upload_id: UUID | None = None,
) -> dict[str, Any]:
    recommendations = []

    aspects = _aspect_counts(db, upload_id=upload_id)

    for item in aspects:

        aspect = item["aspect"]

        rows = (
            _detected_aspect_query(db, upload_id)
            .filter(func.lower(_aspect_label()) == aspect.lower())
            .all()
        )

        total = len(rows)

        positive = sum(
            1 for r in rows if r.sentiment == "Positive"
        )

        negative = sum(
            1 for r in rows if r.sentiment == "Negative"
        )

        pos_percent = _percentage(positive, total)
        neg_percent = _percentage(negative, total)

        if neg_percent >= 60:

            recommendation = (
                f"Customers are unhappy with {aspect}. "
                f"Consider improving this feature."
            )

        elif pos_percent >= 80:

            recommendation = (
                f"{aspect} is a major strength. "
                f"Highlight it in marketing."
            )

        else:

            recommendation = (
                f"{aspect} receives mixed feedback. "
                f"Monitor future customer reviews."
            )

        recommendations.append({

            "aspect": aspect,

            "mentions": total,

            "positive_percentage": pos_percent,

            "negative_percentage": neg_percent,

            "recommendation": recommendation,
        })

    return {

        "recommendations": recommendations

    }


def _aspect_counts(
    db: Session,
    limit: int | None = None,
    upload_id: UUID | None = None,
) -> list[dict[str, Any]]:
    query = (
        _detected_aspect_query(db, upload_id)
        .with_entities(
            _aspect_label().label("aspect"),
            func.count(DetectedAspect.id).label("count"),
        )
        .group_by(_aspect_label())
        .order_by(desc("count"))
    )

    if limit is not None:
        query = query.limit(limit)

    return [
        {
            "aspect": str(row.aspect),
            "count": int(row.count),
        }
        for row in query.all()
        if row.aspect
    ]


def _sentiment_counts(
    db: Session,
    upload_id: UUID | None = None,
) -> dict[str, int]:
    rows = (
        _detected_aspect_query(db, upload_id)
        .with_entities(
            DetectedAspect.sentiment.label("sentiment"),
            func.count(DetectedAspect.id).label("count"),
        )
        .filter(DetectedAspect.sentiment.isnot(None))
        .group_by(DetectedAspect.sentiment)
        .all()
    )
    counts = {sentiment: 0 for sentiment in SENTIMENTS}

    for row in rows:
        sentiment = _normalize_sentiment(str(row.sentiment))
        if sentiment in counts:
            counts[sentiment] += int(row.count)

    return counts


def _top_aspects_by_sentiment_percentage(
    db: Session,
    sentiment: str,
    limit: int,
    upload_id: UUID | None = None,
) -> list[dict[str, Any]]:
    normalized_sentiment = sentiment.lower()
    sentiment_count = func.sum(
        case(
            (func.lower(DetectedAspect.sentiment) == normalized_sentiment, 1),
            else_=0,
        )
    )
    total_count = func.count(DetectedAspect.id)
    sentiment_percentage = cast(sentiment_count, Float) / cast(total_count, Float)

    rows = (
        _detected_aspect_query(db, upload_id)
        .with_entities(
            _aspect_label().label("aspect"),
            total_count.label("total_count"),
            sentiment_count.label("sentiment_count"),
        )
        .group_by(_aspect_label())
        .having(total_count > 0)
        .order_by(desc(sentiment_percentage), desc(total_count))
        .limit(limit)
        .all()
    )

    return [
        {
            "aspect": str(row.aspect),
            "total_count": int(row.total_count),
            f"{sentiment.lower()}_count": int(row.sentiment_count or 0),
            f"{sentiment.lower()}_percentage": _percentage(
                int(row.sentiment_count or 0),
                int(row.total_count),
            ),
        }
        for row in rows
        if row.aspect
    ]


def _review_count_by_sentiment(db: Session, sentiment: str) -> int:
    return int(
        db.query(func.count(func.distinct(DetectedAspect.review_id)))
        .filter(func.lower(DetectedAspect.sentiment) == sentiment.lower())
        .scalar()
        or 0
    )


def _total_reviews(db: Session, upload_id: UUID | None = None) -> int:
    query = db.query(func.count(Review.id))

    if upload_id is not None:
        query = query.filter(Review.uploaded_file_id == upload_id)

    return int(query.scalar() or 0)


def _total_aspects(db: Session, upload_id: UUID | None = None) -> int:
    query = _detected_aspect_query(db, upload_id).with_entities(
        func.count(DetectedAspect.id)
    )

    return int(query.scalar() or 0)


def _detected_aspect_query(db: Session, upload_id: UUID | None = None):
    query = db.query(DetectedAspect)

    if upload_id is not None:
        query = query.join(Review, Review.id == DetectedAspect.review_id).filter(
            Review.uploaded_file_id == upload_id
        )

    return query


def _ensure_upload_exists(db: Session, upload_id: UUID) -> UploadedFile:
    uploaded_file = db.get(UploadedFile, upload_id)

    if uploaded_file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Uploaded dataset not found.",
        )

    return uploaded_file


def _aspect_label() -> Any:
    return func.coalesce(DetectedAspect.aspect, DetectedAspect.aspect_name)


def _percentage(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 2)


def _normalize_sentiment(sentiment: str) -> str:
    normalized = sentiment.strip().lower()
    if normalized == "positive":
        return "Positive"
    if normalized == "negative":
        return "Negative"
    return "Neutral"
