"""ReZEN Dropbox API client implementation."""

from typing import Any, BinaryIO, Dict, List, Optional, Union

from .base_client import BaseClient
from .exceptions import RezenError, ValidationError


class DropboxClient(BaseClient):
    """
    Client for ReZEN Dropbox API endpoints.

    Provides access to Dropbox integration functionality including:
    - OAuth authentication flow
    - Folder management
    - File uploads
    - Token management
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Dropbox API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the API. Defaults to production URL
        """
        super().__init__(api_key=api_key, base_url=base_url)
        # Override base URL for Dropbox endpoints which use sherlock domain
        if base_url is None:
            self.base_url = "https://sherlock.therealbrokerage.com/api/v1"

    def get_auth_url(self) -> Dict[str, Any]:
        """
        Get Dropbox OAuth authentication URL.

        This endpoint returns the URL that should be used to initiate
        the Dropbox OAuth flow for an agent.

        Returns:
            Dict containing the authentication URL:
                {
                    "url": "string"
                }

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "dropbox/auth-url"
        return self.get(endpoint)

    def save_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange OAuth code for Dropbox token and save it for the agent.

        This endpoint completes the OAuth flow by exchanging the authorization
        code for an access token and storing it for future use.

        Args:
            code: The authorization code received from Dropbox OAuth callback

        Returns:
            Empty dict on success (200 OK)

        Raises:
            ValidationError: If the code is invalid
            RezenError: If the API request fails
        """
        if not code or not code.strip():
            raise ValidationError("Authorization code is required")

        endpoint = "dropbox/token"
        data = {"code": code}
        return self.post(endpoint, json_data=data)

    def get_folders(
        self, agent_id: str, path: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user folders from Dropbox.

        Retrieves a list of folders from the agent's connected Dropbox account.

        Args:
            agent_id: UUID of the agent
            path: Optional path to list folders from. If not provided,
                  lists folders from the root directory

        Returns:
            List of folder dictionaries, each containing:
                {
                    "name": "string",
                    "path": "string"
                }

        Raises:
            ValidationError: If the agent_id is invalid
            RezenError: If the API request fails
        """
        if not agent_id:
            raise ValidationError("Agent ID is required")

        endpoint = f"dropbox/{agent_id}/folders"
        params: Dict[str, Any] = {}
        if path:
            params["path"] = path

        response = self.get(endpoint, params=params if params else None)

        # The API returns an array according to the schema, but base client types it as Dict
        # Cast to the expected list type
        return response  # type: ignore[return-value]

    def upload_file(self, agent_id: str, file: BinaryIO, path: str) -> Dict[str, Any]:
        """
        Upload a file to Dropbox.

        Uploads a file to the specified path in the agent's Dropbox account.

        Args:
            agent_id: UUID of the agent
            file: File-like object to upload (opened in binary mode)
            path: Dropbox path where the file should be uploaded

        Returns:
            Empty dict on success (200 OK)

        Raises:
            ValidationError: If required parameters are invalid
            RezenError: If the API request fails

        Example:
            with open('document.pdf', 'rb') as f:
                client.upload_file(agent_id, f, '/transactions/document.pdf')
        """
        if not agent_id:
            raise ValidationError("Agent ID is required")
        if not file:
            raise ValidationError("File is required")
        if not path:
            raise ValidationError("Path is required")

        endpoint = f"dropbox/{agent_id}/files"

        # Prepare multipart form data
        files = {"file": file}
        data = {"path": path}

        return self.post(endpoint, data=data, files=files)

    def create_folder(self, agent_id: str, path: str) -> Dict[str, Any]:
        """
        Create a new folder in Dropbox.

        Creates a new folder at the specified path in the agent's Dropbox account.

        Args:
            agent_id: UUID of the agent
            path: Path of the folder to create in Dropbox

        Returns:
            Empty dict on success (200 OK)

        Raises:
            ValidationError: If required parameters are invalid
            RezenError: If the API request fails

        Example:
            client.create_folder(agent_id, '/transactions/2024/january')
        """
        if not agent_id:
            raise ValidationError("Agent ID is required")
        if not path:
            raise ValidationError("Path is required")

        endpoint = f"dropbox/{agent_id}/folders"
        data = {"path": path}
        return self.post(endpoint, json_data=data)
