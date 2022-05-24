from __future__ import annotations

from typing import TYPE_CHECKING

from conftron.sync.providers.base import BaseSyncProvider

if TYPE_CHECKING:
    from conftron.sync.providers.base import BaseSyncTargetModel
    from conftron.sync.utils.metadata_manager import SyncMetadata


class StubSyncProvider(BaseSyncProvider):
    """Stub class for sync providers classes."""

    name: str = "stub"
    hidden: bool = True

    def __init__(self, *args, **kwargs):
        pass

    def download(self):
        NotImplementedError()

    def upload(self):
        NotImplementedError()

    def download_targets(self):
        NotImplementedError()

    def upload_targets(self):
        NotImplementedError()

    def is_healthy(self):
        NotImplementedError()

    def get_remote_metadata(self):
        NotImplementedError()

    def get_remote_targets(self):
        NotImplementedError()

    def update_metadata(self, metadata: SyncMetadata):
        NotImplementedError()

    def validate_metadata(self, action: str):
        NotImplementedError()

    def check_target_available(self, target: BaseSyncTargetModel):
        NotImplementedError()
