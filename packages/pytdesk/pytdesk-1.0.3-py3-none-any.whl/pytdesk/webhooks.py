"""
Title: Webhooks Module

Description:
    Provides functionality for managing webhooks within the TalentDesk API.
    This includes creating webhook subscriptions and deleting them.

Author: Scott Murray

Version: 1.0.0

"""


########################################################################################################################
########################################################################################################################
class WebhooksAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def create_webhook(self, url: str, event: str) -> dict:
        """
        Create a new outbound webhook.
        Event Options: service-order-event, invitation-event, user-event

        :param url: The target URL to receive event data (must be publicly accessible)
        :param event: The event to subscribe to.
        :return: Dict containing the created webhook information or error message
        """
        if not url or not isinstance(url, str):
            raise ValueError("A valid 'url' string must be provided for the webhook.")

        if not isinstance(event, str):
            raise ValueError("The 'event' must be a string.")

        payload = {"event": event, "url": url}

        return self.client._request("POST", "/outbound-webhooks", json=payload)

########################################################################################################################
    def delete_webhook(self, url: str, event: str) -> dict:
        """
        Delete an outbound webhook.

        :param url: The URL of the webhook to delete (must match the registered one)
        :param event: The event associated with the webhook (default is 'service-order-event')
        :return: Dict containing the response status or error message
        """
        if not url or not isinstance(url, str):
            raise ValueError("A valid 'url' string must be provided for the webhook deletion.")

        if not isinstance(event, str):
            raise ValueError("The 'event' must be a string.")

        payload = {"event": event, "url": url}

        return self.client._request("DELETE", "/outbound-webhooks", json=payload)

########################################################################################################################
    def get_webhook_example(self, event: str) -> dict:
        """
        Retrieve an example payload for a specific outbound webhook event.

        :param event: The event name to retrieve an example for (e.g., 'invitation-event')
        :return: Dict containing the example payload or error message
        """
        if not event or not isinstance(event, str):
            raise ValueError("A valid 'event' string is required.")

        endpoint = f"/outbound-webhooks/example/{event}"
        return self.client._request("GET", endpoint)

########################################################################################################################
########################################################################################################################
