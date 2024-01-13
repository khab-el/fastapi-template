"""Command-line interface - serve command."""
from typing import Any, Dict

import click
import uvicorn

from src.config import settings
from src.config.logger import log_config

cmd_short_help = "Run development server."
cmd_help = """\
Run development uvicorn (ASGI) server.
"""


@click.command(
    help=cmd_help,
    short_help=cmd_short_help,
)
@click.pass_context
def run(ctx: click.Context, **options: Dict[str, Any]) -> None:
    """Define command-line interface run command.

    Args:
        ctx (click.Context): Click Context class object instance.
        options (typing.Dict[str, typing.Any]): Map of command option names to
            their parsed values.

    """
    overrides = {}

    for key, value in options.items():
        source = ctx.get_parameter_source(key)
        if source and source.name == "COMMANDLINE":
            overrides[key] = value

    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        access_log=True,
        log_level=settings.DEBUG,
        log_config=log_config,
        reload=True,
    )
