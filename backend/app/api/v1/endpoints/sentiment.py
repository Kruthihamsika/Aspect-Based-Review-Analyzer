from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import traceback

from app.api.deps import get_db
from app.services.sentiment_service import SentimentService

router = APIRouter(
    prefix="/analyze-sentiment",
    tags=["sentiment"],
)


@router.post("/{upload_id}", status_code=status.HTTP_200_OK)
def analyze_sentiment_endpoint(
    upload_id: str,
    db: Session = Depends(get_db),
) -> dict:

    try:
        service = SentimentService(db)
        return service.analyze_for_upload(upload_id)

    except HTTPException:
        raise

    except Exception as exc:
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc