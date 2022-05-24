from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from conftron.sync.providers.gist import GistSyncProvider


def auth_required(func):
    @wraps(func)
    def wrapper(self: GistSyncProvider, *args, **kwargs):
        self._set_authentication()

        if self._is_authenticated:
            return func(self, *args, **kwargs)

    return wrapper


def current_gist_required(func):
    @wraps(func)
    def wrapper(self: GistSyncProvider, *args, **kwargs):
        self._get_gist_data()

        if self._gist:
            return func(self, *args, **kwargs)

    return wrapper
