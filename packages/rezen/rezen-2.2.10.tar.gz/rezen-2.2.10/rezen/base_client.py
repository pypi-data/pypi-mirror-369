"""Base client for ReZEN API."""

import os
from typing import Any, Dict, List, Optional, Union

import requests
from dotenv import load_dotenv

from .exceptions import (
    AuthenticationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    RezenError,
    ServerError,
    ValidationError,
)

# Load environment variables
load_dotenv()


class BaseClient:
    """Base client for ReZEN API with common functionality."""

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the base client.

        Args:
            api_key: API key for authentication. If None, will look for
                REZEN_API_KEY env var
            base_url: Base URL for the API. Defaults to production URL
        """
        self.api_key = api_key or os.getenv("REZEN_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key is required. Set REZEN_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.base_url = base_url or "https://arrakis.therealbrokerage.com/api/v1"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            Various RezenError subclasses based on status code
        """
        try:
            response_data: Dict[str, Any] = response.json() if response.content else {}
        except ValueError:
            response_data = {"message": response.text}

        if response.status_code == 200:
            return response_data
        elif response.status_code == 201:
            return response_data
        elif response.status_code == 204:
            return {}
        elif response.status_code == 400:
            error_message = response_data.get("message", "Invalid request")
            # Add more context for common errors
            if "Invalid request" in error_message and "/owner-info" in response.url:
                error_message += (
                    " (Note: Owner agent endpoint requires proper transaction setup. "
                    "See TransactionSequenceError for required steps.)"
                )
            raise ValidationError(
                f"Bad request: {error_message}",
                status_code=400,
                response_data=response_data,
            )
        elif response.status_code == 401:
            message = response_data.get("message", "Invalid credentials")
            raise AuthenticationError(
                f"Authentication failed: {message}",
                status_code=401,
                response_data=response_data,
            )
        elif response.status_code == 404:
            raise NotFoundError(
                f"Resource not found: {response_data.get('message', 'Not found')}",
                status_code=404,
                response_data=response_data,
            )
        elif response.status_code == 429:
            message = response_data.get("message", "Too many requests")
            raise RateLimitError(
                f"Rate limit exceeded: {message}",
                status_code=429,
                response_data=response_data,
            )
        elif 500 <= response.status_code < 600:
            message = response_data.get("message", "Internal server error")
            raise ServerError(
                f"Server error: {message}",
                status_code=response.status_code,
                response_data=response_data,
            )
        else:
            raise RezenError(
                f"Unexpected error: {response_data.get('message', 'Unknown error')}",
                status_code=response.status_code,
                response_data=response_data,
            )

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        files: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Form data to send
            json_data: JSON data to send (can be dict or list)
            files: Files to upload
            params: Query parameters

        Returns:
            Parsed response data

        Raises:
            NetworkError: When network connection fails
            Various RezenError subclasses: Based on response status
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            headers = {}
            if files:
                # Don't set Content-Type for multipart requests, let requests handle it
                headers = {
                    k: v
                    for k, v in self.session.headers.items()
                    if k.lower() != "content-type"
                }

            # Don't send json parameter if files are present
            if files:
                # Create a new request without using session to avoid header conflicts
                import requests as req

                final_headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                    # NO Content-Type - let requests set it for multipart
                }
                response = req.request(
                    method=method,
                    url=url,
                    data=data,
                    files=files,
                    params=params,
                    headers=final_headers,
                )
            else:
                response = self.session.request(
                    method=method,
                    url=url,
                    json=json_data,
                    data=data,
                    params=params,
                )

            return self._handle_response(response)

        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {str(e)}")

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Parsed response data
        """
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make POST request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data to send (can be dict or list)
            data: Form data to send
            files: Files to upload

        Returns:
            Parsed response data
        """
        return self._request(
            "POST", endpoint, json_data=json_data, data=data, files=files
        )

    def put(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PUT request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data to send (can be dict or list)
            data: Form data to send
            files: Files to upload

        Returns:
            Parsed response data
        """
        return self._request(
            "PUT", endpoint, json_data=json_data, data=data, files=files
        )

    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request.

        Args:
            endpoint: API endpoint path

        Returns:
            Parsed response data
        """
        return self._request("DELETE", endpoint)

    def patch(
        self,
        endpoint: str,
        json_data: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make PATCH request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data to send (can be dict or list)
            data: Form data to send
            files: Files to upload

        Returns:
            Parsed response data
        """
        return self._request(
            "PATCH", endpoint, json_data=json_data, data=data, files=files
        )
