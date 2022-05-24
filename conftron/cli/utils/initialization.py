from __future__ import annotations

import enum
from pathlib import Path
from typing import TYPE_CHECKING

import click
import typer
from art import art

from conftron.config.config_manager import ConfigManager
from conftron.config.configurator import Configurator, get_configurator
from conftron.sync.utils.providers import get_default_provider, get_provider_by_name, get_providers_names

if TYPE_CHECKING:
    from conftron.sync.providers.base import BaseSyncProvider


def start_initialization(config_path: Path):
    config_data = {}

    sync_provider_name = typer.prompt(
        "Choose synchronization provider",
        default=get_default_provider().name,
        type=click.Choice(get_providers_names()),
    )
    sync_provider: type[BaseSyncProvider] = get_provider_by_name(sync_provider_name)
    options = {}

    typer.echo("Great! Let's write values for provider's options.")

    for field_info in sync_provider.options_model.get_field_info():
        value = typer.prompt(
            f"Option '{field_info['name']}' for {sync_provider.name} provider",
            type=field_info["type"],
            default=field_info["default"],
        )

        options[field_info["name"]] = value

    config_data["sync"] = {"provider": sync_provider_name, "options": options, "targets": []}

    config_obj = Configurator.validate(config_data, sync_provider)

    ConfigManager.write(config_path=str(config_path), config_data=ConfigManager.prepare_config_data(config_obj))

    configurator = get_configurator(config_path=str(config_path))
    configurator.set_config_obj(sync_provider, config_obj=config_obj)

    typer.echo(f"{art('bear squiting')}Yeaaaah! Your config save to {config_path}")

    return configurator


def create_targets(config_path, configurator, synchronizator):
    typer.echo("Moving on to input sync. targets!")

    end_targets = False

    targets: list[dict] = []

    while not end_targets:
        target = {}

        for field_info in synchronizator.targets_model.get_field_info():
            if isinstance(field_info["type"], enum.EnumMeta):
                field_info["type"] = click.Choice(field_info["type"])

            value = typer.prompt(
                f"Target #{len(targets) + 1} option '{field_info['name']}'",
                type=field_info["type"],
                default=field_info["default"],
            )

            target[field_info["name"]] = str(value)

        targets.append(target)

        end_targets = typer.confirm("Synchronization targets finished?", default=False)

    config_data = ConfigManager.prepare_config_data(configurator.get_validated(synchronizator.__class__))
    config_data["sync"]["targets"] = targets

    ConfigManager.write(config_path=str(config_path), config_data=config_data)


def get_remote_targets(config_path, configurator, synchronizator):
    typer.echo(f"Download targets config from provider's source! Save to {config_path}")

    config_data = ConfigManager.prepare_config_data(configurator.get_validated(synchronizator.__class__))
    config_data["sync"]["targets"] = synchronizator.remote_metadata.targets

    ConfigManager.write(config_path=str(config_path), config_data=config_data)
