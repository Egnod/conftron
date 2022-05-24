from __future__ import annotations

import logging
from pathlib import Path

import typer
from art import art

from conftron.cli.command import Command
from conftron.cli.context import AppContextObject, Context
from conftron.cli.controllers import config, sync
from conftron.cli.utils.echo_shortcuts import get_art_title
from conftron.cli.utils.initialization import create_targets, get_remote_targets, start_initialization
from conftron.cli.utils.synchronizator import get_synchronizator
from conftron.config.configurator import get_configurator
from conftron.config.path import get_config_path
from conftron.logs import get_logger, set_logging_configuration
from conftron.sync.utils.providers import get_provider_by_name

__all__ = ("app",)

app = typer.Typer(cls=Command)

app.add_typer(config.app, name="config")
app.add_typer(sync.app, name="sync")


def on_close(ctx: Context):
    def wrapper(*args, **kwargs):
        if ctx.obj and ctx.obj.spinner:
            ctx.obj.spinner.stop()
        ctx.close()

    return wrapper


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    config_path: Path = typer.Option(get_config_path(), "--config", "-C"),
    verbose: bool = typer.Option(False, "--verbose-logs", "-v", is_flag=True),
):
    ctx.call_on_close(on_close(ctx))

    first_start = False
    configurator = None
    typer.echo(get_art_title())

    ctx.obj = AppContextObject(
        config_path=config_path,
        logger=get_logger(f"cli.{ctx.invoked_subcommand if ctx.invoked_subcommand else 'default'}"),
    )

    ctx.obj.spinner.start()

    set_logging_configuration(log_level=logging.INFO if verbose else logging.ERROR)

    if config_path.is_file():
        configurator = get_configurator(config_path=str(config_path))

    if configurator is None:
        with ctx.obj.spinner.hidden():
            ask_create = typer.confirm(f"Config not found {art('bear GTFO')}\nCreate new?", default=True)

            if ask_create:
                configurator = start_initialization(config_path)
                first_start = True
    else:
        configurator.set_config_obj(get_provider_by_name(configurator.get("sync.provider")))

    if not configurator or not configurator.obj:
        ctx.obj.spinner.stop()
        raise typer.Exit()

    if first_start:
        with ctx.obj.spinner.hidden():
            synchronizator = get_synchronizator(
                healthcheck=False,
                config=configurator,
                metadata_path=ctx.obj.metadata_path,
            )

            if synchronizator.validate_metadata(action="download"):
                get_remote_targets(ctx.obj.config_path, configurator, synchronizator)
            else:
                ctx.obj.spinner.stop()
                create_targets(ctx.obj.config_path, configurator, synchronizator)
                ctx.obj.spinner.start()

            configurator = get_configurator(config_path=str(ctx.obj.config_path))

    ctx.obj.config = configurator
