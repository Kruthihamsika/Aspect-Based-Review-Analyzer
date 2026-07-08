from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.v1.api import router as api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.base import initialize_database

configure_logging()

app = FastAPI(title=settings.app_name)

# -------------------- CORS --------------------

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------

app.include_router(api_router)
app.include_router(analytics_router)


@app.on_event("startup")
def startup_event():
    initialize_database()
