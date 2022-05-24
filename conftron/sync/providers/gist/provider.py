from __future__ import annotations

import typing
from typing import TYPE_CHECKING

import github3

from conftron.sync.exceptions.metadata import AppInvalidMetadataValidateAction
from conftron.sync.providers.base import BaseSyncProvider
from conftron.sync.providers.gist.model import GistSyncOptions, GistSyncTarget
from conftron.sync.providers.gist.utils import auth_required, current_gist_required
from conftron.sync.utils.metadata_manager import MetadataManager, SyncMetadata

if TYPE_CHECKING:
    pass


class _GHClient(github3.GitHub):
    def gist(self, id_num: str):
        url = self._build_url("gists", str(id_num))
        json = self._json(self._get(url), 200)
        return self._instance_or_null(github3.gists.ShortGist, json)


class GistSyncProvider(BaseSyncProvider):
    name = "gist"
    options_model = GistSyncOptions
    targets_model = GistSyncTarget

    options: GistSyncOptions
    targets: list[GistSyncTarget]

    _gist_client: github3.GitHub
    _gist: github3.gists.Gist

    _remote_metadata: SyncMetadata | None = None

    default = True

    def __init__(self, local_sync_metadata: SyncMetadata | None = None, **kwargs):
        super().__init__(**kwargs)

        self._is_authenticated = False
        self._gist = None
        self.local_metadata = local_sync_metadata

    def _set_authentication(self):
        if not self._is_authenticated:
            self._gist_client = _GHClient(token=self.options.token)
            self._is_authenticated = True

    @property
    def remote_metadata(self):
        if not self._remote_metadata:
            self._remote_metadata = self.get_remote_metadata()

        return self._remote_metadata

    @auth_required
    def _get_gist_data(self):
        if not self._gist:
            self._gist = self._gist_client.gist(self.options.id)

        return self._gist

    @current_gist_required
    @auth_required
    def get_remote_metadata(self):
        if "metadata" not in self._gist.files or not self._gist.files["metadata"].content():
            return None

        return MetadataManager.deserialize(self._gist.files["metadata"].content())

    @current_gist_required
    @auth_required
    def update_metadata(self, metadata: SyncMetadata, return_edit_schema: bool = False):
        MetadataManager.write(self._kwargs["metadata_path"], metadata)

        edit_schema = {
            "metadata": {
                "content": MetadataManager.serialize(metadata),
                "filename": "metadata",
            }
        }

        if return_edit_schema:
            return edit_schema

        self._gist.edit(files=edit_schema)

    @current_gist_required
    @auth_required
    def validate_metadata(self, action: typing.Literal["upload", "download"]):
        if action == "upload":
            return bool(self.targets)

        elif action == "download":
            return bool(self.get_remote_metadata())

        else:
            raise AppInvalidMetadataValidateAction(action)

    @current_gist_required
    @auth_required
    def download(self):
        possibility_download_status = self.validate_metadata(action="download")

        status = {
            "possibility_download_status": possibility_download_status,
            "targets_status": {},
            "targets_config": [],
        }

        if possibility_download_status:
            for target in self.targets:
                target_download_status = False

                if target_file := (self._gist.files[target.get_target_name()]):
                    if not target.path.parent.is_dir():
                        target.path.parent.mkdir(parents=True, exist_ok=True)

                    if not target.path.is_file():
                        target.path.touch()

                    target.path.write_bytes(target_file.content())

                    target_download_status = True

                status["targets_status"][target.get_target_name()] = target_download_status

            metadata = self.get_remote_metadata()

            status["targets_config"] = metadata.targets

            MetadataManager.write(self._kwargs["metadata_path"], metadata)

        return status

    @current_gist_required
    @auth_required
    def check_target_available(self, target: GistSyncTarget):
        return target.get_target_name() in self._gist.files

    @current_gist_required
    @auth_required
    def upload(self):
        possibility_upload_status = self.validate_metadata(action="upload")

        status = {"possibility_upload_status": possibility_upload_status, "targets_status": {}}

        targets_config_metadata = []

        if possibility_upload_status:
            targets_upload = {}

            if self.targets:  # For targets proceed
                for target in self.targets:
                    target_upload = {}

                    target_upload["filename"] = target.get_target_name()
                    target_upload["content"] = target.get_data()

                    target_upload_status = target.check_local_availability()

                    if target_upload_status:
                        targets_upload[target.get_target_name()] = target_upload.copy()

                    status["targets_status"][target.get_target_name()] = target_upload_status

                    targets_config_metadata.append(target.dict())

            else:
                return status

            new_metadata = MetadataManager.generate()
            new_metadata.targets = targets_config_metadata

            targets_upload.update(self.update_metadata(new_metadata, return_edit_schema=True))

            self._gist.edit(files=targets_upload, description=f"Last update: {new_metadata.datetime}")

            return status

        return status

    @auth_required
    def is_healthy(self) -> bool:
        self._logger.info(f"Your gist's sync metadata: {self.get_remote_metadata()}")

        return True
