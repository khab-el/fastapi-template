import sys
from logging.config import dictConfig

from src.config import settings

LOG_CONFIG = dict(  # noqa
    version=1,
    disable_existing_loggers=False,
    formatters={
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] [info:%(filename)s:%(funcName)s:%(lineno)s] %(message)s",  # noqa
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        },
    },
    handlers={
        "stdout_default": {
            "class": "logging.StreamHandler",
            "level": settings.DEBUG,
            "formatter": "generic",
            "stream": sys.stdout,
        },
    },
    loggers={
        "": {"level": settings.DEBUG, "handlers": ["stdout_default"]},
        "asyncio": {
            "level": settings.DEBUG,
            "propagate": False,
            "handlers": ["stdout_default"],
        },
        "uvicorn.access": {
            "level": "INFO",
            "propagate": False,
            "handlers": ["stdout_default"],
        },
        "api": {
            "level": "DEBUG",
            "propagate": False,
            "handlers": ["stdout_default"],
        },
    },
)
log_config = dictConfig(LOG_CONFIG)
