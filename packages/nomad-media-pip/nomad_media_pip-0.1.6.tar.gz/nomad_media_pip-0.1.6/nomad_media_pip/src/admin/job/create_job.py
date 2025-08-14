"""
This module contains the function to createJob.

Functions:
    _createJob: Create Job.
"""

from nomad_media_pip.src.helpers.send_request import _send_request


def _create_job(
        self, 
        bucket_name: str, 
        object_key: str, 
        notification_callback_url: str, 
        external_id: str, 
        replace_existing_job: bool | None, 
        asset_url: str | None,
        requested_tasks: list[str] | None, 
        requested_transcode_profiles: list[str] | None
    ) -> dict | None:
    """
	Creates a job.
	
	Args:
	    bucket_name (str): The bucket name.
	    object_key (str): The object key.
	    notification_callback_url (str): The notification callback url.
	    external_id (str): The external id.
	    replace_existing_job (bool | None): Whether to replace an existing job.
	    asset_url (str | None): The asset url.
	    requested_tasks (list[str] | None): The requested tasks.
	    requested_transcode_profiles (list[str] | None): The requested transcode profiles.
	
	Returns:
		dict : The JSON response from the server if the request is successful.
        None: If the request fails or the response cannot be parsed as JSON.
	"""
    api_url: str = f"{self.config["serviceApiUrl"]}/api/admin/job"
    
    body = {
		"bucketName": bucket_name,
		"objectKey": object_key,
		"notificationCallbackUrl": notification_callback_url,
		"replaceExistingJob": replace_existing_job,
		"requestedTasks": requested_tasks,
		"requestedTranscodeProfiles": requested_transcode_profiles,
		"externalId": external_id,
		"assetUrl": asset_url,
	}
    return _send_request(self, "Create Job", api_url, "POST", None, body)
