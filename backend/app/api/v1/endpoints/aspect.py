from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.aspect_service import AspectService

router = APIRouter(prefix="/extract-aspects", tags=["aspect"])


@router.post("/{upload_id}", status_code=status.HTTP_200_OK)
def extract_aspects_endpoint(
    upload_id: str,
    db: Session = Depends(get_db),
) -> dict:
    try:
        service = AspectService(db)
        return service.extract_for_upload(upload_id)

    except HTTPException:
        raise

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc