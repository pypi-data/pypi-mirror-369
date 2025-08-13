"""
Title: Pro Forma Invoice Module

Description:
    Provides methods for interacting with pro forma invoices via the TalentDesk API.

    Pro forma invoices represent draft financial summaries of work completed or anticipated,
    which can be reviewed before a formal invoice is generated. This module allows clients to
    retrieve and manage pro forma invoice records for a given organization, including optional
    filtering by status, amount, or related entities like projects or tasks.

    Common use cases include:
        - Fetching all pro forma invoices for review or reconciliation
        - Filtering by currency, project, amount, or date
        - Validating data before converting to actual invoices
        - Integrating financial review workflows prior to payment

Author: Scott Murray

Version: 1.0.0
"""

from .config.client_config import PROFORMA_INVOICE_FILTERS


########################################################################################################################
########################################################################################################################
class ProFormaInvoicesAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_proforma_invoices(self, **filters) -> dict:
        """
        Retrieve all pro forma invoices available for the current user with optional filters.

        Optional filters include:
            - kw (str) - A string to filter Proforma Invoices by
            - status (str) - The Proforma Invoice status to filter by
            - ids (str) - A comma-separated list of Proforma Invoice IDs to include
            - task_id (int) - A task ID to filter Proforma Invoices by
            - currency (str) - Currency code (e.g., 'USD')
            - invoiced (bool) - Whether the Proforma Invoice has been invoiced
            - project_id (int) - Filter by project ID
            - min_date (str) - Start date (ISO 8601)
            - max_date (str) - End date (ISO 8601)
            - min_amount (float) - Minimum invoice amount
            - max_amount (float) - Maximum invoice amount

        :param filters: Arbitrary keyword arguments for filtering the Proforma Invoices
        :return: Dict with response data
        """
        unknown = set(filters) - PROFORMA_INVOICE_FILTERS
        if unknown:
            allowed = ", ".join(sorted(PROFORMA_INVOICE_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(sorted(unknown))}\n"
                f"Allowed filters are: {allowed}"
            )

        return self.client._request("GET", "/proforma-invoices", params=filters)

########################################################################################################################
    def get_proforma_invoice_by_id(self, proforma_invoice_id: int) -> dict:
        """
        Retrieve a specific Proforma Invoice by its unique ID.

        :param proforma_invoice_id: The ID of the Proforma Invoice to retrieve
        :return: Dict with response data
        """
        if not isinstance(proforma_invoice_id, int):
            raise ValueError("proforma_invoice_id must be an integer")

        endpoint = f"/proforma-invoices/{proforma_invoice_id}"
        return self.client._request("GET", endpoint)

########################################################################################################################
    def reject_proforma_invoice(self, proforma_invoice_id: int, message: str) -> dict:
        """
        Reject a Proforma Invoice with a specified message.

        :param proforma_invoice_id: The ID of the Proforma Invoice to reject
        :param message: Rejection message (reason for rejection)
        :return: Dict with response data
        """
        if not isinstance(proforma_invoice_id, int):
            raise ValueError("proforma_invoice_id must be an integer")

        if not message or not isinstance(message, str):
            raise ValueError("A non-empty rejection message must be provided")

        endpoint = f"/proforma-invoices/{proforma_invoice_id}/reject"
        payload = {"message": message}
        return self.client._request("PUT", endpoint, json=payload)

########################################################################################################################
    def approve_proforma_invoice(self, proforma_invoice_id: int, message: str, process_at: str = None) -> dict:
        """
        Approve a Proforma Invoice by its ID.

        :param proforma_invoice_id: The ID of the Proforma Invoice to approve
        :param message: A required message for the approval
        :param process_at: Optional ISO date string to schedule processing on/after a specific date
        :return: Dict with response data
        """
        if not message or not isinstance(message, str):
            raise ValueError("A non-empty message string is required to approve the pro-forma invoice.")

        payload = {"message": message}
        if process_at:
            payload["process_at"] = process_at

        endpoint = f"/proforma-invoices/{proforma_invoice_id}/approve"
        return self.client._request("PUT", endpoint, json=payload)

########################################################################################################################
    def request_amendment(self, proforma_invoice_id: int, message: str) -> dict:
        """
        Request an amendment for a Proforma Invoice.

        :param proforma_invoice_id: The ID of the Proforma Invoice to request an amendment for
        :param message: A required message explaining why the amendment is requested
        :return: Dict with response data
        """
        if not message or not isinstance(message, str):
            raise ValueError("A non-empty message string is required to request an amendment.")

        payload = {"message": message}
        endpoint = f"/proforma-invoices/{proforma_invoice_id}/request-amendment"
        return self.client._request("PUT", endpoint, json=payload)

########################################################################################################################
    def void_proforma_invoice(self, proforma_invoice_id: int) -> dict:
        """
        Void a Proforma Invoice.

        :param proforma_invoice_id: The ID of the Proforma Invoice to void
        :return: Dict with response data
        """
        if not isinstance(proforma_invoice_id, int):
            raise ValueError("proforma_invoice_id must be an integer.")

        endpoint = f"/proforma-invoices/{proforma_invoice_id}/void"
        return self.client._request("PUT", endpoint)

########################################################################################################################
########################################################################################################################
