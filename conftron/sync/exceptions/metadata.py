from __future__ import annotations

from typing import TYPE_CHECKING, Any

import ujson as json

from conftron.exceptions import AppException

if TYPE_CHECKING:
    from conftron.sync.utils.metadata_manager import SyncMetadata


class AppSyncMetadataInvalid(AppException):
    def __init__(self, local_metadata: SyncMetadata, remote_metadata: SyncMetadata, message: str | None = None):
        self.message = message
        self.local_metadata = local_metadata
        self.remote_metadata = remote_metadata

    def show(self):
        return (
            f"{self.message if self.message else 'Error!'}\n"
            f"Local metadata:\n{json.dumps(self.local_metadata.to_dict(), indent=4)}\n"
            f"Remote metadata:\n{json.dumps(self.remote_metadata.to_dict(), indent=4)}"
        )


class AppInvalidMetadataValidateAction(AppException):
    def __init__(self, action: Any):
        self.action = action

    def show(self):
        return f"Invalid action name: {self.action}"
