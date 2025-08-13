"""
Title: TalentDesk API Client
Description:
    Core API client for interacting with the TalentDesk REST API.
    Handles authentication, session management, error handling, retries,
    and generic request dispatching across all modules (users, expenses, projects, etc.).
Author: Scott Murray
Version: 1.0.0
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
from .expenses import ExpensesAPI
from .users import UserAPI
from .opportunities import OpportunitiesAPI
from .organizations import OrganizationsAPI
from .tasks import TasksAPI
from .projects import ProjectsAPI
from .invoices import InvoicesAPI
from .files import FilesAPI
from .pro_forma_invoices import ProFormaInvoicesAPI
from .worksheets import WorksheetsAPI
from .webhooks import WebhooksAPI


########################################################################################################################
########################################################################################################################
class TalentDeskClient:

    def __init__(self, token: str, mode='production', timeout=10, max_retries=3, backoff_factor=0.3) -> None:
        """
        Initialise the API client and set default attributes
        :param token: API Token
        :param: mode: production or development. Production is the default. Used to determine which API environment to use.
        :param timeout: Set to 10 seconds as the default
        :param max_retries: Will attempt 3 requests before returning an error
        :param backoff_factor: Exponential backoff. Increase to extend the time between retries. 0.3 is the default
        """
        self.base_url = "https://api.talentdesk.io/"
        if mode == 'development':
            self.base_url = "https://api-demo.talentdesk.dev/"
        self.token = token
        self.timeout = timeout
        self.session = self._init_session(max_retries, backoff_factor)
        self.expenses = ExpensesAPI(self)
        self.users = UserAPI(self)
        self.opportunities = OpportunitiesAPI(self)
        self.organizations = OrganizationsAPI(self)
        self.tasks = TasksAPI(self)
        self.projects = ProjectsAPI(self)
        self.invoices = InvoicesAPI(self)
        self.files = FilesAPI(self)
        self.proforma_invoices = ProFormaInvoicesAPI(self)
        self.worksheets = WorksheetsAPI(self)
        self.webhooks = WebhooksAPI(self)
        print(f"Running in {mode} mode.")
        print(f"API Endpoint: {self.base_url}")

########################################################################################################################
    @staticmethod
    def _init_session(max_retries: int, backoff_factor: float) -> requests.Session():
        """
         Configure a requests session with retries.
        :param max_retries: Maximum number of retries. Defaults to 3.
        :param backoff_factor: Backoff factor for retries. Defaults to 0.3.
        :return: Requests Session
        """
        session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

########################################################################################################################
    def _get_auth_headers(self, existing_headers: dict = None) -> dict:
        """
        Return authorization and default headers.
        Includes 'Accept: application/json' always.
        Only includes 'Content-Type: application/json' if not already provided.
        """
        headers = {
            "X-Talentdesk-Api-Key": self.token,
            "Accept": "application/json"
        }

        # Respect user-supplied Content-Type (e.g., for file uploads)
        if not existing_headers or "Content-Type" not in existing_headers:
            headers["Content-Type"] = "application/json"

        return headers

########################################################################################################################
    def _parse_link_header(self, link_header: str) -> (str, None):
        """
        Parse the 'Link' header to extract the URL with rel="next".
        Rewrites UI URLs to use API base if needed.
        :param link_header: Link header string
        :return: URL for the next page or None
        """
        if not link_header:
            return None

        matches = re.findall(r'<([^>]+)>\s*;\s*rel="?([^";]+)"?', link_header)
        links = {}

        for url, rel in matches:
            url = url.strip()
            rel = rel.strip()

            # Rewrite frontend URL to match API base
            if "app.talentdesk.io" in url and "api.talentdesk.io" in self.base_url:
                url = url.replace("app.talentdesk.io", "api.talentdesk.io")

            links[rel] = url

        return links.get("next")

########################################################################################################################
    def _build_url(self, base_endpoint: str, next_url: str) -> str:
        """
        Build the full request URL based on the next page information.
        :param base_endpoint: The base API endpoint.
        :param next_url: The next page query string or absolute URL.
        :return: Full URL for the next request.
        """
        if next_url.startswith('http'):
            return next_url
        if next_url.startswith('?'):
            return f"{self.base_url}/{base_endpoint}{next_url}"
        return f"{self.base_url}/{next_url.lstrip('/')}"

########################################################################################################################
    def _extract_message(self, response: requests.models.Response) -> str:
        """
        Helper method to gracefully extract messages from API responses
        :param response: API Response
        :return: String containing response message
        """
        try:
            error_info = response.json()
            return (
                    error_info.get("_meta", {}).get("message")
                    or error_info.get("_error", "")
                    or response.reason
            )
        except Exception:
            return response.text[:200] or "An unknown error occurred"

########################################################################################################################
    def _handle_response(self, response: requests.models.Response) -> [list, dict]:
        """
        Normalize API responses and handle errors.
        :param response: API Response
        :return: Normalized Dictionary of results:
        {"success": True/False, "data": json data / None, "error": Error Message / None}
        """
        try:
            response.raise_for_status()
            try:
                json_data = response.json()
            except ValueError:
                return {"success": False, "data": None, "error": "Response was not valid JSON"}

            return {"success": True, "data": json_data, "error": None}

        except requests.exceptions.HTTPError:
            return {"success": False, "data": None, "error": self._extract_message(response)}

        except requests.exceptions.Timeout:
            return {"success": False, "data": None, "error": f"Request to {response.url} timed out after {self.timeout}s"}

        except requests.exceptions.RequestException as err:
            return {"success": False, "data": None, "error": f"Request failed: {err}"}

########################################################################################################################
    def _request(self, method: str, endpoint: str, **kwargs) -> (list, dict):
        """
        Perform an HTTP request and handle pagination using the Link header.
        :param method: HTTP method (GET, POST, PUT, DELETE).
        :param endpoint: API endpoint.
        :param kwargs: Additional arguments for the request.
        :return: list or dict: Aggregated paginated data or a single dictionary response.
        """
        all_data = []
        next_url = endpoint
        base_endpoint = endpoint.lstrip('/').split('?')[0]

        # Send Initial Request
        while next_url:
            url = self._build_url(base_endpoint, next_url)
            headers = kwargs.pop("headers", {})
            headers.update(self._get_auth_headers(headers))
            response = self.session.request(method, url, timeout=self.timeout, headers=headers, **kwargs)
            json_response = self._handle_response(response)

            # Print an error if the response handler fails
            if not json_response.get("success"):
                print(f"[ERROR] {json_response.get('error')}")
                return json_response

            data = json_response
            # Store response and check for additional pages, add each page to all_data
            if isinstance(data, list):
                all_data.extend(data)
                # Extract next page URL from Link header
                link_header = response.headers.get("Link")
                next_url = self._parse_link_header(link_header)
            elif isinstance(data, dict):
                return data
            else:
                break

        return all_data

########################################################################################################################
########################################################################################################################
