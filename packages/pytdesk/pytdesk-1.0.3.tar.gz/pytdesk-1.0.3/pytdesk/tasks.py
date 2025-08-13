"""
Title: TalentDesk Tasks Module

Description:
    Interface for interacting with task-related endpoints in the TalentDesk API.
    This module supports retrieving, creating, and managing tasks associated with projects
    and opportunities. It enables functionality such as assigning tasks to users,
    updating task statuses, setting deadlines, and linking tasks to deliverables or billing data.
    Tasks are typically used to structure work assignments and track progress within projects.

Author: Scott Murray

Version: 1.0.0
"""

from .config.client_config import TASK_FILTERS, UPDATE_TASK_FIELDS, CREATE_TASK_FIELDS, TASK_ASSIGNMENT_FIELDS


########################################################################################################################
########################################################################################################################
class TasksAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_tasks(self, **filters) -> dict:
        """
        Retrieve all tasks available to the current user with optional filters.

        Optional filters include:
            - page (int) - The page number of paginated results to return
            - kw (str) - A string to filter tasks by (e.g., title, description)
            - status (str) - The task's status to filter by (e.g., "posted")
            - ids (str) - A comma-separated list of task IDs to filter by (e.g., "101,102,103")

        :param filters: Arbitrary keyword arguments for supported filters
        :return: Dict with all tasks in the org
        """

        unknown = set(filters.keys()) - TASK_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(TASK_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", "/tasks", params=filters)

########################################################################################################################
    def get_task_by_id(self, task_id) -> dict:
        """
        Get details of a specific task

        Required:
            - task_id (int) - The ID of the task to get

        :param task_id: UUID of the task
        :return: Dict containing task details
        """
        return self.client._request("GET", f"/tasks/{task_id}")

########################################################################################################################
    def get_task_custom_fields(self) -> dict:
        """
        Return all custom fields, from Task custom field templates in the organization

        :return: Dict containing task details
        """
        return self.client._request("GET", f"/tasks/custom-fields")

########################################################################################################################
    def update_task(self, id: int, **fields) -> dict:
        """
        Update the properties of an existing task.

        Required:
            - id (int) - The ID of the task to update (path parameter)

        Optional fields:
            - checklist (List[str]) - Checklist items associated with the task
            - deadline (str) - Deadline of the task (ISO 8601 format)
            - description (str) - Description of the task
            - starts_on (str) - Task start date (ISO 8601 format)
            - tags (List[str]) - Tags to associate with the task
            - title (str) - Title of the task
            - custom_field_answers (dict | None) - Key-value pairs of custom field values
            - skill_ids (List[int]) - List of skill IDs associated with the task

        :param id: The task ID to update
        :param fields: Arbitrary keyword arguments for fields to update
        :return: Dict with response data
        """

        if not fields:
            raise ValueError("At least one field must be provided to update a task.")

        unknown = set(fields.keys()) - UPDATE_TASK_FIELDS
        if unknown:
            allowed_list = ", ".join(sorted(UPDATE_TASK_FIELDS))
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}\n"
                f"Allowed fields are: {allowed_list}"
            )

        return self.client._request("PATCH", f"/tasks/{id}", json=fields)

########################################################################################################################
    def create_task(self, project_id: int, title: str, description: str, **fields) -> dict:
        """
        Create a new task within a given project.

        Required:
            - project_id (int) - The ID of the project to which the task is added
            - title (str) - The title of the task
            - description (str) - A description of the task

        Optional fields:
            - deadline (str) - Task deadline (ISO 8601); required if org enforces it
            - starts_on (str) - Task start date (ISO 8601)
            - checklist (List[str]) - A list of checklist items for the task
            - tags (List[str]) - Tags associated with the task
            - custom_field_answers (dict | None) - Custom fields and their values
            - skill_ids (List[int]) - List of skill IDs linked to the task
            - owner_user_id (int | None) - The user ID of the task owner

        :param project_id: The project ID where the task will be created
        :param title: The title of the task
        :param description: The description of the task
        :param fields: Arbitrary keyword arguments representing additional task data
        :return: Dict with response data
        """

        unknown = set(fields.keys()) - CREATE_TASK_FIELDS
        if unknown:
            allowed_list = ", ".join(sorted(CREATE_TASK_FIELDS))
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}\n"
                f"Allowed fields are: {allowed_list}"
            )

        payload = {"title": title, "description": description, **fields}

        return self.client._request("POST", f"/projects/{project_id}/add-task", json=payload)

########################################################################################################################
    def add_task_assignees(self, task_id: int, assignments: list[dict]) -> dict:
        """
        Add one or more assignees to a task.

        Required:
            - task_id (int) - ID of the task to assign users to
            - assignments (List[dict]) - A list of assignment objects, each representing one assignee

        Each assignment object may include the following fields:
            - user_id (int) - ID of the user being assigned (required)
            - message (str) - Assignment message (required)
            - suggest_rate (bool) - If suggesting a new rate (required)
            - rate_is_capped (bool) - Whether the rate is capped (required)
            - rate_amount (float) - Required if suggest_rate is True
            - rate_unit (str) - Required if suggest_rate is True
            - capped_value (float) - Required if rate_is_capped is True
            - rate_id (int) - Required if suggest_rate is False
            - currency (str) - Required if suggest_rate is True (e.g., "USD")
            - legal_documents (List[int]) - Optional list of document IDs

        :param task_id: ID of the task
        :param assignments: List of assignee assignment payloads
        :return: Dict with response data
        """

        if not isinstance(assignments, list) or not assignments:
            raise ValueError("assignments must be a non-empty list of dictionaries.")

        for idx, assignment in enumerate(assignments):
            if not isinstance(assignment, dict):
                raise ValueError(f"Assignment at index {idx} is not a dictionary.")

            unknown = set(assignment.keys()) - TASK_ASSIGNMENT_FIELDS
            if unknown:
                allowed = ", ".join(sorted(TASK_ASSIGNMENT_FIELDS))
                raise ValueError(
                    f"Unknown field(s) in assignment[{idx}]: {', '.join(unknown)}\n"
                    f"Allowed fields are: {allowed}"
                )

        payload = {"assignments": assignments}

        return self.client._request("POST", f"/tasks/{task_id}/add-assignees", json=payload)

########################################################################################################################
    def add_task_managers(self, task_id: int, manager_user_ids: list[int]) -> dict:
        """
        Add one or more managers to a task.

        Required:
            - task_id (int) - The ID of the task to add managers to
            - manager_user_ids (List[int]) - A list of user IDs to be added as managers

        :param task_id: ID of the task
        :param manager_user_ids: List of user IDs to be assigned as managers
        :return: Dict with response data
        """

        if not isinstance(manager_user_ids, list) or not all(isinstance(uid, int) for uid in manager_user_ids):
            raise ValueError("manager_user_ids must be a non-empty list of integers.")

        if not manager_user_ids:
            raise ValueError("At least one manager user ID must be provided.")

        payload = {"managerUserIds": manager_user_ids}

        return self.client._request("POST", f"/tasks/{task_id}/managers", json=payload)

########################################################################################################################
    def remove_task_manager(self, task_id: int, user_id: int) -> dict:
        """
        Remove a manager from a task.

        Required:
            - task_id (int) - The ID of the task
            - user_id (int) - The user ID of the manager to remove

        :param task_id: ID of the task to remove the manager from
        :param user_id: ID of the manager being removed
        :return: Dict with response data
        """

        return self.client._request("DELETE", f"/tasks/{task_id}/managers/{user_id}")

########################################################################################################################
    def get_custom_fields(self) -> dict:
        """
        Return all custom fields, from Task custom field templates in the organization

        :return: Dict with custom field data
        """

        return self.client._request("GET", f"/tasks/custom-fields")

########################################################################################################################
    def stop_task(self, task_id: int, message: str) -> dict:
        """
        Stop a task

        Required:
            - task_id (int) – The ID of the task to stop
            - message (str) – A reason or note detailing why the task is stopped

        :param task_id: UUID of the task
        :param message: Message associated with the action.
        :return: Dict with response data
        """
        payload = {"message": message}
        return self.client._request("PUT", f"/tasks/{task_id}/stop", json=payload)

########################################################################################################################
    def cancel_task_invitation(self, task_id: int, user_id: int, message: str) -> dict:
        """
        Cancel a user's invitation to join a task.

        Required:
            - task_id (int) – The ID of the task to cancel the invitation from
            - user_id (int) – The ID of the user whose invitation should be canceled
            - message (str) – A reason or note explaining the cancellation

        :param task_id: The ID of the task
        :param user_id: The ID of the invited user to cancel
        :param message: The cancellation message
        :return: Dict with response data
        """

        payload = {"user_id": user_id, "message": message}
        return self.client._request("PUT", f"/tasks/{task_id}/cancel-invitation", json=payload)

########################################################################################################################
    def remove_task_assignee(self, task_id: int, provider_user_id: int) -> dict:
        """
        Remove an assigned provider from a task.

        Required:
            - task_id (int) – The ID of the task
            - provider_user_id (int) – The user ID of the assignee to be removed

        :param task_id: ID of the task
        :param provider_user_id: ID of the provider/user to remove from the task
        :return: Dict with response data
        """
        return self.client._request("DELETE", f"/tasks/{task_id}/providers/{provider_user_id}")

########################################################################################################################
########################################################################################################################
