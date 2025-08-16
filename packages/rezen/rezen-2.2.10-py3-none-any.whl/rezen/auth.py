"""Authentication client for ReZEN API."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class AuthClient(BaseClient):
    """Client for authentication API endpoints.

    This client provides access to authentication functionality including
    login, logout, and password management. Note: This uses the keymaker
    authentication service with a different base URL.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the authentication client.

        Args:
            api_key: API key for authentication. If None, will look for REZEN_API_KEY env var
            base_url: Base URL for the auth API. Defaults to keymaker production URL
        """
        # Use the keymaker base URL for authentication API
        auth_base_url = base_url or "https://keymaker.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=auth_base_url)

    def signin(
        self,
        username: str,
        password: str,
        app_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sign in a user with username and password.

        Args:
            username: User's username or email address
            password: User's password
            app_name: Optional application name header (X-real-app-name)

        Returns:
            Dictionary containing JWT authentication response with access token

        Raises:
            AuthenticationError: If credentials are invalid
            ValidationError: If request parameters are invalid

        Example:
            ```python
            # Sign in with username and password
            response = client.auth.signin(
                username="user@example.com",
                password="secure_password"
            )

            # Access token for API requests
            access_token = response['accessToken']
            ```
        """
        headers = {}
        if app_name:
            headers["X-real-app-name"] = app_name

        login_data = {
            "username": username,
            "password": password,
        }

        # Temporarily clear authorization header for login request
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        try:
            if headers:
                # Update session headers temporarily
                original_headers = dict(self.session.headers)
                self.session.headers.update(headers)
                response = self.post("auth/signin", json_data=login_data)
                self.session.headers.clear()
                self.session.headers.update(original_headers)
            else:
                response = self.post("auth/signin", json_data=login_data)
        finally:
            # Restore authorization header
            if original_auth:
                self.session.headers["Authorization"] = original_auth

        return response

    def signout(self) -> Dict[str, Any]:
        """Sign out the current user.

        Returns:
            Dictionary containing sign out confirmation

        Example:
            ```python
            # Sign out current user
            result = client.auth.signout()
            ```
        """
        return self.post("auth/signout")

    def update_password(
        self,
        current_password: str,
        new_password: str,
        app_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the current user's password.

        Args:
            current_password: User's current password
            new_password: New password to set
            app_name: Optional application name header (X-real-app-name)

        Returns:
            Dictionary containing password update confirmation

        Raises:
            AuthenticationError: If current password is invalid
            ValidationError: If new password doesn't meet requirements

        Example:
            ```python
            # Update password
            result = client.auth.update_password(
                current_password="old_password",
                new_password="new_secure_password"
            )
            ```
        """
        headers = {}
        if app_name:
            headers["X-real-app-name"] = app_name

        password_data = {
            "currentPassword": current_password,
            "newPassword": new_password,
        }

        if headers:
            # Update session headers temporarily
            original_headers = dict(self.session.headers)
            self.session.headers.update(headers)
            response = self.post("auth/updatepassword", json_data=password_data)
            self.session.headers.clear()
            self.session.headers.update(original_headers)
            return response
        else:
            return self.post("auth/updatepassword", json_data=password_data)

    def reset_password(
        self,
        email: str,
        new_password: str,
        reset_token: str,
    ) -> Dict[str, Any]:
        """Reset password using reset token.

        Args:
            email: User's email address
            new_password: New password to set
            reset_token: Password reset token received via email

        Returns:
            Dictionary containing password reset confirmation

        Raises:
            AuthenticationError: If reset token is invalid or expired
            ValidationError: If new password doesn't meet requirements

        Example:
            ```python
            # Reset password with token
            result = client.auth.reset_password(
                email="user@example.com",
                new_password="new_secure_password",
                reset_token="reset_token_from_email"
            )
            ```
        """
        reset_data = {
            "email": email,
            "newPassword": new_password,
            "resetToken": reset_token,
        }

        return self.post("auth/resetpassword", json_data=reset_data)

    def change_password(
        self,
        username: str,
        new_password: str,
        reset_token: str,
    ) -> Dict[str, Any]:
        """Change password (typically for password reset flows).

        Args:
            username: Username or email address
            new_password: New password to set
            reset_token: Token for password change authorization

        Returns:
            Dictionary containing password change confirmation

        Raises:
            AuthenticationError: If token is invalid
            ValidationError: If password doesn't meet requirements

        Example:
            ```python
            # Change password with token
            result = client.auth.change_password(
                username="user@example.com",
                new_password="new_secure_password",
                reset_token="change_token"
            )
            ```
        """
        change_data = {
            "username": username,
            "newPassword": new_password,
            "resetToken": reset_token,
        }

        # This endpoint doesn't require authentication
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        try:
            response = self.post("auth/changepassword", json_data=change_data)
        finally:
            # Restore authorization header
            if original_auth:
                self.session.headers["Authorization"] = original_auth

        return response

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and exchange an auth token.

        Args:
            token: Authentication token to verify

        Returns:
            Dictionary containing user principal information

        Example:
            ```python
            # Verify auth token
            user_info = client.auth.verify_token("auth_token")
            ```
        """
        # This endpoint doesn't require authentication
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        try:
            response = self.get(f"auth/verify/{token}")
        finally:
            # Restore authorization header
            if original_auth:
                self.session.headers["Authorization"] = original_auth

        return response

    def check_username_availability(self, username: str) -> Dict[str, Any]:
        """Check if a username is available.

        Args:
            username: Username to check availability

        Returns:
            Dictionary containing availability status

        Example:
            ```python
            # Check username availability
            availability = client.auth.check_username_availability("new_username")
            is_available = availability.get('available', False)
            ```
        """
        params = {"username": username}

        # This endpoint doesn't require authentication
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        try:
            response = self.get("auth/checkusernameavailability", params=params)
        finally:
            # Restore authorization header
            if original_auth:
                self.session.headers["Authorization"] = original_auth

        return response

    def check_email_availability(self, email: str) -> Dict[str, Any]:
        """Check if an email address is available.

        Args:
            email: Email address to check availability

        Returns:
            Dictionary containing availability status

        Example:
            ```python
            # Check email availability
            availability = client.auth.check_email_availability("user@example.com")
            is_available = availability.get('available', False)
            ```
        """
        params = {"email": email}

        # This endpoint doesn't require authentication
        original_auth = self.session.headers.get("Authorization")
        if "Authorization" in self.session.headers:
            del self.session.headers["Authorization"]

        try:
            response = self.get("auth/checkemailavailability", params=params)
        finally:
            # Restore authorization header
            if original_auth:
                self.session.headers["Authorization"] = original_auth

        return response

    def get_current_user(self) -> Dict[str, Any]:
        """Get current authenticated user information.

        Returns:
            Dictionary containing current user's identity summary

        Example:
            ```python
            # Get current user info
            user = client.auth.get_current_user()
            print(f"User ID: {user.get('id')}")
            print(f"Username: {user.get('username')}")
            ```
        """
        return self.get("keymaker/myself")

    def get_user_identity(self, user_id: str) -> Dict[str, Any]:
        """Get user's login information by ID.

        Args:
            user_id: User ID to retrieve information for

        Returns:
            Dictionary containing user's identity summary

        Example:
            ```python
            # Get user identity by ID
            user = client.auth.get_user_identity("user_id")
            ```
        """
        return self.get(f"users/{user_id}")
