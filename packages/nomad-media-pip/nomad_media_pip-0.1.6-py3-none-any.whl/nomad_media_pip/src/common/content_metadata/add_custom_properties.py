"""
This module is used to add custom properties to an asset.

Functions:
    _add_custom_properties: Adds custom properties to an asset.
"""

from nomad_media_pip.src.helpers.send_request import _send_request


def _add_custom_properties(
    self,
    content_id: str,
    name: str | None = None,
    date: str | None = None,
    custom_properties: dict | None = None,
    available_start_date: str | None = None,
    available_end_date: str | None = None
) -> dict | None:
    """
    Adds custom properties to an asset.

    Args:
        content_id (str): The ID of the asset to add custom properties to.
        name (str | None): The display name of the asset.
        date (str | None): The display date of the asset.
        custom_properties (dict | None): The custom properties of the asset.
        available_start_date (str | None): The availability starting date of the asset for entitlement purposes.
        available_end_date (str | None): The availability ending date of the asset for entitlement purposes.

    Returns:
        dict: The JSON response from the server if the request is successful.
        None: If the request fails or the response cannot be parsed as JSON.
    """

    api_url: str = f"{self.config["serviceApiUrl"]}/api/admin/asset/{content_id}"

    body: dict = {}

    if name is not None:
        body["displayName"] = name
    if date is not None:
        body["displayDate"] = date
    if custom_properties is not None:
        body["customProperties"] = custom_properties
    if available_start_date is not None:
        body["availableStartDate"] = available_start_date
    if available_end_date is not None:
        body["availableEndDate"] = available_end_date

    return _send_request(self, "Add Custom Properties", api_url, "PATCH", None, body)
