"""
Title: TalentDesk Projects Module

Description:
    This module provides a Python interface to the TalentDesk Projects API, allowing clients to interact with and manage
    projects within their organization. It supports operations such as retrieving project details, creating new projects,
    updating project metadata, managing project teams and documents, and performing actions such as archiving or tagging.
    Methods in this module typically interface with endpoints under `/projects`, and are designed to simplify integration
    with TalentDesk’s project lifecycle workflows.

Author: Scott Murray

Version: 1.0
"""

from .config.client_config import (PROJECT_FILTERS, PROJECT_WORKSHEET_FILTERS, PROJECT_EXPENSE_FILTERS,
                                  PROJECT_TASK_FILTERS, PROJECT_TEAM_FILTERS, CREATE_PROJECT_FIELDS, UPDATE_PROJECT_FIELDS)


########################################################################################################################
########################################################################################################################
class ProjectsAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_projects(self, **filters) -> dict:
        """
        Retrieve all projects available to the current user with optional filters.

        Optional filters include:
            - page (int) – The page number to retrieve
            - kw (str) – A query string to filter projects by
            - status (str) – The project status to filter by (e.g., "posted")
            - ids (str) – A comma-separated list of project IDs
            - currency (str) – Filter projects by currency code (e.g., "USD")

        :param filters: Arbitrary keyword arguments for supported query parameters
        :return: Dict with project details
        """
        unknown = set(filters.keys()) - PROJECT_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(PROJECT_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", "/projects", params=filters)

########################################################################################################################
    def get_project_by_id(self, project_id: int) -> dict:
        """
        Retrieve a project by its unique ID.

        Required:
            - project_id (int) – The ID of the project to fetch

        :param project_id: The unique ID of the project
        :return: Dict with project details
        """
        return self.client._request("GET", f"/projects/{project_id}")

########################################################################################################################
    def get_project_worksheets(self, project_id: int, **filters) -> dict:
        """
        Retrieve all worksheets for a specific project, with optional filters.

        Required:
            - project_id (int) – The ID of the project to retrieve worksheets for

        Optional filters include:
            - page (int) – Page number for pagination
            - kw (str) – Query string to filter worksheets by
            - status (str) – Filter by worksheet status (e.g., "submitted")
            - ids (str) – Comma-separated list of worksheet IDs
            - task_id (int) – Filter by task ID
            - currency (str) – Filter by currency code (e.g., "USD")
            - invoiced (bool) – Whether the worksheet is invoiced
            - min_date (str) – Minimum date (ISO 8601)
            - max_date (str) – Maximum date (ISO 8601)
            - min_amount (float) – Minimum worksheet amount
            - max_amount (float) – Maximum worksheet amount

        :param project_id: The ID of the project
        :param filters: Arbitrary keyword arguments for supported query parameters
        :return: Dict with response data
        """
        unknown = set(filters.keys()) - PROJECT_WORKSHEET_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(PROJECT_WORKSHEET_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", f"/projects/{project_id}/worksheets", params=filters)

########################################################################################################################
    def get_project_expenses(self, project_id: int, **filters) -> dict:
        """
        Retrieve all expenses for a given project, with optional filters.

        Required:
            - project_id (int) – The ID of the project to retrieve expenses for

        Optional filters include:
            - page (int) – Page number for pagination
            - kw (str) – Query string to filter expenses by
            - status (str) – Filter by expense status (e.g., "submitted")
            - ids (str) – Comma-separated list of expense IDs
            - task_id (int) – Filter by related task ID
            - currency (str) – Currency code (e.g., "USD")
            - invoiced (bool) – Whether the expense is invoiced
            - min_date (str) – Filter by earliest date (ISO 8601)
            - max_date (str) – Filter by latest date (ISO 8601)
            - min_amount (float) – Minimum amount filter
            - max_amount (float) – Maximum amount filter

        :param project_id: The ID of the project
        :param filters: Arbitrary keyword arguments for supported query parameters
        :return: Dict with response data
        """
        unknown = set(filters.keys()) - PROJECT_EXPENSE_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(PROJECT_EXPENSE_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", f"/projects/{project_id}/expenses", params=filters)

########################################################################################################################
    def get_project_tasks(self, project_id: int, **filters) -> dict:
        """
        Retrieve all tasks associated with a specific project, with optional filters.

        Required:
            - project_id (int) – The ID of the project to retrieve tasks for

        Optional filters include:
            - page (int) – Page number for pagination
            - kw (str) – A query string to filter tasks by
            - status (str) – The status of the task (e.g., "posted")
            - ids (str) – Comma-separated list of task IDs

        :param project_id: The ID of the project
        :param filters: Arbitrary keyword arguments for supported query parameters
        :return: Dict with response data
        """
        unknown = set(filters.keys()) - PROJECT_TASK_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(PROJECT_TASK_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", f"/projects/{project_id}/tasks", params=filters)

########################################################################################################################
    def get_project_team(self, project_id: int, **filters) -> dict:
        """
        Retrieve all team members assigned to a specific project.

        Required:
            - project_id (int) – The ID of the project to retrieve the team for

        Optional filters include:
            - page (int) – Page number for pagination
            - kw (str) – Query string to filter team members (e.g., by name or role)

        :param project_id: The ID of the project
        :param filters: Arbitrary keyword arguments for supported query parameters
        :return: Dict with response data
        """
        unknown = set(filters.keys()) - PROJECT_TEAM_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(PROJECT_TEAM_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", f"/projects/{project_id}/team", params=filters)

########################################################################################################################

    def get_project_custom_fields(self) -> dict:
        """
        Retrieve all custom fields defined for projects in the organization.

        This is typically used before creating or updating a project, so the correct
        custom field paths and expected values can be supplied.

        :return: Dict with custom field definitions
        """
        return self.client._request("GET", "/projects/custom-fields")

########################################################################################################################
    def create_project(self, title: str, brief: str, owner_id: int, started_at: str, **fields) -> dict:
        """
        Create a new project with the specified details and optional fields.

        Required fields:
            - title (str): The title of the project
            - brief (str): The project brief (minimum length: 1)
            - owner_id (int): The user ID of the project owner
            - started_at (str): The start date of the project (ISO 8601)

        Optional fields:
            - all_project_managers_can_manage_team (bool | None): If any manager can manage team
            - budget (float | None): Project budget deducted from owner's budget
            - clients (List[str] | None): List of client names
            - custom_field_answers (dict | None): Custom field responses
            - deadline (str | None): Project deadline (ISO 8601)
            - documents (List[int] | None): File IDs from /files/{fileName}
            - external_project_id (str | None): External reference ID
            - only_managers_can_view_project_team (bool | None): Manager-only team visibility
            - tags (List[str] | None): List of tag strings

        :param title: Title of the project
        :param brief: Brief description of the project
        :param owner_id: ID of the user who owns the project
        :param started_at: Start date of the project (ISO 8601 format)
        :param fields: Additional optional fields for project creation
        :return: Dict with response data
        """
        unknown = set(fields.keys()) - CREATE_PROJECT_FIELDS
        if unknown:
            allowed_list = ", ".join(sorted(CREATE_PROJECT_FIELDS))
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}\n"
                f"Allowed fields are: {allowed_list}"
            )

        payload = {
            "title": title,
            "brief": brief,
            "owner_id": owner_id,
            "started_at": started_at,
            **fields
        }

        return self.client._request("POST", "/projects", json=payload)

########################################################################################################################
    def update_project(self, project_id: int, **fields) -> dict:
        """
        Update an existing project with any combination of supported fields.

        Required:
            - project_id (int): The ID of the project to update

        Optional fields (all are nullable unless stated):
            - all_project_managers_can_manage_team (bool | None): Allow any manager to manage team
            - brief (str): The updated project brief (min length ≥ 1)
            - clients (List[str] | None): Updated list of client names
            - deadline (str | None): New project deadline (ISO 8601)
            - documents (List[int] | None): File IDs from /files/{fileName}
            - external_project_id (str | None): Updated external project reference
            - only_managers_can_view_project_team (bool | None): Restrict visibility to managers
            - started_at (str | None): Updated start date (ISO 8601)
            - tags (List[str] | None): Updated tag list
            - title (str): Updated project title (min length ≥ 1)

        :param project_id: ID of the project to update
        :param fields: Arbitrary keyword arguments for the fields to update
        :return: Dict with response data
        """

        if not fields:
            raise ValueError("At least one field must be provided to update a project.")

        unknown = set(fields.keys()) - UPDATE_PROJECT_FIELDS
        if unknown:
            allowed_list = ", ".join(sorted(UPDATE_PROJECT_FIELDS))
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}\n"
                f"Allowed fields are: {allowed_list}"
            )

        return self.client._request("PATCH", f"/projects/{project_id}", json=fields)

########################################################################################################################
    def add_project_budget(self, project_id: int, budget: float) -> dict:
        """
        Add a specified budget amount to an existing project.

        Required:
            - project_id (int): The ID of the project to add budget to
            - budget (float): The amount to add to the project budget

        :param project_id: The ID of the project
        :param budget: The budget amount to add (must be a positive number)
        :return: Dict with response data
        """
        if not isinstance(budget, (int, float)) or budget <= 0:
            raise ValueError("Budget must be a positive number.")

        payload = {
            "budget": budget
        }

        return self.client._request("POST", f"/projects/{project_id}/budget", json=payload)

########################################################################################################################
    def add_project_members(self, project_id: int, user_ids: list[int], send_invitations: bool | None = None,
                            invitation_expiry_days: int | None = None) -> dict:
        """
        Add or invite users to a project.

        Required:
            - project_id (int): The ID of the project
            - user_ids (List[int]): The list of user IDs to add or invite

        Optional:
            - send_invitations (bool | None): If True, sends invitations instead of direct addition
            - invitation_expiry_days (int | None): Expiry in days for pending invitations

        :param project_id: The ID of the project
        :param user_ids: List of user IDs to add/invite
        :param send_invitations: Whether to send invitations
        :param invitation_expiry_days: Number of days until invitation expires
        :return: Dict with response data
        """
        if not user_ids or not all(isinstance(uid, int) for uid in user_ids):
            raise ValueError("At least one valid integer user_id must be provided.")

        payload = {"user_ids": user_ids}

        if send_invitations is not None:
            payload["send_invitations"] = send_invitations
        if invitation_expiry_days is not None:
            payload["invitation_expiry_days"] = invitation_expiry_days

        return self.client._request("POST", f"/projects/{project_id}/add-members", json=payload)

########################################################################################################################
    def remove_project_member(self, project_id: int, user_id: int) -> dict:
        """
        Remove a user from a project.

        Required:
            - project_id (int): The ID of the project
            - user_id (int): The ID of the user to remove

        :param project_id: The ID of the project to remove the member from
        :param user_id: The ID of the user to remove from the project
        :return: Dict with response data
        """
        if not isinstance(project_id, int) or not isinstance(user_id, int):
            raise ValueError("Both project_id and user_id must be integers.")

        endpoint = f"/projects/{project_id}/members/{user_id}"
        return self.client._request("DELETE", endpoint)

########################################################################################################################
    def update_project_status(self, project_id: int, status: str) -> dict:
        """
        Change the status of a project.

        Required:
            - project_id (int): The ID of the project
            - status (str): The new status for the project (e.g. 'in-progress', 'completed', etc.)

        Notes:
            - When setting the status to "completed", any remaining project budget will be returned to the organization owner.

        :param project_id: The ID of the project to update
        :param status: The new project status
        :return: Dict with response data
        """
        if not status or not isinstance(status, str):
            raise ValueError("A valid project status string must be provided.")

        payload = {"status": status}

        return self.client._request("PUT", f"/projects/{project_id}/status", json=payload)

########################################################################################################################
########################################################################################################################
