from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

from conftron.logs import get_logger
from conftron.sync.providers.base.model import BaseSyncOptionsModel, BaseSyncTargetModel

if TYPE_CHECKING:
    from conftron.sync.utils.metadata_manager import SyncMetadata


class BaseSyncProvider(metaclass=ABCMeta):
    """Base class for sync providers classes."""

    name: str
    options_model: type[BaseSyncOptionsModel]
    targets_model: type[BaseSyncTargetModel]

    local_metadata: SyncMetadata | None = None
    remote_metadata: SyncMetadata | None = None

    default: bool = False
    hidden: bool = False

    def __init__(self, options: dict[str, str], targets: list[dict[str, Any]], force: bool, **kwargs):
        self.with_force = force
        self.options = self.options_model(**options)
        self.targets = [self.targets_model(**target) for target in targets]
        self._logger = get_logger(__name__)
        self._kwargs = kwargs

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self):
        pass

    @abstractmethod
    def check_target_available(self, target: BaseSyncTargetModel):
        pass

    @abstractmethod
    def get_remote_metadata(self) -> SyncMetadata:
        pass

    @abstractmethod
    def update_metadata(self, metadata: SyncMetadata):
        pass

    @abstractmethod
    def validate_metadata(self, action: str) -> bool:
        pass

    @abstractmethod
    def is_healthy(self) -> bool:
        pass
