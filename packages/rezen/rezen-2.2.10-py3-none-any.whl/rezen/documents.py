"""ReZEN Documents/Signature API client implementation."""

from typing import Any, BinaryIO, Dict, List, Optional

from .base_client import BaseClient


class DocumentClient(BaseClient):
    """
    Client for ReZEN Documents/Signature API endpoints.

    Provides access to document and signature-related functionality including:
    - Uploading documents for signature
    - Managing signature requests
    - Document templates and workflows
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Document/Signature API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the documents API. Defaults to production URL
        """
        super().__init__(api_key=api_key, base_url=base_url)

    def post_document(
        self, data: Dict[str, Any], file: Optional[BinaryIO] = None
    ) -> Dict[str, Any]:
        """
        Post document to signature API.

        Args:
            data: Document metadata including signers, fields, etc.
            file: Document file to upload (optional)

        Returns:
            Dict containing document creation response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "documents"

        if file:
            # If file is provided, use multipart/form-data
            files = {"file": file}
            return self._request("POST", endpoint, data=data, files=files)
        else:
            # Otherwise just send JSON data
            return self.post(endpoint, json_data=data)

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get document details.

        Args:
            document_id: The document ID

        Returns:
            Dict containing document details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}"
        return self.get(endpoint)

    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """
        Get document signature status.

        Args:
            document_id: The document ID

        Returns:
            Dict containing document status

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/status"
        return self.get(endpoint)

    def send_document_for_signature(
        self, document_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send document for signature.

        Args:
            document_id: The document ID
            data: Signature request data including signers

        Returns:
            Dict containing signature request response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/send"
        return self.post(endpoint, json_data=data)

    def cancel_signature_request(self, document_id: str) -> Dict[str, Any]:
        """
        Cancel signature request.

        Args:
            document_id: The document ID

        Returns:
            Dict containing cancellation response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/cancel"
        return self.post(endpoint)

    def remind_signer(
        self, document_id: str, signer_id: str, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send reminder to signer.

        Args:
            document_id: The document ID
            signer_id: The signer ID
            message: Optional reminder message

        Returns:
            Dict containing reminder response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/signers/{signer_id}/remind"
        data = {"message": message} if message else {}
        return self.post(endpoint, json_data=data)

    def download_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get download URL for document.

        Args:
            document_id: The document ID

        Returns:
            Dict containing download URL

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/download"
        return self.get(endpoint)

    def get_audit_trail(self, document_id: str) -> Dict[str, Any]:
        """
        Get document audit trail.

        Args:
            document_id: The document ID

        Returns:
            Dict containing audit trail

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/audit-trail"
        return self.get(endpoint)

    def get_document_templates(
        self, page_number: int = 0, page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get available document templates.

        Args:
            page_number: Page number for pagination
            page_size: Page size for pagination

        Returns:
            Dict containing document templates

        Raises:
            RezenError: If the API request fails
        """
        params = {"pageNumber": page_number, "pageSize": page_size}
        return self.get("documents/templates", params=params)

    def create_document_from_template(
        self, template_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create document from template.

        Args:
            template_id: The template ID
            data: Document creation data

        Returns:
            Dict containing created document

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/templates/{template_id}/create"
        return self.post(endpoint, json_data=data)

    def bulk_send_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk send multiple documents for signature.

        Args:
            documents: List of document data

        Returns:
            Dict containing bulk send response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "documents/bulk-send"
        return self.post(endpoint, json_data={"documents": documents})

    def get_signer_link(self, document_id: str, signer_id: str) -> Dict[str, Any]:
        """
        Get signing link for specific signer.

        Args:
            document_id: The document ID
            signer_id: The signer ID

        Returns:
            Dict containing signing link

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"documents/{document_id}/signers/{signer_id}/link"
        return self.get(endpoint)


# Alias for backward compatibility
SignatureClient = DocumentClient
