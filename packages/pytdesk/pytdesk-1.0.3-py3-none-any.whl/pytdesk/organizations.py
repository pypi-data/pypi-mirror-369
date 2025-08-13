"""
Title: TalentDesk Organizations Module

Description:
    Provides access to organization-level endpoints in the TalentDesk API.
    This module enables retrieval of high-level metadata and configuration for the
    authenticated organization.

Author: Scott Murray

Version: 1.0.0
"""


########################################################################################################################
########################################################################################################################
class OrganizationsAPI:
    def __init__(self, client):
        self.client = client

########################################################################################################################
    def get_org(self) -> dict:
        """
        :return: Dict with organization details
        """
        return self.client._request("GET", "/organization/")

########################################################################################################################
########################################################################################################################
