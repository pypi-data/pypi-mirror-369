"""
This module gets the media group from the service API.

Functions:
    _get_media_group: Gets the media group.
"""

from nomad_media_pip.src.helpers.send_request import _send_request


def _get_media_group(self, media_group_id: str, filter_ids) -> dict | None:
    """
    Gets the media group.

    Args:
        media_group_id (str): The ID of the media group.
        filter_ids (list[str] | None): The IDs of the media items to filter by. If None, all media items are returned.Q

    Returns:
        dict: The JSON response from the server if the request is successful.
        None: If the request fails or the response cannot be parsed as JSON.
    """

    api_url: str = f"{self.config["serviceApiUrl"]}/api/media/group/{media_group_id}"
    if filter_ids:
        api_url += "?" + "&".join(f"filterIds={fid}" for fid in filter_ids)


    return _send_request(self, "Get Media Group", api_url, "GET", None, None)
