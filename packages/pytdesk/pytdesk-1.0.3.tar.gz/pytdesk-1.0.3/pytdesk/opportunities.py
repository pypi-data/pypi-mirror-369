"""
Title: TalentDesk Opportunities Module

Description:
    Provides an interface for interacting with the Opportunities endpoints of the TalentDesk API.
    Supports operations such as retrieving open opportunities, submitting proposals,
    managing freelancer interest, and tracking opportunity status and assignment workflows.
    Enables clients or managers to publish project-based or ad-hoc opportunities to their resource pool.

Author: Scott Murray

Version: 1.0.0
"""

from .config.client_config import OPPORTUNITY_FILTERS, CREATE_OPPORTUNITY_FIELDS, UPDATE_OPPORTUNITY_FIELDS


########################################################################################################################
########################################################################################################################
class OpportunitiesAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_opportunities(self, **filters) -> dict:
        """
        Retrieve all opportunities available to the organization with optional filters.

        Optional filters include:
            - page (int) - The page number to use
            - kw (str) - A string to filter opportunities by
            - status (str) - The opportunity's status to filter by (e.g., "posted")
            - ids (str) - A comma-separated list of opportunity IDs to filter by
            - currency (str) - The currency code to filter by (e.g., "USD")

        :param filters: Arbitrary keyword arguments for supported filters
        :return: Dict containing opportunity details
        """

        unknown = set(filters.keys()) - OPPORTUNITY_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(OPPORTUNITY_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(unknown)}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", "/opportunities", params=filters)

########################################################################################################################
    def create_opportunity(self, title: str, brief: str, owner_id: int, **fields) -> dict:
        """
        Create a new opportunity with the specified fields.

        Optional fields:
            - all_project_managers_can_manage_team (bool | None) - If any managers can add/remove team members
            - budget (float | None) - The opportunity's budget
            - clients (List[str] | None) - Array of client names
            - custom_field_answers (dict | None) - Custom fields answered
            - deadline (str | None) - Opportunity deadline (ISO 8601)
            - documents (List[int] | None) - File IDs uploaded via /files endpoint
            - external_project_id (str | None) - External reconciliation reference
            - only_managers_can_view_project_team (bool | None) - Restrict project team visibility to managers
            - tags (List[str] | None) - Tags for opportunity classification
            - invitations_only (bool | None) - If only invited providers can see/apply
            - max_applicants (int | None) - Max number of applicants allowed
            - rate_guide_unit (str | None) - Rate unit (e.g., "hourly")
            - rate_guide_min (float | None) - Minimum rate for applications
            - rate_guide_max (float | None) - Maximum rate for applications
            - rate_guide_fixed (float | None) - Fixed rate amount for applications
        :param title: Title of the opportunity
        :param brief: The opportunity brief
        :param owner_id: The user id of the manager who will be the owner of the opportunity
        :param fields: Arbitrary keyword arguments representing the opportunity payload
        :return: Dict with response data of the created opportunity
        """

        unknown = set(fields.keys()) - CREATE_OPPORTUNITY_FIELDS
        if unknown:
            allowed_list = ", ".join(sorted(CREATE_OPPORTUNITY_FIELDS))
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}\n"
                f"Allowed fields are: {allowed_list}"
            )

        payload = {
            "title": title,
            "brief": brief,
            "owner_id": owner_id,
            **fields
        }

        return self.client._request("POST", "/opportunities", json=payload)

########################################################################################################################
    def get_opportunity_by_id(self, opp_id: int) -> dict:
        """
        Get opportunity using the ID
        :param opp_id: UUID of the opportunity
        :return: Dictionary containing opportunity details
        """
        return self.client._request("GET", f"/opportunities/{opp_id}")

########################################################################################################################
    def update_opportunity(self, id: int, **fields) -> dict:
        """
        Update an existing opportunity.

        Required:
            - id (int) - The ID of the opportunity to update (path param)

        Optional fields:
            - title (str) - Updated title of the opportunity
            - brief (str) - Updated brief/description
            - all_project_managers_can_manage_team (bool | None)
            - clients (List[str] | None)
            - deadline (str | None)
            - documents (List[int] | None)
            - external_project_id (str | None)
            - only_managers_can_view_project_team (bool | None)
            - started_at (str | None)
            - tags (List[str] | None)
            - invitations_only (bool | None)
            - max_applicants (int | None)
            - rate_guide_unit (str | None)
            - rate_guide_min (float | None)
            - rate_guide_max (float | None)
            - rate_guide_fixed (float | None)

        :param id: The opportunity ID to update
        :param fields: Optional fields to update
        :return: Dict with response data
        """

        if not fields:
            raise ValueError("At least one field must be provided to update an opportunity.")

        unknown = set(fields.keys()) - UPDATE_OPPORTUNITY_FIELDS
        if unknown:
            allowed_list = ", ".join(sorted(UPDATE_OPPORTUNITY_FIELDS))
            raise ValueError(
                f"Unknown field(s): {', '.join(sorted(unknown))}\n"
                f"Allowed fields are: {allowed_list}"
            )

        return self.client._request("PATCH", f"/opportunities/{id}", json=fields)

########################################################################################################################
########################################################################################################################
