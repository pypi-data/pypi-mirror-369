"""API Keys client for ReZEN API."""

from typing import Any, Dict, List, Optional

from .base_client import BaseClient


class ApiKeysClient(BaseClient):
    """Client for API keys management endpoints.

    This client provides access to API key functionality including
    generation, listing, and revocation. Note: This uses the keymaker
    authentication service with a different base URL.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the API keys client.

        Args:
            api_key: API key for authentication. If None, will look for REZEN_API_KEY env var
            base_url: Base URL for the API keys API. Defaults to keymaker production URL
        """
        # Use the keymaker base URL for API keys API
        api_keys_base_url = base_url or "https://keymaker.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=api_keys_base_url)

    def get_api_keys(self) -> List[Dict[str, Any]]:
        """Get all API keys for the current user.

        Returns:
            List of dictionaries containing API key information

        Example:
            ```python
            # Get all API keys
            api_keys = client.api_keys.get_api_keys()
            for key in api_keys:
                print(f"Key ID: {key.get('id')}")
                print(f"Name: {key.get('name')}")
                print(f"Created: {key.get('createdAt')}")
            ```
        """
        # Override the return type since this endpoint returns a list
        response: Any = self.get("api-keys")
        # The API returns a list directly
        if isinstance(response, list):
            return response
        return []

    def generate_api_key(
        self,
        name: str,
        description: Optional[str] = None,
        expires_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a new API key.

        Args:
            name: Name for the API key
            description: Optional description for the API key
            expires_at: Optional expiration date (ISO format)

        Returns:
            Dictionary containing new API key information including the key value

        Raises:
            ValidationError: If request parameters are invalid
            AuthenticationError: If user is not authorized

        Example:
            ```python
            # Generate a new API key
            new_key = client.api_keys.generate_api_key(
                name="Production Key",
                description="API key for production environment"
            )

            # Store the key value securely
            key_value = new_key.get('keyValue')
            key_id = new_key.get('id')
            ```
        """
        key_data = {
            "name": name,
        }

        if description is not None:
            key_data["description"] = description

        if expires_at is not None:
            key_data["expiresAt"] = expires_at

        return self.post("api-keys", json_data=key_data)

    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        """Revoke an API key.

        Args:
            key_id: ID of the API key to revoke

        Returns:
            Dictionary containing revocation confirmation

        Raises:
            NotFoundError: If API key is not found
            AuthenticationError: If user is not authorized

        Example:
            ```python
            # Revoke an API key
            result = client.api_keys.revoke_api_key("key-12345")
            ```
        """
        # According to the API spec, DELETE /api-keys requires request body
        return self._request(
            method="DELETE", endpoint="api-keys", json_data={"keyId": key_id}
        )

    def get_api_key_details(self, key_id: str) -> Dict[str, Any]:
        """Get details of a specific API key.

        Args:
            key_id: ID of the API key to retrieve

        Returns:
            Dictionary containing API key details

        Raises:
            NotFoundError: If API key is not found

        Example:
            ```python
            # Get API key details
            key_details = client.api_keys.get_api_key_details("key-12345")
            print(f"Key name: {key_details.get('name')}")
            print(f"Created: {key_details.get('createdAt')}")
            print(f"Last used: {key_details.get('lastUsedAt')}")
            ```
        """
        # Get all keys and filter for the specific one
        all_keys = self.get_api_keys()
        for key in all_keys:
            if key.get("id") == key_id:
                return key

        # If not found in the list, raise NotFoundError
        from .exceptions import NotFoundError

        raise NotFoundError(f"API key with ID {key_id} not found")

    def update_api_key(
        self,
        key_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an API key's metadata.

        Args:
            key_id: ID of the API key to update
            name: New name for the API key
            description: New description for the API key

        Returns:
            Dictionary containing updated API key information

        Raises:
            NotFoundError: If API key is not found
            ValidationError: If request parameters are invalid

        Example:
            ```python
            # Update API key
            updated_key = client.api_keys.update_api_key(
                key_id="key-12345",
                name="Updated Production Key",
                description="Updated description"
            )
            ```
        """
        update_data = {}

        if name is not None:
            update_data["name"] = name

        if description is not None:
            update_data["description"] = description

        if not update_data:
            raise ValueError(
                "At least one field (name or description) must be provided"
            )

        return self.patch(f"api-keys/{key_id}", json_data=update_data)
