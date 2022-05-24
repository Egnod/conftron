from pathlib import Path

from conftron.config.configurator import Configurator
from conftron.sync.utils import get_synchronizator as get_synchronizator_provider
from conftron.sync.utils.metadata_manager import MetadataManager


def get_synchronizator(config: Configurator, metadata_path: Path, healthcheck: bool = True, *args, **kwargs):
    local_sync_metadata = MetadataManager.read(metadata_path)
    synchronizator = get_synchronizator_provider(
        config.get("sync"), local_sync_metadata=local_sync_metadata, metadata_path=metadata_path
    )

    if healthcheck:
        synchronizator.is_healthy()

    return synchronizator
