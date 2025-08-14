"""
This module contains the _upload_thread function that is used to upload a part of an asset to
the Nomad Media API.

Functions:
    _upload_thread: Uploads a part of an asset to the Nomad Media API.
"""

from nomad_media_pip.src.admin.asset_upload.upload_asset_part import _upload_asset_part
from nomad_media_pip.src.admin.asset_upload.upload_asset_part_complete import _upload_asset_part_complete


def _upload_thread(self, open_file, part: dict) -> None:
    """
    Uploads a part of an asset to the Nomad Media API.

    Args:
        file (str): The file to upload.
        part (dict): The part to upload.
        worker_count (dict): The number of active workers.
    """

    etag: str | None = _upload_asset_part(open_file, part, self.debug)
    if not etag:
        return "Connection error"
    _upload_asset_part_complete(self, part["id"], etag)
