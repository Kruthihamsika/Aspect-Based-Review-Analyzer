from sqlalchemy.orm import declarative_base

from app.database.session import engine

Base = declarative_base()


def initialize_database() -> None:
    import app.models.analysis_job  # noqa: F401
    import app.models.aspect_sentiment  # noqa: F401
    import app.models.detected_aspect  # noqa: F401
    import app.models.review  # noqa: F401
    import app.models.uploaded_file  # noqa: F401

    Base.metadata.create_all(bind=engine)
