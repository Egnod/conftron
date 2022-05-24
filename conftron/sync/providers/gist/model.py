from pydantic import Field

from conftron.sync.providers.base import (
    BaseSyncOptionsModel,
    BaseSyncOptionsModelConfig,
    BaseSyncTargetModel,
    BaseSyncTargetModelConfig,
)


class GistSyncOptions(BaseSyncOptionsModel):
    id: str = Field(...)
    token: str = Field(...)

    class Config(BaseSyncOptionsModelConfig):
        pass


class GistSyncTarget(BaseSyncTargetModel):
    class Config(BaseSyncTargetModelConfig):
        pass
