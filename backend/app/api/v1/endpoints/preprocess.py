from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.preprocess_service import PreprocessService

router = APIRouter(prefix="/preprocess", tags=["preprocess"])


@router.post("/{upload_id}", status_code=status.HTTP_200_OK)
async def preprocess_upload(
    upload_id: str,
    db: Session = Depends(get_db),
) -> dict:
    try:
        service = PreprocessService(db)
        return service.preprocess_upload(upload_id)

    except HTTPException:
        raise

    except Exception as exc:
        import traceback

        # Print the complete error to the terminal
        traceback.print_exc()

        # Return the actual error in Swagger (temporary for debugging)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc