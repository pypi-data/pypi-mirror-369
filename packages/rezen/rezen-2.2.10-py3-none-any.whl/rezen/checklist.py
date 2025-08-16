"""ReZEN Checklist API client implementation."""

import re
from typing import Any, BinaryIO, Dict, List, Optional, Union

from .base_client import BaseClient
from .exceptions import ValidationError


def _validate_uuid(value: str, field_name: str) -> None:
    """Validate that a string is a valid UUID format.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Raises:
        ValidationError: If the value is not a valid UUID format
    """
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )
    if not uuid_pattern.match(value):
        raise ValidationError(f"{field_name} must be a valid UUID format, got: {value}")


class ChecklistClient(BaseClient):
    """
    Client for ReZEN Checklist API endpoints.

    Provides access to checklist-related functionality including:
    - Managing checklists and checklist items
    - Document upload and management
    - Checklist progress tracking
    - Batch operations

    Document Upload Approaches:
        There are two ways to upload documents to checklist items:

        1. Direct Upload (using add_document_to_checklist_item):
           - Use when the transaction doesn't have Dropbox integration
           - Uploads directly to the checklist item
           - Requires: name, description, uploader_id, transaction_id, file
           - May fail with 403 if user is not a participant on the transaction

        2. Dropbox Upload (two-step process):
           - Use when transaction has a dropboxId
           - Step 1: Upload to transaction's Dropbox storage
             POST https://dropbox.therealbrokerage.com/api/v1/dropboxes/{dropboxId}/files
           - Step 2: Link the uploaded file to the checklist item
             POST /checklists/checklist-items/{checklistItemId}/file-references
           - See examples/upload_to_checklist_via_dropbox.py for implementation

        Note: The upload approach depends on the transaction configuration.
        Check if transaction has 'dropboxId' field to determine which method to use.
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Checklist API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the checklist API. Defaults to sherlock production URL
        """
        # Use the sherlock base URL for checklist API
        checklist_base_url = base_url or "https://sherlock.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=checklist_base_url)

    def get_checklist_item(self, checklist_item_id: str) -> Dict[str, Any]:
        """
        Get checklist item for given ID.

        Args:
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing checklist item details

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}"
        return self.get(endpoint)

    def update_checklist_item(
        self, checklist_item_id: str, item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update checklist item for given checklist item ID.

        Args:
            checklist_item_id: The checklist item ID
            item_data: Item data including item details

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}"
        return self.put(endpoint, json_data=item_data)

    def delete_checklist_item(self, checklist_item_id: str) -> Dict[str, Any]:
        """
        Delete checklist item for given ID.

        Args:
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing deletion status and message

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}"
        return self.delete(endpoint)

    def complete_checklist_item(
        self, checklist_item_id: str, is_complete: bool = True
    ) -> Dict[str, Any]:
        """
        Mark checklist item as complete or incomplete.

        Args:
            checklist_item_id: The checklist item ID
            is_complete: Whether to mark as complete (default: True)

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}/complete?isComplete={is_complete}"
        return self.put(endpoint)

    def get_checklist_document(self, document_id: str) -> Dict[str, Any]:
        """
        Get document for the given ID.

        Args:
            document_id: The document ID

        Returns:
            Dict containing document details including versions

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{document_id}"
        return self.get(endpoint)

    def update_checklist_document(
        self, document_id: str, document_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update current version for the given document ID.

        Args:
            document_id: The document ID
            document_data: Document data including versions and current version

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{document_id}"
        return self.put(endpoint, json_data=document_data)

    def delete_checklist_document(self, document_id: str) -> Dict[str, Any]:
        """
        Delete the given document ID.

        Args:
            document_id: The document ID

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/{document_id}"
        return self.delete(endpoint)

    def create_checklist_item(
        self, checklist_id: str, item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create checklist item for given checklist ID.

        Args:
            checklist_id: The checklist ID
            item_data: Item data including item details

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}/items"
        return self.post(endpoint, json_data=item_data)

    def create_checklist(
        self, checklist_definition_id: str, checklist_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create checklist for given checklist definition ID.

        Args:
            checklist_definition_id: The checklist definition ID
            checklist_data: Checklist creation data including parent info and assignees

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_definition_id}"
        return self.post(endpoint, json_data=checklist_data)

    def add_document_to_checklist_item(
        self,
        checklist_item_id: str,
        name: str,
        description: str,
        uploader_id: str,
        transaction_id: str,
        file: BinaryIO,
    ) -> Dict[str, Any]:
        """
        Add a new document to the given checklist item ID.

        Note: This method uploads directly to the checklist item. If the transaction
        uses Dropbox storage (has a dropboxId), you may need to use the two-step
        Dropbox upload approach instead. See examples/upload_to_checklist_via_dropbox.py

        Args:
            checklist_item_id: The checklist item ID (must be valid UUID)
            name: Document name (required)
            description: Document description (required)
            uploader_id: ID of the user uploading the document (must be valid UUID)
            transaction_id: Transaction ID (must be valid UUID)
            file: File to upload (required - must be opened in binary mode)

        Returns:
            Dict containing document details

        Raises:
            ValidationError: If required parameters are missing or invalid format
            RezenError: If the API request fails (403 if user not a participant)

        Example:
            >>> with open('document.pdf', 'rb') as f:
            ...     result = client.add_document_to_checklist_item(
            ...         checklist_item_id='550e8400-e29b-41d4-a716-446655440000',
            ...         name='MLS Sheet',
            ...         description='Property MLS information',
            ...         uploader_id='123e4567-e89b-12d3-a456-426614174000',
            ...         transaction_id='987fcdeb-51d2-4321-b789-123456789012',
            ...         file=f
            ...     )
        """
        # Validate required parameters
        if not name or not name.strip():
            raise ValidationError("Document name is required and cannot be empty")

        if not description or not description.strip():
            raise ValidationError(
                "Document description is required and cannot be empty"
            )

        if not checklist_item_id or not checklist_item_id.strip():
            raise ValidationError("Checklist item ID is required and cannot be empty")

        if not uploader_id or not uploader_id.strip():
            raise ValidationError("Uploader ID is required and cannot be empty")

        if not transaction_id or not transaction_id.strip():
            raise ValidationError("Transaction ID is required and cannot be empty")

        if file is None:
            raise ValidationError(
                "File is required for document upload. Please provide a file opened in binary mode (e.g., open('file.pdf', 'rb'))"
            )

        # Validate UUID formats
        try:
            _validate_uuid(checklist_item_id.strip(), "checklist_item_id")
            _validate_uuid(uploader_id.strip(), "uploader_id")
            _validate_uuid(transaction_id.strip(), "transaction_id")
        except ValidationError as e:
            raise ValidationError(f"Invalid parameter format: {e}")

        endpoint = f"checklists/checklist-items/{checklist_item_id.strip()}/documents"

        # Prepare form data exactly as specified in OpenAPI schema
        data = {
            "name": name.strip(),
            "description": description.strip(),
            "uploaderId": uploader_id.strip(),  # API expects camelCase
            "transactionId": transaction_id.strip(),  # API expects camelCase
        }

        files = {"file": file}

        try:
            return self._request("POST", endpoint, data=data, files=files)
        except ValidationError as e:
            # Add more context to validation errors
            error_msg = f"Document upload failed: {str(e)}"
            if "Bad request" in str(e):
                error_msg += (
                    "\n\nDebugging checklist:\n"
                    f"- Checklist Item ID: {checklist_item_id} (valid UUID: {bool(re.match(r'^[0-9a-f-]{36}$', checklist_item_id, re.I))})\n"
                    f"- Uploader ID: {uploader_id} (valid UUID: {bool(re.match(r'^[0-9a-f-]{36}$', uploader_id, re.I))})\n"
                    f"- Transaction ID: {transaction_id} (valid UUID: {bool(re.match(r'^[0-9a-f-]{36}$', transaction_id, re.I))})\n"
                    f"- Document name: '{name}' (length: {len(name)})\n"
                    f"- Description: '{description}' (length: {len(description)})\n"
                    f"- File provided: {file is not None}\n"
                    f"- File readable: {hasattr(file, 'read') if file else False}\n"
                    "\nCommon issues:\n"
                    "1. Ensure all IDs are valid UUIDs (36 characters with dashes)\n"
                    "2. Ensure the file is opened in binary mode: open('file.pdf', 'rb')\n"
                    "3. Ensure the uploader has permission to upload to this checklist item\n"
                    "4. Ensure the transaction_id is associated with the checklist"
                )
            raise ValidationError(error_msg)

    def add_document_version(
        self,
        checklist_document_id: str,
        name: str,
        description: str,
        uploader_id: str,
        transaction_id: str,
        file: BinaryIO,
    ) -> Dict[str, Any]:
        """
        Add a new version for given document ID.

        Args:
            checklist_document_id: The checklist document ID (must be valid UUID)
            name: Version name (required)
            description: Version description (required)
            uploader_id: ID of the user uploading the version (must be valid UUID)
            transaction_id: Transaction ID (must be valid UUID)
            file: File to upload (required - must be opened in binary mode)

        Returns:
            Dict containing version details

        Raises:
            ValidationError: If required parameters are missing or invalid format
            RezenError: If the API request fails
        """
        # Validate required parameters
        if not name or not name.strip():
            raise ValidationError("Version name is required and cannot be empty")

        if not description or not description.strip():
            raise ValidationError("Version description is required and cannot be empty")

        if not checklist_document_id or not checklist_document_id.strip():
            raise ValidationError(
                "Checklist document ID is required and cannot be empty"
            )

        if not uploader_id or not uploader_id.strip():
            raise ValidationError("Uploader ID is required and cannot be empty")

        if not transaction_id or not transaction_id.strip():
            raise ValidationError("Transaction ID is required and cannot be empty")

        if file is None:
            raise ValidationError(
                "File is required for document version upload. Please provide a file opened in binary mode (e.g., open('file.pdf', 'rb'))"
            )

        # Validate UUID formats
        try:
            _validate_uuid(checklist_document_id.strip(), "checklist_document_id")
            _validate_uuid(uploader_id.strip(), "uploader_id")
            _validate_uuid(transaction_id.strip(), "transaction_id")
        except ValidationError as e:
            raise ValidationError(f"Invalid parameter format: {e}")

        endpoint = (
            f"checklists/checklist-documents/{checklist_document_id.strip()}/versions"
        )

        # Prepare form data exactly as specified in OpenAPI schema
        data = {
            "name": name.strip(),
            "description": description.strip(),
            "uploaderId": uploader_id.strip(),  # API expects camelCase
            "transactionId": transaction_id.strip(),  # API expects camelCase
        }

        files = {"file": file}

        try:
            return self._request("POST", endpoint, data=data, files=files)
        except ValidationError as e:
            # Add more context to validation errors
            error_msg = f"Document version upload failed: {str(e)}"
            if "Bad request" in str(e):
                error_msg += (
                    "\n\nDebugging checklist:\n"
                    f"- Document ID: {checklist_document_id} (valid UUID: {bool(re.match(r'^[0-9a-f-]{36}$', checklist_document_id, re.I))})\n"
                    f"- Uploader ID: {uploader_id} (valid UUID: {bool(re.match(r'^[0-9a-f-]{36}$', uploader_id, re.I))})\n"
                    f"- Transaction ID: {transaction_id} (valid UUID: {bool(re.match(r'^[0-9a-f-]{36}$', transaction_id, re.I))})\n"
                    f"- Version name: '{name}' (length: {len(name)})\n"
                    f"- Description: '{description}' (length: {len(description)})\n"
                    f"- File provided: {file is not None}\n"
                    f"- File readable: {hasattr(file, 'read') if file else False}"
                )
            raise ValidationError(error_msg)

    def batch_update_checklists(
        self, batch_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Update all checklists with the given IDs.

        Args:
            batch_items: List of items with checklistId and patch data

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "checklists/batch-update"
        data = {"items": batch_items}
        return self.post(endpoint, json_data=data)

    def get_checklist(self, checklist_id: str) -> Dict[str, Any]:
        """
        Get checklist for given ID.

        Args:
            checklist_id: The checklist ID

        Returns:
            Dict containing checklist details and items

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/{checklist_id}"
        return self.get(endpoint)

    def get_checklists_progress(self, checklist_ids: List[str]) -> Dict[str, Any]:
        """
        Get checklists progress for given checklist IDs.

        Args:
            checklist_ids: List of checklist IDs

        Returns:
            Dict containing progress information (API returns array in 'data' field)

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "checklists/progress"
        params = {"checklistIds": checklist_ids}
        return self.get(endpoint, params=params)

    def download_document_version(self, version_id: str) -> Dict[str, Any]:
        """
        Get the download URL for a document version.

        Args:
            version_id: The version ID

        Returns:
            Dict containing the download URL (response will be processed by base client)

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/checklist-documents/versions/{version_id}/download"
        return self.get(endpoint)

    def link_file_to_checklist_item(
        self, checklist_item_id: str, file_references: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Link files uploaded to Dropbox to a checklist item.

        This is the second step of the Dropbox upload approach. After uploading
        files to the transaction's Dropbox, use this method to link them to
        the checklist item.

        Args:
            checklist_item_id: The checklist item ID to link files to
            file_references: List of file references, each containing:
                - fileId: The ID returned from Dropbox upload
                - filename: The filename for display

        Returns:
            Dict containing the API response

        Raises:
            RezenError: If the API request fails

        Example:
            >>> # After uploading to Dropbox and getting file_id
            >>> references = [{
            ...     "fileId": "4bd8d903-fda2-42ee-ba3e-8aa953b7c796",
            ...     "filename": "MLS_Sheet.pdf"
            >>> }]
            >>> result = client.checklist.link_file_to_checklist_item(
            ...     checklist_item_id="b0bce9b2-dfe9-4668-a1ae-7841a8929f3a",
            ...     file_references=references
            ... )
        """
        endpoint = f"checklists/checklist-items/{checklist_item_id}/file-references"
        data = {"references": file_references}
        return self.post(endpoint, json_data=data)

    # Legacy methods for backward compatibility
    def post_document_to_checklist(
        self,
        checklist_item_id: str,
        data: Dict[str, Any],
        file: BinaryIO,
    ) -> Dict[str, Any]:
        """
        Upload document to checklist item (legacy method).

        Args:
            checklist_item_id: The checklist item ID to upload to
            data: Document metadata (must include name, description, uploaderId, transactionId)
            file: File to upload (required - must be opened in binary mode)

        Returns:
            Dict containing upload response

        Raises:
            ValidationError: If required fields are missing from data
            RezenError: If the API request fails
        """
        # Validate required fields in data dict
        required_fields = ["name", "description", "uploaderId", "transactionId"]
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields in data: {missing_fields}. "
                f"Required fields: {required_fields}"
            )

        return self.add_document_to_checklist_item(
            checklist_item_id=checklist_item_id,
            name=data["name"],
            description=data["description"],
            uploader_id=data["uploaderId"],
            transaction_id=data["transactionId"],
            file=file,
        )

    def mark_checklist_item_complete(
        self, checklist_id: str, checklist_item_id: str
    ) -> Dict[str, Any]:
        """
        Mark checklist item as complete (legacy method).

        Args:
            checklist_id: The checklist ID (not used in new API)
            checklist_item_id: The checklist item ID

        Returns:
            Dict containing updated checklist item

        Raises:
            RezenError: If the API request fails
        """
        return self.complete_checklist_item(checklist_item_id, is_complete=True)

    def delete_checklist_item_document(
        self, checklist_item_id: str, document_id: str
    ) -> Dict[str, Any]:
        """
        Delete document from checklist item (legacy method).

        Args:
            checklist_item_id: The checklist item ID (not used in new API)
            document_id: The document ID to delete

        Returns:
            Dict containing deletion response

        Raises:
            RezenError: If the API request fails
        """
        return self.delete_checklist_document(document_id)

    def get_checklist_templates(self) -> Dict[str, Any]:
        """
        Get available checklist templates (legacy method).

        Returns:
            Dict containing checklist templates

        Raises:
            RezenError: If the API request fails
        """
        endpoint = "checklists/templates"
        return self.get(endpoint)

    def create_checklist_from_template(
        self, template_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new checklist from a template (legacy method).

        Args:
            template_id: The template ID to use
            data: Checklist creation data

        Returns:
            Dict containing created checklist

        Raises:
            RezenError: If the API request fails
        """
        endpoint = f"checklists/templates/{template_id}/create"
        return self.post(endpoint, json_data=data)
