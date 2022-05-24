from __future__ import annotations

from typing import TYPE_CHECKING

from conftron.exceptions import AppException

if TYPE_CHECKING:
    pass


class AppSyncDefaultProviderNotFound(AppException):
    def show(self):
        return "Default synchronization provider not found!"
