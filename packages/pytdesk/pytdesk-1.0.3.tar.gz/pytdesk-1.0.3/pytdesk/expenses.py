"""
Title: TalentDesk Expenses Module

Description:
    Handles expense-related API interactions for TalentDesk, including
    creating, cancelling, rejecting, and listing expenses. Integrates
    with project and user ownership metadata to support approval workflows.

Author: Scott Murray

Version: 1.0.0
"""

from .config.client_config import EXPENSE_FILTERS


########################################################################################################################
########################################################################################################################
class ExpensesAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_expenses(self, **filters) -> dict:
        """
        :return: Dict with of all expenses within the entity
        """
        unknown = set(filters.keys()) - EXPENSE_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(EXPENSE_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(unknown)}\n"
                f"Allowed filters are: {allowed_list}"
            )
        return self.client._request("GET", "/expenses/", params=filters)

########################################################################################################################
    def get_expense_by_id(self, expense_id: int) -> dict:
        """
        :param expense_id: UUID of the expense to retrieve
        :return: Dictionary containing details of the expense
        """
        return self.client._request("GET", f"/expenses/{expense_id}")

########################################################################################################################
    def approve_expense(self, expense_id: int, message: str, process_at: str = "") -> dict:
        """
        :param expense_id: UUID of the expense to retrieve
        :param message: The message to be included in the approval
        :param process_at: The expense will be included in the next invoice on/after this date. Format: YYYY-MM-DD
        :return: Expense details & status
        """
        payload = {"message": message,
                   "process_at:": process_at}
        return self.client._request("PUT", f"/expenses/{expense_id}/approve", json=payload)

########################################################################################################################
    def reject_expense(self, expense_id: int, message: str) -> dict:
        """
        :param expense_id: UUID of the expense to retrieve
        :param message: The message to be included in the rejection
        :return: Expense details & status
        """
        payload = {"message": message}
        return self.client._request("PUT", f"/expenses/{expense_id}/reject", json=payload)

########################################################################################################################
    def cancel_expense(self, expense_id: int, message: str) -> dict:
        """
        :param expense_id: UUID of the expense to retrieve
        :param message: The message to be included in the cancellation
        :return: Expense details & status.
        """
        payload = {"message": message}
        return self.client._request("PUT", f"/expenses/{expense_id}/cancel", json=payload)

########################################################################################################################
    def request_amendment(self, expense_id: int, message: str) -> dict:
        """
        :param expense_id: UUID of the expense which needs to be amended
        :param message: The message to be included in the request
        :return: Expense details & status
        """
        payload = {"message": message}
        return self.client._request("PUT", f"/expenses/{expense_id}/request-amendment", json=payload)

########################################################################################################################
    def void_expense(self, expense_id: int) -> dict:
        """
        :param expense_id: UUID of the expense to retrieve
        :return: Dictionary containing details of the expense
        """
        return self.client._request("PUT", f"/expenses/{expense_id}/void")

########################################################################################################################
########################################################################################################################
