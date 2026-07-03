from fastapi import APIRouter

from app.api.v1.endpoints import router as endpoints_router

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=dict)
async def health_check() -> dict:
    return {"status": "healthy"}


router.include_router(endpoints_router)
