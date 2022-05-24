from pathlib import Path

import typer

from conftron.metadata import name


def get_config_path():
    app_config_path = typer.get_app_dir(name)

    return str(Path(app_config_path) / "config.yaml")
