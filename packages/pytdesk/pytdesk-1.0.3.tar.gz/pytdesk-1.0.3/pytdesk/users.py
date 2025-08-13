"""
Title: TalentDesk User Module

Description:
    Interface for interacting with user-related endpoints in the TalentDesk API.
    Supports operations such as retrieving user lists with filters,
    querying user attributes, and managing user-specific configurations.

Author: Scott Murray

Version: 1.0.0
"""

from .config.client_config import USER_FILTERS


########################################################################################################################
########################################################################################################################
class UserAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_all_users(self, **filters) -> dict:
        """
           Retrieve all users within the organization with optional filters.

           Optional filters include:
               - page (int) - The page number to use
               - kw (str) - A string to filter users by
               - status (str) - The user's status to filter by
               - role (str) - The role of the users to filter by
               - employment (str) - The employment type of the users to filter by
               - country (str, ISO-2) - A two-letter ISO country code to filter the users by country
               - language (str, ISO-2) - A two-letter ISO language code to filter the users by language
               - incorporated (int, 0 or 1) - Whether the user is incorporated or not
               - min_rating (float) - the minimum rating to filter users by
               - min_rate (float) - the minimum rate amount to filter the users by
               - max_rate (float) - the maximum rate amount to filter the users by

           :param filters: Arbitrary keyword arguments for supported filters
           :return: Dict with response data
        """

        unknown = set(filters.keys()) - USER_FILTERS
        if unknown:
            allowed_list = ", ".join(sorted(USER_FILTERS))
            raise ValueError(
                f"Unknown filter(s): {', '.join(unknown)}\n"
                f"Allowed filters are: {allowed_list}"
            )

        return self.client._request("GET", "/users/", params=filters)

########################################################################################################################
    def me(self) -> dict:
        """
        :return: Return details of the current authorized user
        """
        return self.client._request("GET", "/me")

########################################################################################################################
    def get_user_by_id(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user data
        """
        return self.client._request("GET", f"/users/{user_id}")

########################################################################################################################
    def get_user_skills(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user skills
        """
        return self.client._request("GET", f"/users/{user_id}/skills")

########################################################################################################################
    def get_user_notes(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user notes
        """
        return self.client._request("GET", f"/users/{user_id}/notes")

########################################################################################################################
    def get_user_languages(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user languages
        """
        return self.client._request("GET", f"/users/{user_id}/languages")

########################################################################################################################
    def get_user_availability(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user availability
        """
        return self.client._request("GET", f"/users/{user_id}/availability")

########################################################################################################################
    def get_user_socials(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user social media accounts
        """
        return self.client._request("GET", f"/users/{user_id}/socials")

########################################################################################################################
    def get_user_rates(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user rates
        """
        return self.client._request("GET", f"/users/{user_id}/rates")

########################################################################################################################
    def get_user_rate_details(self, user_id, rate_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :param: rate_id: UUID of the rate. Int32
        :return: Dictionary containing user rate information
        """
        return self.client._request("GET", f"/users/{user_id}/rates/{rate_id}")

########################################################################################################################
    def get_user_reviews(self, user_id) -> dict:
        """
        :param: user_id: UUID of the user. Int32
        :return: Dictionary containing user reviews
        """
        return self.client._request("GET", f"/users/{user_id}/reviews")

########################################################################################################################
########################################################################################################################
