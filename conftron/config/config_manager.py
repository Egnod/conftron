from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from conftron.sync.providers.base import BaseSyncProvider
    from conftron.sync.providers.base import BaseSyncModel

import yaml
from pydantic import create_model

from conftron.sync.utils.providers import get_providers_names_enum


class ConfigManager:
    @classmethod
    def prepare_config_data(cls, config_data: type[BaseSyncModel]) -> dict:
        serialized = config_data.json()

        return config_data.Config.json_loads(serialized)

    @classmethod
    def write(cls, config_path: str, config_data: dict):
        with open(config_path, "w+") as f:
            yaml.safe_dump(config_data, stream=f, indent=4, sort_keys=True, default_flow_style=False)

    @classmethod
    def get_config_model(cls, provider_class: type[BaseSyncProvider]):
        sync_section_model = create_model(
            f"ConfigSyncFor{provider_class.name.capitalize()}",
            provider=(get_providers_names_enum(), provider_class.name),
            options=(provider_class.options_model, ...),
            targets=(list[provider_class.targets_model], []),  # type: ignore
        )
        config_model = create_model(f"ConfigFor{provider_class.name.capitalize()}", sync=(sync_section_model, ...))

        return config_model
