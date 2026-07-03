import logging
from logging.config import dictConfig

from app.core.config import settings


def configure_logging() -> None:
    log_level = "DEBUG" if settings.debug else "INFO"
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": log_level,
            }
        },
        "root": {
            "handlers": ["default"],
            "level": log_level,
        },
    }
    dictConfig(logging_config)


configure_logging()
