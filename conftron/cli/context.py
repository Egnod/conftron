from __future__ import annotations

import typing
from dataclasses import dataclass
from pathlib import Path

import typer
from structlog.types import WrappedLogger
from yaspin.core import Yaspin
from yaspin.spinners import Spinners

from conftron.cli.utils.stub_sync_provider import StubSyncProvider
from conftron.config.configurator import Configurator

if typing.TYPE_CHECKING:
    from conftron.sync.providers.base import BaseSyncProvider


@dataclass
class AppContextObject:
    config_path: Path
    logger: WrappedLogger

    config: Configurator = Configurator(config_provider=None)

    synchronizator: BaseSyncProvider = StubSyncProvider()

    spinner: Yaspin = Yaspin(spinner=Spinners.aesthetic)

    @property
    def metadata_path(self):
        return self.config_path.parent / "metadata.conftron"


class Context(typer.Context):
    obj: AppContextObject
