"""Application configuration - FastAPI."""
import typing as t

from pydantic_settings import BaseSettings

from src.version import __version__


class Application(BaseSettings):
    """Define application configuration model.

    Constructor will attempt to determine the values of any fields not passed
    as keyword arguments by reading from the environment. Default values will
    still be used if the matching environment variable is not set.

    Environment variables:
        * FASTAPI_DEBUG
        * FASTAPI_PROJECT_NAME
        * FASTAPI_VERSION
        * FASTAPI_DOCS_URL
        * FASTAPI_USE_REDIS

    Attributes:
        DEBUG (bool): FastAPI logging level. You should disable this for
            production.
        PROJECT_NAME (str): FastAPI project name.
        VERSION (str): Application version.
        DOCS_URL (str): Path where swagger ui will be served at.

    """

    DEBUG: bool = True
    PROJECT_NAME: str = "core"
    VERSION: str = __version__
    DOCS_URL: str = "/api/docs"
    POD_NAME: t.Optional[str] = None
    GIT_TAG_NAME: t.Optional[str] = None
    GIT_COMMIT_ID: t.Optional[str] = None
    ENV: str = "dev" if not POD_NAME else "qa" if "-qa-" in POD_NAME else "prod" if "-prod-" in POD_NAME else "dev"
    # All your additional application configuration should go either here or in
    # separate file in this submodule.
    MAX_TRIES: int = 3
    SENTRY_DSN: str = ""
    DB_URI: str = "postgresql+asyncpg://test:test@127.0.0.1:7433/core"
    ECHO_SQL: bool = False

    class Config:
        """Config sub-class needed to customize BaseSettings settings.

        Attributes:
            case_sensitive (bool): When case_sensitive is True, the environment
                variable names must match field names (optionally with a prefix)
            env_prefix (str): The prefix for environment variable.

        Resources:
            https://pydantic-docs.helpmanual.io/usage/settings/

        """

        case_sensitive = True
        env_prefix = "FASTAPI_"


settings = Application()
