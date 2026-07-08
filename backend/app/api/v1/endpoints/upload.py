from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.uploaded_file import UploadedFile
from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(tags=["upload"])


@router.get("/uploads", response_model=list[dict])
def list_uploads(db: Session = Depends(get_db)) -> list[dict]:
    uploads = (
        db.query(UploadedFile)
        .order_by(desc(UploadedFile.upload_time))
        .all()
    )

    return [
        {
            "id": str(upload.id),
            "filename": upload.filename,
            "total_reviews": upload.total_reviews,
            "status": upload.status,
            "created_at": upload.upload_time.isoformat(),
        }
        for upload in uploads
    ]


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadResponse:
    try:
        service = UploadService(db)
        result = service.process_csv(file)

    except HTTPException:
        raise

    except Exception as exc:
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    return UploadResponse(**result)
