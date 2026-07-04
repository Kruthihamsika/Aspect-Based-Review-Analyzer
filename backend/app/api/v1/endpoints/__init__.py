from app.api.v1.endpoints.aspect import router as aspect_router
from app.api.v1.endpoints.preprocess import router as preprocess_router
from app.api.v1.endpoints.root import router as root_router
from app.api.v1.endpoints.upload import router as upload_router

router = root_router
router.include_router(upload_router)
router.include_router(preprocess_router)
router.include_router(aspect_router)

__all__ = ["router"]
