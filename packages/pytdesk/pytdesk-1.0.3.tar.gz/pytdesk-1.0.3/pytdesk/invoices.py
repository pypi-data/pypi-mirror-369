"""
Title: TalentDesk Invoices Module

Description:
    Provides methods to interact with the TalentDesk API's invoicing functionality.
    This module enables retrieval and management of invoices, including:
        - Listing all invoices
        - Filtering by status, currency, or related entity (user, task, project)
        - Fetching specific invoice details
        - Managing invoice-related data such as line items or associated documents

    Common use cases include:
        - Generating invoice reports
        - Verifying payment status
        - Integrating with accounting or financial systems

Author: Scott Murray

Version: 1.0.0
"""

from .config.client_config import INVOICE_FILTERS


########################################################################################################################
########################################################################################################################
class InvoicesAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_invoices(self, **filters) -> dict:
        """
        Retrieve all invoices available to the current user, with optional filters.

        Optional filters include:
            - page (int): Page number for paginated results
            - kw (str): A string to filter invoices by
            - status (str): Status of the invoice
            - currency (str): Currency code (e.g., 'USD')
            - project_id (int): Filter invoices by project ID
            - raised_by (str): Filter invoices by the user who raised them
            - min_date (str): Filter invoices created on/after this date (ISO 8601)
            - max_date (str): Filter invoices created on/before this date (ISO 8601)
            - min_amount (float): Minimum invoice amount
            - max_amount (float): Maximum invoice amount

        :param filters: Arbitrary keyword arguments representing filter options
        :return: Dict containing invoice results
        """

        unknown = set(filters.keys()) - INVOICE_FILTERS
        if unknown:
            allowed = ", ".join(sorted(INVOICE_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(unknown)}\n"
                f"Allowed filters are: {allowed}"
            )

        return self.client._request("GET", "/invoices", params=filters)

########################################################################################################################
    def get_invoice_by_id(self, invoice_id: int) -> dict:
        """
        Retrieve a specific invoice by its ID.

        Required:
            - invoice_id (int): The ID of the invoice to retrieve

        :param invoice_id: Unique identifier of the invoice
        :return: Dict containing the invoice details
        """
        if not isinstance(invoice_id, int):
            raise ValueError("The invoice_id must be an integer.")

        return self.client._request("GET", f"/invoices/{invoice_id}")

########################################################################################################################
    def mark_invoice_as_paid(self, invoice_id: int) -> dict:
        """
        Mark an invoice as paid.

        Required:
            - invoice_id (int): The ID of the invoice to be marked as paid

        :param invoice_id: Unique identifier of the invoice
        :return: Dict with response data confirming the invoice status update
        """
        if not isinstance(invoice_id, int):
            raise ValueError("The invoice_id must be an integer.")

        return self.client._request("PUT", f"/invoices/{invoice_id}/mark-as-paid")

########################################################################################################################
########################################################################################################################
