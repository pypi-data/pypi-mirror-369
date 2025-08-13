"""
Title: Worksheets Module

Description:
    This module provides a set of methods for interacting with worksheets in the TalentDesk platform.
    Worksheets are used to log time, deliverables, and other billable items associated with tasks or projects.
    It includes functionality for retrieving worksheet data, filtering by multiple parameters such as task,
    status, currency, invoicing state, or date ranges.

    Common use cases include:
        - Fetching all worksheets for a user or project
        - Filtering worksheets by task, project, or status
        - Integrating worksheet data into financial reporting or invoicing pipelines

    This module is typically used in conjunction with tasks, projects, and invoice modules.

Author: Scott Murray

Version: 1.0.0

"""

from .config.client_config import WORKSHEET_FILTERS


########################################################################################################################
########################################################################################################################
class WorksheetsAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_worksheets(self, **filters) -> dict:
        """
        Retrieve all worksheets in the organization with optional filters.

        Optional filters include:
            - page (int): The page number to use
            - kw (str): A string to filter worksheets by
            - status (str): The worksheet's status to filter by (e.g., 'submitted')
            - ids (str): A comma-separated list of worksheet IDs to filter by
            - task_id (int): A task ID to filter worksheets by
            - currency (str): Currency to filter by (e.g., 'USD')
            - invoiced (bool): Whether the worksheet is invoiced or not
            - project_id (int): Filter worksheets by project ID
            - min_date (str): Minimum date (ISO 8601)
            - max_date (str): Maximum date (ISO 8601)
            - min_amount (float): Minimum amount filter
            - max_amount (float): Maximum amount filter
            - user_id (str): A comma-separated list of user IDs to filter worksheets by

        :param filters: Arbitrary keyword arguments for supported filters
        :return: Dict with all worksheets for the org
        """

        unknown = set(filters.keys()) - WORKSHEET_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(WORKSHEET_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(unknown)}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", "/worksheets", params=filters)

########################################################################################################################
    def get_worksheet_by_id(self, worksheet_id: int) -> dict:
        """
        Retrieve a worksheet by its ID.

        :param worksheet_id: The ID of the worksheet to retrieve
        :return: Dict with worksheet details
        """
        if not isinstance(worksheet_id, int):
            raise ValueError("worksheet_id must be an integer")

        endpoint = f"/worksheets/{worksheet_id}"
        return self.client._request("GET", endpoint)

########################################################################################################################
    def approve_worksheet(self, worksheet_id: int, message: str, process_at: str = None) -> dict:
        """
        Approve a worksheet by ID.

        :param worksheet_id: The ID of the worksheet to approve
        :param message: A message to include with the approval (required)
        :param process_at: Optional ISO 8601 date to include in the next invoice on/after this date
        :return: Dict with response data
        """
        if not isinstance(worksheet_id, int):
            raise ValueError("worksheet_id must be an integer")
        if not message or not isinstance(message, str):
            raise ValueError("A non-empty message string is required to approve a worksheet.")

        payload = {"message": message}
        if process_at:
            payload["process_at"] = process_at

        endpoint = f"/worksheets/{worksheet_id}/approve"
        response = self.client._request("PUT", endpoint, json=payload)
        if response['data']:
            if response['data']['status'] == "not-enough-funds":
                print("[ERROR] Not enough funds")
                return {'success': False, 'data': None, 'error': 'Not enough funds'}

        return response

########################################################################################################################
    def reject_worksheet(self, worksheet_id: int, message: str) -> dict:
        """
        Reject a worksheet by ID.

        :param worksheet_id: The ID of the worksheet to reject
        :param message: A message explaining the reason for rejection
        :return: Dict with response data
        """
        if not isinstance(worksheet_id, int):
            raise ValueError("worksheet_id must be an integer")
        if not message or not isinstance(message, str):
            raise ValueError("A non-empty message string is required to reject a worksheet.")

        payload = {"message": message}
        endpoint = f"/worksheets/{worksheet_id}/reject"
        return self.client._request("PUT", endpoint, json=payload)

########################################################################################################################
    def cancel_worksheet(self, worksheet_id: int, message: str) -> dict:
        """
        Cancel a worksheet by ID.

        :param worksheet_id: The ID of the worksheet to cancel
        :param message: A message explaining the reason for cancellation
        :return: Dict with response data
        """
        if not isinstance(worksheet_id, int):
            raise ValueError("worksheet_id must be an integer")
        if not message or not isinstance(message, str):
            raise ValueError("A non-empty message string is required to cancel a worksheet.")

        payload = {"message": message}
        endpoint = f"/worksheets/{worksheet_id}/cancel"
        return self.client._request("PUT", endpoint, json=payload)

########################################################################################################################
    def request_worksheet_amendment(self, worksheet_id: int, message: str) -> dict:
        """
        Request an amendment for a worksheet by ID.

        :param worksheet_id: The ID of the worksheet to amend
        :param message: A message explaining the reason for the amendment
        :return: Dict with response data
        """
        if not isinstance(worksheet_id, int):
            raise ValueError("worksheet_id must be an integer")
        if not message or not isinstance(message, str):
            raise ValueError("A non-empty message string is required to request an amendment.")

        payload = {"message": message}
        endpoint = f"/worksheets/{worksheet_id}/request-amendment"
        return self.client._request("PUT", endpoint, json=payload)

########################################################################################################################
    def void_worksheet(self, worksheet_id: int) -> dict:
        """
        Void a worksheet by ID.

        :param worksheet_id: The ID of the worksheet to void
        :return: Dict with response data
        """
        if not isinstance(worksheet_id, int):
            raise ValueError("worksheet_id must be an integer.")

        endpoint = f"/worksheets/{worksheet_id}/void"
        return self.client._request("PUT", endpoint)

########################################################################################################################
########################################################################################################################
