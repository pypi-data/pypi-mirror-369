"""
This module contains the function to createJob.

Functions:
    createJob: Create Job.
"""

from nomad_media_pip.src.helpers.send_request import _send_request


def _create_job_id(self, asset_id, job_results_url, external_id) -> dict | None:
    """
    Create Job.

    Args:
        asset_id (str): The asset id.
        job_results_url (str): The job results url.
        external_id (str): The external id.

    Returns:
        dict: The JSON response from the server if the request is successful.
        None: If the request fails or the response cannot be parsed as JSON.
    """

    api_url: str = f"{self.config["serviceApiUrl"]}/api/admin/job/${asset_id}"
    
    body = {
		"jobResultsUrl": job_results_url,
		"externalId": external_id,
	}
    return _send_request(self, "Create Job", api_url, "POST", None, body)
