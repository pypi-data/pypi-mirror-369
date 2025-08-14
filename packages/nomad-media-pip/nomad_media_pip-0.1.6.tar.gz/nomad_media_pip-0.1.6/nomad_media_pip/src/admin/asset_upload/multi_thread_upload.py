"""
This module contains the implementation of the multi-threaded upload function.

Functions:
    _multi_thread_upload: Uploads parts of a file in multiple threads.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from nomad_media_pip.src.admin.asset_upload.upload_thread import _upload_thread

def _multi_thread_upload(self, file: str, start_upload_info: dict) -> None:
    """
    Upload file parts concurrently.
    Client can control concurrency through their ThreadPoolExecutor configuration.
    """
    parts = start_upload_info["parts"]
    total_parts = len(parts)
    completed_parts = 0

    try:
        with open(file, "rb") as open_file:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = [
                    executor.submit(_upload_thread, self, open_file, part)
                    for part in parts
                ]

                for future in as_completed(futures):
                    try:
                        error = future.result()
                        if error:
                            raise Exception(error)
                        completed_parts += 1
                        progress = (completed_parts / total_parts)
                        logging.info(f"Upload progress: {progress:.2f}% ({completed_parts}/{(total_parts)})")

                    except Exception as e:
                        for f in futures:
                            f.cancel()
                        return False

            return True
        
    except (OSError) as e:
        logging.error(f"Error opening file {file}: {e}")
        raise

    except Exception as e:
        logging.error(f"Error during multi-thread upload")
        raise