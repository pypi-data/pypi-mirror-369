"""
Title: TalentDesk Files Module

Description:
    Provides access to file-related endpoints in the TalentDesk API.
    This module allows you to upload new files to the platform
    across various resources such as projects, tasks, opportunities, and invoices.

    Supported functionality includes:
        - Uploading new files via filename-based endpoints

Author: Scott Murray

Version: 1.0.0
"""

import os
import mimetypes


########################################################################################################################
########################################################################################################################
class FilesAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def upload_file(self, file_path: str) -> dict:
        """
        Upload a file to TalentDesk as raw binary
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_name)
        if not content_type:
            content_type = "application/octet-stream"

        headers = {
            "Content-Type": content_type,
            "Accept": "application/json",
        }

        # Keep file handle open during the request
        with open(file_path, "rb") as f:
            return self.client._request(
                method="POST",
                endpoint=f"/files/{file_name}",
                data=f,              # raw stream body
                headers=headers,
            )
########################################################################################################################
########################################################################################################################
