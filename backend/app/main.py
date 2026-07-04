from fastapi import FastAPI

from app.api.v1.api import router as api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.base import initialize_database

configure_logging()

app = FastAPI(title=settings.app_name)
app.include_router(api_router)


@app.on_event("startup")
def startup_event() -> None:
    initialize_database()
