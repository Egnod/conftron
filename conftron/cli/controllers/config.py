import typer

from conftron.cli.context import Context
from conftron.cli.utils.open_editor import open_editor

__all__ = ("app",)

app = typer.Typer()


@app.command("open")
def open_config(ctx: Context):
    with ctx.obj.spinner.hidden():
        open_editor(ctx.obj.config_path)


@app.command()
def path(ctx: Context):
    with ctx.obj.spinner.hidden():
        typer.echo(f"Path to config file: {ctx.obj.config_path}")
