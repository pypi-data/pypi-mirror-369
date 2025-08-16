"""Directory client for ReZEN API."""

from enum import Enum
from typing import Any, BinaryIO, Dict, List, Optional, Union

from .base_client import BaseClient
from .enums import Country, StateOrProvince


class DirectoryEntryType(Enum):
    """Directory entry types."""

    VENDOR = "VENDOR"
    PERSON = "PERSON"


class DirectoryRole(Enum):
    """Directory roles."""

    CLIENT = "CLIENT"
    LANDLORD = "LANDLORD"
    TENANT = "TENANT"
    TITLE_ESCROW = "TITLE_ESCROW"
    LENDER = "LENDER"
    LAWYER = "LAWYER"
    TRUSTEE = "TRUSTEE"
    OTHER_AGENT = "OTHER_AGENT"
    VENDOR = "VENDOR"
    REFERRAL = "REFERRAL"
    OTHER = "OTHER"


class VendorSortField(Enum):
    """Vendor sort fields."""

    NAME = "NAME"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    CITY = "CITY"
    STATE_OR_PROVINCE = "STATE_OR_PROVINCE"
    STATUS = "STATUS"


class PersonSortField(Enum):
    """Person sort fields."""

    FIRST_NAME = "FIRST_NAME"
    LAST_NAME = "LAST_NAME"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    IS_PUBLIC = "IS_PUBLIC"


class DirectoryEntrySortField(Enum):
    """Directory entry sort fields."""

    NAME = "NAME"
    NAME_LOGICAL = "NAME_LOGICAL"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"
    PHONE_NUMBER = "PHONE_NUMBER"
    CITY = "CITY"
    STATE_OR_PROVINCE = "STATE_OR_PROVINCE"
    STATUS = "STATUS"


class DirectoryClient(BaseClient):
    """
    Client for ReZEN Directory API endpoints.

    Provides access to directory functionality including:
    - Vendor management (create, update, search, archive)
    - Person management (create, update, search, link/unlink)
    - Directory entry search across vendors and persons
    - Role management and W9 file handling
    """

    def __init__(
        self, api_key: Optional[str] = None, base_url: Optional[str] = None
    ) -> None:
        """
        Initialize the Directory API client.

        Args:
            api_key: ReZEN API key for authentication
            base_url: Base URL for the directory API. Defaults to yenta production URL
        """
        # Use the yenta base URL for directory API
        directory_base_url = base_url or "https://yenta.therealbrokerage.com/api/v1"
        super().__init__(api_key=api_key, base_url=directory_base_url)

    # ===== VENDOR ENDPOINTS =====

    def create_vendor(self, vendor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a vendor.

        Args:
            vendor_data: Vendor creation data

        Returns:
            Created vendor response data

        Raises:
            RezenError: If the API request fails
        """
        return self.post("directory/vendors", json_data=vendor_data)

    def get_vendor(self, vendor_id: str) -> Dict[str, Any]:
        """
        Get vendor by id.

        Args:
            vendor_id: UUID of the vendor

        Returns:
            Vendor data

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"directory/vendors/{vendor_id}")

    def update_vendor(
        self, vendor_id: str, vendor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update vendor by id.

        Args:
            vendor_id: UUID of the vendor
            vendor_data: Updated vendor data

        Returns:
            Updated vendor data

        Raises:
            RezenError: If the API request fails
        """
        return self._request(
            "PATCH", f"directory/vendors/{vendor_id}", json_data=vendor_data
        )

    def get_vendor_w9_url(self, vendor_id: str) -> str:
        """
        Get a vendor's W9 URL.

        Args:
            vendor_id: UUID of the vendor

        Returns:
            W9 file URL

        Raises:
            RezenError: If the API request fails
        """
        response = self.get(f"directory/vendors/{vendor_id}/w9")
        # The API sometimes returns a string directly, sometimes a dict with "url" key
        # We need to handle both cases at runtime
        try:
            return str(response.get("url", ""))
        except AttributeError:
            # If response is a string, it doesn't have .get() method
            return str(response)

    def update_vendor_w9(self, vendor_id: str, w9_file: BinaryIO) -> Dict[str, Any]:
        """
        Update a vendor's W9 file.

        Args:
            vendor_id: UUID of the vendor
            w9_file: W9 file to upload

        Returns:
            Updated vendor data

        Raises:
            RezenError: If the API request fails
        """
        files = {"w9": w9_file}
        return self._request("PATCH", f"directory/vendors/{vendor_id}/w9", files=files)

    def archive_vendor(self, vendor_id: str, archive: bool = True) -> Dict[str, Any]:
        """
        Archive or unarchive a vendor.

        Args:
            vendor_id: UUID of the vendor
            archive: True to archive, False to unarchive

        Returns:
            Updated vendor data

        Raises:
            RezenError: If the API request fails
        """
        params = {"archive": archive}
        return self._request(
            "PATCH", f"directory/vendors/{vendor_id}/archive", params=params
        )

    def search_vendors(
        self,
        page_number: int,
        page_size: int,
        is_archived: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        has_linked_persons: Optional[bool] = None,
        search_text: Optional[str] = None,
        national_business_id: Optional[str] = None,
        name: Optional[str] = None,
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        postal: Optional[str] = None,
        state_or_province: Optional[Union[StateOrProvince, str]] = None,
        country: Optional[Union[Country, str]] = None,
        administrative_area_ids: Optional[List[str]] = None,
        roles: Optional[List[Union[DirectoryRole, str]]] = None,
        sort_by: Optional[List[Union[VendorSortField, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Get all vendors with paging, sorting, and filtering.

        Args:
            page_number: Page number for pagination
            page_size: Page size for pagination
            is_archived: Filter by archived status
            is_verified: Filter by verified status
            has_linked_persons: Filter by whether vendor has linked persons
            search_text: Search text
            national_business_id: Filter by national business ID
            name: Filter by name
            email_address: Filter by email address
            phone_number: Filter by phone number
            street: Filter by street address
            city: Filter by city
            postal: Filter by postal code
            state_or_province: Filter by state or province
            country: Filter by country
            administrative_area_ids: Filter by administrative area IDs
            roles: Filter by roles
            sort_by: Fields to sort by

        Returns:
            Paginated vendor search results

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        if is_archived is not None:
            params["isArchived"] = is_archived
        if is_verified is not None:
            params["isVerified"] = is_verified
        if has_linked_persons is not None:
            params["hasLinkedPersons"] = has_linked_persons
        if search_text:
            params["searchText"] = search_text
        if national_business_id:
            params["nationalBusinessId"] = national_business_id
        if name:
            params["name"] = name
        if email_address:
            params["emailAddress"] = email_address
        if phone_number:
            params["phoneNumber"] = phone_number
        if street:
            params["street"] = street
        if city:
            params["city"] = city
        if postal:
            params["postal"] = postal
        if state_or_province:
            params["stateOrProvince"] = (
                state_or_province.value
                if isinstance(state_or_province, StateOrProvince)
                else state_or_province
            )
        if country:
            params["country"] = (
                country.value if isinstance(country, Country) else country
            )
        if administrative_area_ids:
            params["administrativeAreaIds"] = administrative_area_ids
        if roles:
            params["roles"] = [
                r.value if isinstance(r, DirectoryRole) else r for r in roles
            ]
        if sort_by:
            params["sortBy"] = [
                s.value if isinstance(s, VendorSortField) else s for s in sort_by
            ]

        return self.get("directory/vendors/search/all", params=params)

    # ===== PERSON ENDPOINTS =====

    def create_person(
        self,
        person_data: Dict[str, Any],
        owner_agent_id: Optional[str] = None,
        owner_team_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a person.

        Args:
            person_data: Person creation data
            owner_agent_id: Owner agent ID
            owner_team_id: Owner team ID

        Returns:
            Created person response data

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if owner_agent_id:
            params["ownerAgentId"] = owner_agent_id
        if owner_team_id:
            params["ownerTeamId"] = owner_team_id

        return self._request(
            "POST", "directory/persons", json_data=person_data, params=params
        )

    def get_person(self, person_id: str) -> Dict[str, Any]:
        """
        Get person by id.

        Args:
            person_id: UUID of the person

        Returns:
            Person data

        Raises:
            RezenError: If the API request fails
        """
        return self.get(f"directory/persons/{person_id}")

    def update_person(
        self, person_id: str, person_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update person by id.

        Args:
            person_id: UUID of the person
            person_data: Updated person data

        Returns:
            Updated person data

        Raises:
            RezenError: If the API request fails
        """
        return self._request(
            "PATCH", f"directory/persons/{person_id}", json_data=person_data
        )

    def unlink_person(self, person_id: str) -> Dict[str, Any]:
        """
        Unlink a person from its linked vendor.

        Args:
            person_id: UUID of the person

        Returns:
            Updated person data

        Raises:
            RezenError: If the API request fails
        """
        return self._request("PATCH", f"directory/persons/{person_id}/unlink")

    def link_person(self, person_id: str, link_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Link a person to a vendor.

        Args:
            person_id: UUID of the person
            link_data: Link data containing vendor information

        Returns:
            Updated person data

        Raises:
            RezenError: If the API request fails
        """
        return self._request(
            "PATCH", f"directory/persons/{person_id}/link", json_data=link_data
        )

    def archive_person(self, person_id: str, archive: bool = True) -> Dict[str, Any]:
        """
        Archive or unarchive a person.

        Args:
            person_id: UUID of the person
            archive: True to archive, False to unarchive

        Returns:
            Updated person data

        Raises:
            RezenError: If the API request fails
        """
        params = {"archive": archive}
        return self._request(
            "PATCH", f"directory/persons/{person_id}/archive", params=params
        )

    def search_persons(
        self,
        page_number: int,
        page_size: int,
        is_archived: Optional[bool] = None,
        is_public: Optional[bool] = None,
        is_linked_to_vendor: Optional[bool] = None,
        search_text: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
        roles: Optional[List[Union[DirectoryRole, str]]] = None,
        sort_by: Optional[List[Union[PersonSortField, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Get all persons with paging, sorting, and filtering.

        Args:
            page_number: Page number for pagination
            page_size: Page size for pagination
            is_archived: Filter by archived status
            is_public: Filter by public status
            is_linked_to_vendor: Filter by whether person is linked to vendor
            search_text: Search text
            first_name: Filter by first name
            last_name: Filter by last name
            email_address: Filter by email address
            phone_number: Filter by phone number
            roles: Filter by roles
            sort_by: Fields to sort by

        Returns:
            Paginated person search results

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        if is_archived is not None:
            params["isArchived"] = is_archived
        if is_public is not None:
            params["isPublic"] = is_public
        if is_linked_to_vendor is not None:
            params["isLinkedToVendor"] = is_linked_to_vendor
        if search_text:
            params["searchText"] = search_text
        if first_name:
            params["firstName"] = first_name
        if last_name:
            params["lastName"] = last_name
        if email_address:
            params["emailAddress"] = email_address
        if phone_number:
            params["phoneNumber"] = phone_number
        if roles:
            params["roles"] = [
                r.value if isinstance(r, DirectoryRole) else r for r in roles
            ]
        if sort_by:
            params["sortBy"] = [
                s.value if isinstance(s, PersonSortField) else s for s in sort_by
            ]

        return self.get("directory/persons/search/all", params=params)

    # ===== GENERAL DIRECTORY ENDPOINTS =====

    def get_permitted_roles(
        self, entry_type: Optional[Union[DirectoryEntryType, str]] = None
    ) -> Dict[str, Any]:
        """
        Get roles available for directory entries.

        Args:
            entry_type: Filter by entry type (VENDOR or PERSON)

        Returns:
            Available roles for directory entries

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {}
        if entry_type:
            params["entryType"] = (
                entry_type.value
                if isinstance(entry_type, DirectoryEntryType)
                else entry_type
            )

        return self.get("directory/permitted-roles", params=params)

    def search_all_entries(
        self,
        page_number: int,
        page_size: int,
        is_archived: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        search_text: Optional[str] = None,
        national_business_id: Optional[str] = None,
        name: Optional[str] = None,
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        postal: Optional[str] = None,
        state_or_province: Optional[Union[StateOrProvince, str]] = None,
        country: Optional[Union[Country, str]] = None,
        administrative_area_ids: Optional[List[str]] = None,
        roles: Optional[List[Union[DirectoryRole, str]]] = None,
        created_by: Optional[str] = None,
        entry_id: Optional[str] = None,
        sort_by: Optional[List[Union[DirectoryEntrySortField, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Get all vendors and persons with paging, sorting, and filtering.

        Args:
            page_number: Page number for pagination
            page_size: Page size for pagination
            is_archived: Filter by archived status
            is_verified: Filter by verified status
            search_text: Search text
            national_business_id: Filter by national business ID
            name: Filter by name
            email_address: Filter by email address
            phone_number: Filter by phone number
            street: Filter by street address
            city: Filter by city
            postal: Filter by postal code
            state_or_province: Filter by state or province
            country: Filter by country
            administrative_area_ids: Filter by administrative area IDs
            roles: Filter by roles
            created_by: Filter by creator UUID
            entry_id: Filter by entry ID
            sort_by: Fields to sort by

        Returns:
            Paginated directory entry search results

        Raises:
            RezenError: If the API request fails
        """
        params: Dict[str, Any] = {
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        if is_archived is not None:
            params["isArchived"] = is_archived
        if is_verified is not None:
            params["isVerified"] = is_verified
        if search_text:
            params["searchText"] = search_text
        if national_business_id:
            params["nationalBusinessId"] = national_business_id
        if name:
            params["name"] = name
        if email_address:
            params["emailAddress"] = email_address
        if phone_number:
            params["phoneNumber"] = phone_number
        if street:
            params["street"] = street
        if city:
            params["city"] = city
        if postal:
            params["postal"] = postal
        if state_or_province:
            params["stateOrProvince"] = (
                state_or_province.value
                if isinstance(state_or_province, StateOrProvince)
                else state_or_province
            )
        if country:
            params["country"] = (
                country.value if isinstance(country, Country) else country
            )
        if administrative_area_ids:
            params["administrativeAreaIds"] = administrative_area_ids
        if roles:
            params["roles"] = [
                r.value if isinstance(r, DirectoryRole) else r for r in roles
            ]
        if created_by:
            params["createdBy"] = created_by
        if entry_id:
            params["id"] = entry_id
        if sort_by:
            params["sortBy"] = [
                s.value if isinstance(s, DirectoryEntrySortField) else s
                for s in sort_by
            ]

        return self.get("directory/search/all", params=params)

    # ===== CONVENIENCE METHODS =====
