"""Multi-Factor Authentication client for ReZEN API."""

from typing import Any, Dict, Optional

from .base_client import BaseClient


class MfaClient(BaseClient):
    """Client for multi-factor authentication API endpoints.

    This client provides access to MFA functionality including MFA login,
    setup, and SMS management. Note: This uses the keymaker authentication
    service with a different base URL.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """Initialize the MFA client.

        Args:
            api_key: API key for authentication. If None, will look for REZEN_API_KEY env var
            base_url: Base URL for the MFA API. Defaults to keymaker production URL
        """
        # Use the keymaker base URL for MFA API
        mfa_base_url = base_url or "https://keymaker.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=mfa_base_url)

    def signin_with_mfa(
        self,
        username: str,
        mfa_code: str,
        app_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Sign in with multi-factor authentication code.

        Args:
            username: User's username or email address
            mfa_code: Multi-factor authentication code
            app_name: Optional application name header (X-real-app-name)

        Returns:
            Dictionary containing JWT authentication response with access token

        Raises:
            AuthenticationError: If MFA code is invalid
            ValidationError: If request parameters are invalid

        Example:
            ```python
            # Sign in with MFA code
            response = client.mfa.signin_with_mfa(
                username="user@example.com",
                mfa_code="123456"
            )

            # Access token for API requests
            access_token = response['accessToken']
            ```
        """
        headers = {}
        if app_name:
            headers["X-real-app-name"] = app_name

        mfa_data = {
            "username": username,
            "mfaCode": mfa_code,
        }

        if headers:
            # Update session headers temporarily
            original_headers = dict(self.session.headers)
            self.session.headers.update(headers)
            response = self.post("mfa/signin-with-mfa", json_data=mfa_data)
            self.session.headers.clear()
            self.session.headers.update(original_headers)
            return response
        else:
            return self.post("mfa/signin-with-mfa", json_data=mfa_data)

    def enable_mfa(
        self,
        secret_key: str,
        verification_code: str,
    ) -> Dict[str, Any]:
        """Enable multi-factor authentication.

        Args:
            secret_key: MFA secret key for authenticator app
            verification_code: Verification code from authenticator app

        Returns:
            Dictionary containing MFA enablement confirmation

        Raises:
            AuthenticationError: If verification code is invalid
            ValidationError: If request parameters are invalid

        Example:
            ```python
            # Enable MFA
            result = client.mfa.enable_mfa(
                secret_key="JBSWY3DPEHPK3PXP",
                verification_code="123456"
            )
            ```
        """
        mfa_data = {
            "secretKey": secret_key,
            "verificationCode": verification_code,
        }

        return self.post("mfa/enable-mfa", json_data=mfa_data)

    def enable_mfa_and_signin(
        self,
        secret_key: str,
        verification_code: str,
        app_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Enable multi-factor authentication and sign in.

        Args:
            secret_key: MFA secret key for authenticator app
            verification_code: Verification code from authenticator app
            app_name: Optional application name header (X-real-app-name)

        Returns:
            Dictionary containing JWT authentication response with access token

        Raises:
            AuthenticationError: If verification code is invalid
            ValidationError: If request parameters are invalid

        Example:
            ```python
            # Enable MFA and sign in
            response = client.mfa.enable_mfa_and_signin(
                secret_key="JBSWY3DPEHPK3PXP",
                verification_code="123456"
            )

            # Access token for API requests
            access_token = response['accessToken']
            ```
        """
        headers = {}
        if app_name:
            headers["X-real-app-name"] = app_name

        mfa_data = {
            "secretKey": secret_key,
            "verificationCode": verification_code,
        }

        if headers:
            # Update session headers temporarily
            original_headers = dict(self.session.headers)
            self.session.headers.update(headers)
            response = self.post("mfa/enable-mfa-and-signin", json_data=mfa_data)
            self.session.headers.clear()
            self.session.headers.update(original_headers)
            return response
        else:
            return self.post("mfa/enable-mfa-and-signin", json_data=mfa_data)

    def send_mfa_sms(self, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """Send multi-factor authentication code to phone via SMS.

        Args:
            phone_number: Phone number to send SMS to (optional)

        Returns:
            Dictionary containing SMS send confirmation

        Example:
            ```python
            # Send MFA code to default phone
            result = client.mfa.send_mfa_sms()

            # Send MFA code to specific phone
            result = client.mfa.send_mfa_sms(phone_number="+1234567890")
            ```
        """
        params = {}
        if phone_number is not None:
            params["phoneNumber"] = phone_number

        return self.get("mfa/send-mfa-sms", params=params)

    def get_mfa_qr_code(self) -> Dict[str, Any]:
        """Get Authenticator QR code for MFA setup.

        Returns:
            Dictionary containing QR code information

        Example:
            ```python
            # Get QR code for MFA setup
            qr_response = client.mfa.get_mfa_qr_code()
            ```
        """
        return self.get("mfa/mfa-qr-code")

    def get_mfa_status(self) -> Dict[str, Any]:
        """Get current MFA status information.

        Returns:
            Dictionary containing MFA status details

        Example:
            ```python
            # Get MFA status
            status = client.mfa.get_mfa_status()
            is_enabled = status.get('enabled', False)
            ```
        """
        return self.get("mfa")
