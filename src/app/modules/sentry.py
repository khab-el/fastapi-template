import logging

import sentry_sdk

from src.config import settings

log = logging.getLogger("api.sentry")


def init_sentry(sentry_dsn: str = settings.SENTRY_DSN):  # pragma: no cover
    """Init sentry."""
    if sentry_dsn is None:
        log.warning("sentry dsn is not set")
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        attach_stacktrace=True,
        environment=settings.ENV,
        release=settings.GIT_TAG_NAME,
    )
    with sentry_sdk.configure_scope() as scope:
        scope.set_tag("commit_id", settings.GIT_COMMIT_ID)
    log.info("sentry initialized @ env=%s", settings.ENV)