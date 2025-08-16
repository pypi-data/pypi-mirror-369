"""Transaction Builder client for ReZEN API."""

from typing import Any, BinaryIO, Dict, List, Optional, Union

from .base_client import BaseClient
from .exceptions import (
    InvalidFieldNameError,
    InvalidFieldValueError,
    TransactionSequenceError,
    ValidationError,
)


class TransactionBuilderClient(BaseClient):
    """Client for transaction builder endpoints."""

    def update_title_info(
        self, transaction_id: str, title_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title details for a transaction builder.

        Important: Use camelCase for field names:
        - firstName (not first_name)
        - lastName (not last_name)
        - phoneNumber (not phone_number)

        Example:
            title_info = {
                "company": "Premier Title Company",
                "firstName": "Sarah",
                "lastName": "Johnson",
                "email": "sarah@premiertitle.com",
                "phoneNumber": "(555) 555-5555"
            }

        Args:
            transaction_id: Transaction builder ID
            title_info: Title information data with camelCase fields

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/title"
        return self.put(endpoint, json_data=title_info)

    def add_seller(
        self, transaction_id: str, seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new seller to a transaction builder.

        Important: Use camelCase for field names:
        - firstName (not first_name)
        - lastName (not last_name)
        - phoneNumber (not phone_number)

        Phone Number Format:
        - MUST include country code (1 for US)
        - Format: "1(xxx) xxx-xxxx" or "+1-xxx-xxx-xxxx"
        - Examples: "1(801) 555-9876", "+1-801-555-9876"

        Example:
            seller_info = {
                "firstName": "Jane",
                "lastName": "Smith",
                "email": "jane.smith@example.com",
                "phoneNumber": "1(555) 987-6543"  # Include country code!
            }

        Args:
            transaction_id: Transaction builder ID
            seller_info: Seller information data with camelCase fields

        Returns:
            Transaction builder response data
        """
        # Check for common field name errors
        field_mappings = {
            "first_name": "firstName",
            "last_name": "lastName",
            "phone_number": "phoneNumber",
            "phone": "phoneNumber",
        }

        for snake, camel in field_mappings.items():
            if snake in seller_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for seller fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/seller"
        return self.put(endpoint, json_data=seller_info)

    def add_referral_info(
        self,
        transaction_id: str,
        role: str,
        receives_invoice: bool,
        referral_type: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        company_name: Optional[str] = None,
        email: Optional[str] = None,
        ein: Optional[str] = None,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        agent_id: Optional[str] = None,
        file: Optional[BinaryIO] = None,
    ) -> Dict[str, Any]:
        """Add referral info to a transaction builder.

        Note: This endpoint is marked as deprecated in the API specification.

        Args:
            transaction_id: Transaction builder ID
            role: Role type (e.g., 'REAL', 'BUYERS_AGENT', 'SELLERS_AGENT', etc.)
            receives_invoice: Whether the referral receives invoice
            referral_type: Type of referral ('EXTERNAL_ENTITY' or 'AGENT')
            first_name: First name (optional)
            last_name: Last name (optional)
            company_name: Company name (optional)
            email: Email address (optional)
            ein: EIN number (optional)
            phone_number: Phone number (optional)
            address: Address (optional)
            agent_id: Agent ID (optional)
            file: File to upload (optional)

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/referral-info"
        params = {
            "role": role,
            "receivesInvoice": receives_invoice,
            "type": referral_type,
        }

        # Add optional parameters
        if first_name:
            params["firstName"] = first_name
        if last_name:
            params["lastName"] = last_name
        if company_name:
            params["companyName"] = company_name
        if email:
            params["email"] = email
        if ein:
            params["ein"] = ein
        if phone_number:
            params["phoneNumber"] = phone_number
        if address:
            params["address"] = address
        if agent_id:
            params["agentId"] = agent_id

        files = {"file": file} if file else None
        return self._request("PUT", endpoint, params=params, files=files)

    def upload_w9_to_referral_participant(
        self, transaction_id: str, participant_id: str, file: BinaryIO
    ) -> Dict[str, Any]:
        """Upload W9 to external referral participant.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID
            file: W9 file to upload

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/referral-info/{participant_id}/upload-w9"
        files = {"file": file}
        return self.put(endpoint, files=files)

    def prepare_price_and_date_data(
        self,
        sale_price: Union[int, float],
        representation_type: str,
        listing_commission_percent: float = 3.0,
        sale_commission_percent: float = 3.0,
        deal_type: str = "SALE",
        property_type: str = "RESIDENTIAL",
        acceptance_date: Optional[str] = None,
        closing_date: Optional[str] = None,
        earnest_money: Optional[float] = None,
        down_payment: Optional[float] = None,
        loan_amount: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Prepare price and date data with required commission objects.

        This helper method ensures all required fields are included with proper formatting,
        particularly the commission objects that must always be present with the critical
        negativeOrEmpty field set to false.

        ⚠️ CRITICAL FIELDS ⚠️
        Both commission objects MUST include negativeOrEmpty: false or submission will fail!

        Args:
            sale_price: The sale price amount
            representation_type: "BUYER" or "SELLER"
            listing_commission_percent: Listing commission percentage (default: 3.0)
            sale_commission_percent: Sale commission percentage (default: 3.0)
            deal_type: Deal type (default: "SALE", NOT "COMPENSATING"!)
            property_type: Property type (default: "RESIDENTIAL")
            acceptance_date: Acceptance date in "YYYY-MM-DD" format
            closing_date: Closing date in "YYYY-MM-DD" format
            earnest_money: Earnest money amount
            down_payment: Down payment amount
            loan_amount: Loan amount

        Returns:
            Dict with properly formatted price/date data including both commission objects
            with all required fields including negativeOrEmpty: false

        Example:
            ```python
            # Simple usage with defaults
            price_data = client.prepare_price_and_date_data(
                sale_price=500000,
                representation_type="BUYER",
                acceptance_date="2024-06-16",
                closing_date="2024-07-16"
            )
            # This will include:
            # - dealType: "SALE" (not "COMPENSATING")
            # - propertyType: "RESIDENTIAL"
            # - Both commissions with negativeOrEmpty: false

            result = client.update_price_and_date_info(transaction_id, price_data)
            ```
        """
        data: Dict[str, Any] = {
            "dealType": deal_type,
            "propertyType": property_type,
            "salePrice": {"amount": sale_price, "currency": "USD"},
            "representationType": representation_type,
            "listingCommission": {
                "commissionPercent": listing_commission_percent,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
            "saleCommission": {
                "commissionPercent": sale_commission_percent,
                "percentEnabled": True,
                "negativeOrEmpty": False,
            },
        }

        # Add optional fields if provided
        if acceptance_date:
            data["acceptanceDate"] = acceptance_date
        if closing_date:
            data["closingDate"] = closing_date
        if earnest_money is not None:
            data["earnestMoney"] = earnest_money
        if down_payment is not None:
            data["downPayment"] = down_payment
        if loan_amount is not None:
            data["loanAmount"] = loan_amount

        return data

    def update_price_and_date_info(
        self, transaction_id: str, price_date_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update price and date information.

        ⚠️ CRITICAL REQUIREMENT ⚠️
        Basic price/date fields alone will FAIL with "Bad request: Invalid request".
        The API requires BOTH commission objects for successful price/date updates.

        REQUIRED COMMISSION FIELDS:
            Both listingCommission AND saleCommission objects are REQUIRED together.
            You cannot provide just one - the API needs both.

        Field Structure Requirements:
            - salePrice MUST be an object with 'amount' and 'currency', NOT a simple number
            - All dates use camelCase format: acceptanceDate, closingDate, etc.
            - representationType determines valid agent roles (BUYER → BUYERS_AGENT, SELLER → SELLERS_AGENT)

        Required Fields for Success:
            - dealType (str): Deal type - use "SALE" for standard transactions
                - "SALE": Standard sale transaction (recommended)
                - "COMPENSATING": May cause 500 errors on submission (deprecated)
                - "NON_COMPENSATING": May cause 500 errors on submission (deprecated)
            - propertyType (str): "RESIDENTIAL", "COMMERCIAL", etc.
            - salePrice (dict): {"amount": 500000, "currency": "USD"}
            - representationType (str): "BUYER" or "SELLER" - affects owner agent role
            - listingCommission (dict): Commission object - REQUIRED
            - saleCommission (dict): Commission object - REQUIRED

        Optional Fields:
            - acceptanceDate (str): Date in "YYYY-MM-DD" format
            - closingDate (str): Date in "YYYY-MM-DD" format
            - earnestMoney (float): Earnest money amount
            - downPayment (float): Down payment amount
            - loanAmount (float): Loan amount

        Working Example:
            ```python
            # ✅ This WORKS (includes both required commission objects)
            price_date_info = {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL",
                "salePrice": {
                    "amount": 565000,
                    "currency": "USD"
                },
                "representationType": "BUYER",
                "listingCommission": {       # REQUIRED
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                },
                "saleCommission": {          # REQUIRED
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                },
                "acceptanceDate": "2024-01-15",
                "closingDate": "2024-02-28"
            }

            # ❌ This FAILS (missing commission objects)
            price_date_info = {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL",
                "salePrice": {"amount": 500000, "currency": "USD"},
                "representationType": "BUYER"
                # Missing both commission objects - API returns "Bad request: Invalid request"
            }

            # ❌ This ALSO FAILS (only one commission object)
            price_date_info = {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL",
                "salePrice": {"amount": 500000, "currency": "USD"},
                "representationType": "BUYER",
                "listingCommission": {       # Only one commission
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                }
                # Missing saleCommission - API still returns "Bad request: Invalid request"
            }
            ```

        Args:
            transaction_id: Transaction builder ID
            price_date_info: Price and date information data with BOTH commission objects

        Returns:
            Transaction builder response data

        Raises:
            ValidationError: If missing required fields or commission objects
            InvalidFieldValueError: If salePrice format is incorrect or representationType invalid
        """
        # Validate required fields
        required_fields = [
            "dealType",
            "propertyType",
            "salePrice",
            "representationType",
            "listingCommission",
            "saleCommission",
        ]
        missing_fields = [
            field for field in required_fields if field not in price_date_info
        ]
        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}. "
                f"CRITICAL: Both listingCommission AND saleCommission objects are required for price/date updates. "
                f"All of these are required: {', '.join(required_fields)}"
            )

        # Validate salePrice structure
        if "salePrice" in price_date_info:
            sale_price = price_date_info["salePrice"]
            if isinstance(sale_price, (int, float)):
                raise InvalidFieldValueError(
                    "salePrice",
                    sale_price,
                    "Object with 'amount' and 'currency' fields: {'amount': 500000, 'currency': 'USD'}",
                )
            elif isinstance(sale_price, dict):
                if "amount" not in sale_price or "currency" not in sale_price:
                    raise InvalidFieldValueError(
                        "salePrice",
                        sale_price,
                        "Object must contain both 'amount' and 'currency' fields",
                    )

        # Validate representationType values
        if "representationType" in price_date_info:
            rep_type = price_date_info["representationType"]
            valid_types = ["BUYER", "SELLER"]
            if rep_type not in valid_types:
                raise InvalidFieldValueError(
                    "representationType",
                    rep_type,
                    f"One of: {', '.join(valid_types)} (Note: Use 'BUYER' not 'BUYERS_AGENT')",
                )

        # Check for common date field errors
        date_fields = {
            "acceptance_date": "acceptanceDate",
            "closing_date": "closingDate",
        }
        for snake, camel in date_fields.items():
            if snake in price_date_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for date fields."
                )

        # Ensure commission objects have negativeOrEmpty field
        for commission_field in ["listingCommission", "saleCommission"]:
            if commission_field in price_date_info and isinstance(
                price_date_info[commission_field], dict
            ):
                if "negativeOrEmpty" not in price_date_info[commission_field]:
                    price_date_info[commission_field]["negativeOrEmpty"] = False

        endpoint = f"transaction-builder/{transaction_id}/price-date-info"
        return self.put(endpoint, json_data=price_date_info)

    def update_personal_deal_info(
        self, transaction_id: str, deal_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update personal deal information.

        Sets whether this transaction is a personal deal (agent buying/selling own property).

        Required Fields:
            - isPersonalDeal (bool): Whether this is a personal deal

        Example:
            ```python
            deal_info = {
                "isPersonalDeal": True  # Agent is buying/selling their own property
            }
            client.update_personal_deal_info(transaction_id, deal_info)
            ```

        Args:
            transaction_id: Transaction builder ID
            deal_info: Personal deal information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/personal-deal-info"
        return self.put(endpoint, json_data=deal_info)

    def update_owner_info(
        self, transaction_id: str, owner_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update owner agent information.

        Args:
            transaction_id: Transaction builder ID
            owner_info: Owner agent information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/owner-info"
        return self.put(endpoint, json_data=owner_info)

    def add_participant(
        self, transaction_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new participant to the transaction builder.

        Args:
            transaction_id: Transaction builder ID
            participant_info: Participant information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/other-participants"
        # This endpoint uses multipart/form-data according to the schema
        # Convert form data to files format to force multipart
        files = {key: (None, str(value)) for key, value in participant_info.items()}
        return self._request("PUT", endpoint, files=files)

    def add_opcity(self, transaction_id: str, opcity: bool) -> Dict[str, Any]:
        """Add opcity to transaction builder.

        Args:
            transaction_id: Transaction builder ID
            opcity: Whether to enable opcity

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/opcity"
        params = {"opcity": opcity}
        return self._request("PUT", endpoint, params=params)

    def update_mortgage_info(
        self, transaction_id: str, mortgage_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update mortgage information.

        Args:
            transaction_id: Transaction builder ID
            mortgage_info: Mortgage information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/mortgage-info"
        return self.put(endpoint, json_data=mortgage_info)

    def update_location_info(
        self, transaction_id: str, location_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update location information.

        ⚠️ CRITICAL REQUIREMENT ⚠️
        Basic address fields alone (street, city, state, zip) will FAIL.
        The API requires additional property details for successful location updates.

        REQUIRED ADDITIONAL FIELDS (beyond basic address):
            - county (str): County name (e.g., "Salt Lake")
            - yearBuilt (int): Year the property was built (e.g., 2020)
            - mlsNumber (str): MLS listing number (e.g., "MLS123456")

        Field Name Requirements:
            - Use 'street' not 'address'
            - Use 'zip' not 'zipCode' or 'zip_code'
            - State must be ALL CAPS (e.g., 'UTAH', 'CALIFORNIA')
            - Use camelCase for: yearBuilt, mlsNumber, escrowNumber

        Required Fields for Success:
            - street (str): Property street address
            - city (str): City name
            - state (str): State name in ALL CAPS
            - zip (str): ZIP code
            - county (str): County name - REQUIRED
            - yearBuilt (int): Year built - REQUIRED
            - mlsNumber (str): MLS number - REQUIRED

        Optional Fields:
            - street2 (str): Secondary address line
            - unit (str): Unit number
            - escrowNumber (str): Escrow number

        Working Example:
            ```python
            # ✅ This WORKS (includes required additional fields)
            location_info = {
                "street": "123 Main Street",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
                "county": "Salt Lake",        # REQUIRED
                "yearBuilt": 2020,           # REQUIRED
                "mlsNumber": "MLS123456",    # REQUIRED
                "escrowNumber": "ESC-2024-001"  # Optional
            }

            # ❌ This FAILS (missing required additional fields)
            location_info = {
                "street": "123 Main Street",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101"
                # Missing county, yearBuilt, mlsNumber - API returns "Bad request: Invalid request"
            }
            ```

        Args:
            transaction_id: Transaction builder ID
            location_info: Location information data with ALL required fields

        Returns:
            Transaction builder response data

        Raises:
            InvalidFieldNameError: If using wrong field names (address, zipCode, etc.)
            InvalidFieldValueError: If state is not in ALL CAPS
            ValidationError: If missing required additional fields
        """
        # Check for common field name errors
        if "address" in location_info:
            raise InvalidFieldNameError(
                "address",
                "street",
                "The API expects 'street' for the property address.",
            )

        if "zipCode" in location_info or "zip_code" in location_info:
            raise InvalidFieldNameError(
                "zipCode/zip_code", "zip", "The API expects 'zip' for the ZIP code."
            )

        # Validate state format if present
        if "state" in location_info:
            state = location_info["state"]
            # Check if it's lowercase or mixed case
            if state and state != state.upper():
                raise InvalidFieldValueError(
                    "state",
                    state,
                    "State code in ALL CAPS (e.g., 'UTAH', 'CALIFORNIA')",
                )

        # Check for snake_case field names
        snake_case_fields = {
            "year_built": "yearBuilt",
            "mls_number": "mlsNumber",
            "escrow_number": "escrowNumber",
        }
        for snake, camel in snake_case_fields.items():
            if snake in location_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for property fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/location-info"
        return self.put(endpoint, json_data=location_info)

    def update_fmls_info(
        self, transaction_id: str, fmls_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update whether this builder's property is listed on FMLS.

        Args:
            transaction_id: Transaction builder ID
            fmls_info: FMLS information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/fmls"
        return self.put(endpoint, json_data=fmls_info)

    def add_double_ender_agent(
        self, transaction_id: str, agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add double-ender agent to the transaction builder.

        Args:
            transaction_id: Transaction builder ID
            agent_info: Double-ender agent information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/double-ender-agent"
        return self.put(endpoint, json_data=agent_info)

    def add_commission_payer(
        self, transaction_id: str, commission_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add commission payer information.

        IMPORTANT: This endpoint requires multipart/form-data format.
        The method automatically handles the conversion for you.

        ⚠️ CRITICAL FOR SUBMISSION ⚠️
        Commission payer (usually title company) is REQUIRED before transaction submission!
        Without it, submission will fail.

        Required Fields:
            - role (str): Commission payer role. Common values:
                - "TITLE" - Title company (most common)
                - "SELLER" - Seller pays commission
                - "LANDLORD" - Landlord (for rental transactions)
                - "OTHER_AGENT" - Another agent pays
                - "REAL" - Real (company) pays
            - firstName (str): First name of the commission payer
            - lastName (str): Last name of the commission payer
            - email (str): Email address of the commission payer
            - phoneNumber (str): Phone number with country code (e.g., "1(555) 123-4567")
            - companyName (str): Company name of the commission payer

        Optional Fields:
            - receivesInvoice (bool): Whether the payer receives invoice (default: False)
            - opCityReferral (bool): Whether this is an OpCity referral (default: False)
            - optedInForEcp (bool): Whether opted in for ECP (default: False)
            - participantId (str): If provided, validation for other fields is bypassed
            - address (str): Address of the commission payer
            - ein (str): Employer Identification Number

        Special Notes:
            1. If you provide a participantId, the validation for other required fields is ignored.
               This is useful when referencing an existing participant.
            2. The role "TITLE" is most commonly used for title companies.
            3. Some role values like "NA", "LISTING_AGENT", "BUYERS_AGENT" may not work as
               they are not valid enum values for commission payer roles.

        Working Example (Title Company):
            ```python
            # Title company as commission payer (most common)
            commission_info = {
                "role": "TITLE",
                "firstName": "ABC",
                "lastName": "Title",
                "email": "closing@abctitle.com",
                "phoneNumber": "1(801) 555-5555",  # Include country code!
                "companyName": "ABC Title Company",
                "receivesInvoice": True,
                "opCityReferral": False,
                "optedInForEcp": False
            }
            result = client.add_commission_payer(transaction_id, commission_info)

            # Using existing participant ID (bypasses validation)
            commission_info = {
                "role": "TITLE",
                "participantId": "existing-participant-uuid",
                "receivesInvoice": True
            }
            result = client.add_commission_payer(transaction_id, commission_info)
            ```

        Args:
            transaction_id: Transaction builder ID
            commission_info: Commission payer information data

        Returns:
            Transaction builder response data with commissionPayerInfo populated
        """
        endpoint = f"transaction-builder/{transaction_id}/commission-payer"
        # This endpoint requires multipart/form-data
        # Convert form data to files format to force multipart
        files = {key: (None, str(value)) for key, value in commission_info.items()}
        return self._request("PUT", endpoint, files=files)

    def update_commission_splits(
        self, transaction_id: str, commission_splits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update commission splits information.

        ⚠️ CRITICAL: Commission splits require PARTICIPANT IDs, not AGENT IDs! ⚠️

        After adding agents (owner agent, co-agents) to the transaction, each agent gets
        a PARTICIPANT ID. You must use these participant IDs for commission splits.

        🔄 REQUIRED WORKFLOW:
        1. Create transaction and add all basic info (location, price/dates, buyers/sellers)
        2. Add owner agent and any co-agents
        3. Call get_transaction_builder() to retrieve the participant IDs
        4. Use the participant IDs (NOT agent IDs) for commission splits

        Commission Split Structure:
            Each split should contain:
            - participantId (str): The participant ID from transaction data (NOT agent ID!)
            - commission (dict): Commission data object with:
                - commissionPercent (float): Percentage (e.g., 50.0 for 50%)
                - percentEnabled (bool): Always True for percentage-based
                - negativeOrEmpty (bool): Always False for valid commissions

        WORKING EXAMPLE:
            ```python
            # Step 1: Get the transaction to find participant IDs
            transaction = client.transaction_builder.get_transaction_builder(transaction_id)

            # Step 2: Extract participant IDs from agents
            owner_participant_id = None
            co_agent_participant_id = None

            # From owner agents
            for agent in transaction["agentsInfo"]["ownerAgent"]:
                if agent["agentId"] == "your-agent-uuid":
                    owner_participant_id = agent["id"]  # This is the participant ID!

            # From co-agents
            for agent in transaction["agentsInfo"]["coAgents"]:
                if agent["agentId"] == "co-agent-uuid":
                    co_agent_participant_id = agent["id"]  # This is the participant ID!

            # Step 3: Create commission splits using PARTICIPANT IDs
            commission_splits = [
                {
                    "participantId": owner_participant_id,  # NOT agentId!
                    "commission": {
                        "commissionPercent": 80.0,
                        "percentEnabled": True,
                        "negativeOrEmpty": False
                    }
                },
                {
                    "participantId": co_agent_participant_id,  # NOT agentId!
                    "commission": {
                        "commissionPercent": 20.0,
                        "percentEnabled": True,
                        "negativeOrEmpty": False
                    }
                }
            ]

            # Step 4: Submit commission splits
            client.update_commission_splits(transaction_id, commission_splits)
            ```

        ❌ COMMON MISTAKE:
            Using agent IDs instead of participant IDs will fail with "Bad request"

        Args:
            transaction_id: Transaction builder ID
            commission_splits: List of commission split data with PARTICIPANT IDs

        Returns:
            Transaction builder response data

        Raises:
            ValidationError: If using agent IDs instead of participant IDs
        """
        endpoint = f"transaction-builder/{transaction_id}/commission-info"
        return self._request("PUT", endpoint, json_data=commission_splits)

    def update_owner_agent_info(
        self, transaction_builder_id: str, owner_agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update owner agent information for the transaction.

        ✅ WORKING SOLUTION ✅
        This method now works correctly when called in the proper sequence.

        🔄 REQUIRED SEQUENCE:
        1. Create transaction (create_transaction_builder)
        2. Add location info with ALL required fields (update_location_info)
        3. Add price/date info with commission objects (update_price_and_date_info)
        4. Add buyers/sellers (add_buyer/add_seller)
        5. THEN add owner agent (this method) - ✅ WORKS!

        📋 COMPLETE DATA REQUIREMENTS:

        Location Info Must Include:
            - street, city, state, zip (basic)
            - county: Required additional field
            - yearBuilt: Required additional field
            - mlsNumber: Required additional field

        Price/Date Info Must Include:
            - dealType, propertyType, salePrice, representationType (basic)
            - listingCommission: Required commission object
            - saleCommission: Required commission object

        Owner Agent Data Structure:
            owner_agent_info = {
                "ownerAgent": {
                    "agentId": str,  # User ID (same as agent ID in ReZEN)
                    "role": str      # "BUYERS_AGENT" or "SELLERS_AGENT"
                },
                "officeId": str,     # From user.offices[0].id
                "teamId": str        # UUID of the team
            }

        🎯 GETTING THE RIGHT IDS:
            - agentId: Use current user's ID (user["id"] from get_current_user())
            - officeId: Use user["offices"][0]["id"] from get_current_user()
            - teamId: Use team ID from get_user_teams_and_offices()

        Role Matching:
            The role MUST match the representationType from price/date info:
            - representationType: "BUYER" → role: "BUYERS_AGENT"
            - representationType: "SELLER" → role: "SELLERS_AGENT"

        💡 TIP: Use convenience methods instead of manual setup:
            - set_current_user_as_owner_agent() for default team
            - set_current_user_as_owner_agent_with_team() for specific team

        Example - Complete Working Sequence:
            ```python
            # 1. Create transaction
            builder_id = client.transaction_builder.create_transaction_builder()

            # 2. Add location with ALL required fields (REQUIRED FIRST)
            client.transaction_builder.update_location_info(builder_id, {
                "street": "123 Main St",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
                "county": "Salt Lake",        # REQUIRED
                "yearBuilt": 2020,           # REQUIRED
                "mlsNumber": "MLS-123456"    # REQUIRED
            })

            # 3. Add price/date with commission objects (REQUIRED SECOND)
            client.transaction_builder.update_price_and_date_info(builder_id, {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL",
                "salePrice": {"amount": 500000, "currency": "USD"},
                "representationType": "BUYER",
                "listingCommission": {       # REQUIRED
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                },
                "saleCommission": {          # REQUIRED
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                }
            })

            # 4. Add buyer (REQUIRED THIRD)
            client.transaction_builder.add_buyer(builder_id, {
                "firstName": "John",
                "lastName": "Buyer",
                "email": "john@example.com",
                "phoneNumber": "1(801) 555-1234"  # Include country code!
            })

            # 5. Get user and office info
            user = client.users.get_current_user()

            # 6. NOW add owner agent (WORKS!)
            owner_info = {
                "ownerAgent": {
                    "agentId": user["id"],          # User ID = Agent ID
                    "role": "BUYERS_AGENT"          # Must match representationType
                },
                "officeId": user["offices"][0]["id"],  # From user's offices
                "teamId": "your-team-uuid"              # Your team ID
            }
            result = client.transaction_builder.update_owner_agent_info(builder_id, owner_info)
            ```

        Args:
            transaction_builder_id: UUID of the transaction builder
            owner_agent_info: Dictionary containing owner agent details

        Returns:
            Updated transaction builder data

        Raises:
            ValidationError: If owner agent info is invalid or sequence not followed
            NotFoundError: If transaction builder not found
        """
        # Validate required structure
        if "ownerAgent" not in owner_agent_info:
            raise ValidationError(
                "Missing required field 'ownerAgent'. Expected structure: "
                "{'ownerAgent': {'agentId': 'uuid', 'role': 'BUYERS_AGENT'}, "
                "'officeId': 'uuid', 'teamId': 'uuid'}"
            )

        owner_agent = owner_agent_info["ownerAgent"]
        if not isinstance(owner_agent, dict):
            raise InvalidFieldValueError(
                "ownerAgent", owner_agent, "Object with 'agentId' and 'role' fields"
            )

        # Validate ownerAgent fields
        if "agentId" not in owner_agent:
            raise ValidationError("Missing required field 'agentId' in ownerAgent")
        if "role" not in owner_agent:
            raise ValidationError("Missing required field 'role' in ownerAgent")

        # Validate role value
        role = owner_agent["role"]
        valid_roles = ["BUYERS_AGENT", "SELLERS_AGENT"]
        if role not in valid_roles:
            raise InvalidFieldValueError(
                "role",
                role,
                f"One of: {', '.join(valid_roles)} (Must match representationType: BUYER→BUYERS_AGENT, SELLER→SELLERS_AGENT)",
            )

        # Validate required fields for transaction creation
        if "officeId" not in owner_agent_info:
            raise ValidationError(
                "Missing required field 'officeId' - required for transaction creation"
            )
        if "teamId" not in owner_agent_info:
            raise ValidationError(
                "Missing required field 'teamId' - required for transaction creation"
            )

        endpoint = f"transaction-builder/{transaction_builder_id}/owner-info"

        try:
            return self.put(endpoint, json_data=owner_agent_info)
        except ValidationError as e:
            # If we get a generic "Bad request" error, provide more helpful context
            if "Invalid request" in str(e):
                raise TransactionSequenceError(
                    "Owner agent endpoint failed. This usually means the transaction isn't properly set up yet.",
                    required_steps=[
                        "Create transaction (create_transaction_builder)",
                        "Add location info (update_location_info) - REQUIRED FIRST",
                        "Add price/date info (update_price_and_date_info) with representationType - REQUIRED SECOND",
                        "Add buyers/sellers (add_buyer/add_seller) - REQUIRED THIRD",
                        "THEN add owner agent (update_owner_agent_info)",
                    ],
                )
            raise  # Re-raise if it's a different error

    def add_co_agent(
        self, transaction_id: str, co_agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new co-agent to the transaction.

        Co-agents can be added at any time after transaction creation, unlike owner agents
        which require a specific sequence. The co-agent will appear in the transaction's
        agentsInfo.coAgents array.

        ⚠️ ROLE LIMITATIONS ⚠️
        Based on testing, only certain roles work with co-agents:

        ✅ WORKING ROLES:
            - "REAL" - Always works (may display differently based on representationType)
            - "BUYERS_AGENT" - Works on transactions with location data
            - "SELLERS_AGENT" - Works on transactions with location data

        ❌ NON-WORKING ROLES:
            - "LISTING_AGENT" - Fails with "Bad request: Invalid request"

        Required Fields:
            - agentId (str): UUID of the co-agent (must be a valid agent ID)
            - role (str): Agent role - use one of the working roles above
            - receivesInvoice (bool): Whether the co-agent receives invoice

        Optional Fields:
            - opCityReferral (bool): Whether this is an OpCity referral (default: False)
            - optedInForEcp (bool): Whether opted in for ECP (default: False)

        Note on Role Display:
            The role field accepts "REAL" but may be displayed differently in the response
            based on the transaction's representationType. For example, if representationType
            is "BUYER", a co-agent with role "REAL" may appear as "BUYERS_AGENT" in the response.

        Working Examples:
            ```python
            # ✅ Co-agent with REAL role (always works)
            co_agent_info = {
                "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                "role": "REAL",
                "receivesInvoice": False,
                "opCityReferral": False,
                "optedInForEcp": False
            }
            result = client.add_co_agent(transaction_id, co_agent_info)

            # ✅ Co-agent with BUYERS_AGENT role (works with location data)
            co_agent_info = {
                "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                "role": "BUYERS_AGENT",
                "receivesInvoice": False
            }
            result = client.add_co_agent(transaction_id, co_agent_info)

            # ❌ This FAILS (LISTING_AGENT role not supported)
            co_agent_info = {
                "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                "role": "LISTING_AGENT",  # This role fails
                "receivesInvoice": False
            }
            # Will return "Bad request: Invalid request"
            ```

        Args:
            transaction_id: Transaction builder ID
            co_agent_info: Co-agent information data

        Returns:
            Transaction builder response data with updated co-agents list

        Raises:
            ValidationError: If role is not supported or agent ID is invalid
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent"
        return self.put(endpoint, json_data=co_agent_info)

    def add_buyer(
        self, transaction_id: str, buyer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new buyer.

        Important: Use camelCase for field names:
        - firstName (not first_name)
        - lastName (not last_name)
        - phoneNumber (not phone_number)

        Phone Number Format:
        - MUST include country code (1 for US)
        - Format: "1(xxx) xxx-xxxx" or "+1-xxx-xxx-xxxx"
        - Examples: "1(801) 555-0123", "+1-801-555-0123"

        Example:
            buyer_info = {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john.doe@example.com",
                "phoneNumber": "1(555) 123-4567"  # Include country code!
            }

        Args:
            transaction_id: Transaction builder ID
            buyer_info: Buyer information data with camelCase fields

        Returns:
            Transaction builder response data
        """
        # Check for common field name errors
        field_mappings = {
            "first_name": "firstName",
            "last_name": "lastName",
            "phone_number": "phoneNumber",
            "phone": "phoneNumber",
        }

        for snake, camel in field_mappings.items():
            if snake in buyer_info:
                raise InvalidFieldNameError(
                    snake, camel, "Use camelCase for buyer fields."
                )

        endpoint = f"transaction-builder/{transaction_id}/buyer"
        return self.put(endpoint, json_data=buyer_info)

    def update_buyer_and_seller_info(
        self, transaction_id: str, buyer_seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update buyer and seller information.

        Args:
            transaction_id: Transaction builder ID
            buyer_seller_info: Buyer and seller information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer-seller-info"
        return self.put(endpoint, json_data=buyer_seller_info)

    def update_additional_fees_info(
        self, transaction_id: str, fees_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update additional fees information.

        Args:
            transaction_id: Transaction builder ID
            fees_info: Additional fees information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/additional-fees-info"
        return self.put(endpoint, json_data=fees_info)

    def add_referral_info_v2(
        self, transaction_id: str, referral_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add referral info (v2 endpoint).

        Args:
            transaction_id: Transaction builder ID
            referral_info: Referral information data

        Returns:
            Builder participant data
        """
        endpoint = f"transaction-builder/{transaction_id}/add-referral-info"
        return self.put(endpoint, json_data=referral_info)

    # GET endpoints
    def get_transaction_builders(
        self,
        limit: int,
        from_offset: int,
        yenta_id: str,
        builder_type: str = "TRANSACTION",
    ) -> Dict[str, Any]:
        """Get a paginated list of transaction builders.

        Args:
            limit: Maximum number of results to return
            from_offset: Starting offset for pagination
            yenta_id: User ID
            builder_type: Type of builder ('TRANSACTION' or 'LISTING')

        Returns:
            Paginated list of transaction builders
        """
        endpoint = "transaction-builder"
        params = {
            "limit": limit,
            "from": from_offset,
            "yentaId": yenta_id,
            "type": builder_type,
        }
        return self.get(endpoint, params=params)

    def get_transaction_builders_paged(
        self,
        limit: int,
        from_offset: int,
        yenta_id: str,
        builder_type: str = "TRANSACTION",
    ) -> Dict[str, Any]:
        """Get a paginated list of transaction builders (alternative endpoint).

        Args:
            limit: Maximum number of results to return
            from_offset: Starting offset for pagination
            yenta_id: User ID
            builder_type: Type of builder ('TRANSACTION' or 'LISTING')

        Returns:
            Paginated list of transaction builders
        """
        endpoint = "transaction-builder/paged"
        params = {
            "limit": limit,
            "from": from_offset,
            "yentaId": yenta_id,
            "type": builder_type,
        }
        return self.get(endpoint, params=params)

    def get_transaction_builder(self, transaction_id: str) -> Dict[str, Any]:
        """Get a specific transaction builder by ID.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction builder data
        """
        endpoint = f"transaction-builder/{transaction_id}"
        return self.get(endpoint)

    def get_builder_features(self, transaction_id: str) -> Dict[str, Any]:
        """Get optional features available for the transaction being built.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Available features data
        """
        endpoint = f"transaction-builder/{transaction_id}/features"
        return self.get(endpoint)

    def get_eligible_for_mortgage_ecp(self, transaction_id: str) -> Dict[str, Any]:
        """Check if transaction builder is eligible for mortgage ECP.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Eligibility status
        """
        endpoint = f"transaction-builder/{transaction_id}/eligible-for-mortgage-ecp"
        return self.get(endpoint)

    def get_commission_payer_roles_and_display_name(
        self, transaction_id: str
    ) -> Dict[str, Any]:
        """Get commission payer roles and display names for transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Commission payer roles and display names
        """
        endpoint = f"transaction-builder/{transaction_id}/commission-payer-roles-and-display-name"
        return self.get(endpoint)

    def get_commission_payer_roles(
        self, country: str = "UNITED_STATES"
    ) -> Dict[str, Any]:
        """Get available commission payer roles.

        Args:
            country: Country code (default: "UNITED_STATES")

        Returns:
            Available commission payer roles
        """
        endpoint = "transaction-builder/commission-payer-roles"
        params = {"country": country}
        return self.get(endpoint, params=params)

    def get_commission_payer_roles_and_display_names(
        self, country: str = "UNITED_STATES", representation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get commission payer roles and their display names.

        Args:
            country: Country code (default: "UNITED_STATES")
            representation_type: Type of representation (e.g., "SELLER", "BUYER")

        Returns:
            Commission payer roles with display names
        """
        endpoint = "transaction-builder/commission-payer-roles-and-display-name"
        params = {"country": country}
        if representation_type:
            params["representationType"] = representation_type
        return self.get(endpoint, params=params)

    def get_metadata_for_participant_creation(
        self, transaction_id: str, participant_role: str
    ) -> Dict[str, Any]:
        """Get metadata required to create a participant.

        Args:
            transaction_id: Transaction builder ID
            participant_role: Role of the participant to be created

        Returns:
            Metadata for participant creation
        """
        endpoint = f"transaction-builder/{transaction_id}/metadata-for-participant-creation/{participant_role}"
        return self.get(endpoint)

    # POST endpoints
    def create_transaction_builder(
        self, builder_type: str = "TRANSACTION"
    ) -> Dict[str, Any]:
        """Create empty transaction builder.

        This is the starting point for creating a new transaction. After creation,
        you'll receive a transaction ID that you'll use for all subsequent operations.

        ⚠️ CRITICAL: Follow the recommended workflow for successful transaction creation.
        Many endpoints require specific data to be present before they will work.

        Recommended Workflow:
            1. Create transaction builder (this method)
            2. Add location info (update_location_info) - REQUIRES additional fields
            3. Add price/date info (update_price_and_date_info) - REQUIRES commission objects
            4. Add buyers/sellers (add_buyer/add_seller) - Works after location data
            5. Add co-agents (add_co_agent) - Works with specific roles
            6. Add owner agent (update_owner_agent_info) - Requires complete setup + office/team IDs

        Successful Working Example:
            ```python
            # Complete working sequence with co-agent
            client = RezenClient()

            # 1. Create transaction
            response = client.transaction_builder.create_transaction_builder()
            transaction_id = response["id"]

            # 2. Add location (with required additional fields)
            location_data = {
                "street": "123 Main Street",
                "city": "Salt Lake City",
                "state": "UTAH",
                "zip": "84101",
                "county": "Salt Lake",      # REQUIRED
                "yearBuilt": 2020,         # REQUIRED
                "mlsNumber": "MLS123456"   # REQUIRED
            }
            client.transaction_builder.update_location_info(transaction_id, location_data)

            # 3. Add price/date (with both commission objects)
            price_data = {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL",
                "salePrice": {"amount": 550000, "currency": "USD"},
                "representationType": "BUYER",
                "listingCommission": {     # REQUIRED
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                },
                "saleCommission": {        # REQUIRED
                    "commissionPercent": 3.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                }
            }
            client.transaction_builder.update_price_and_date_info(transaction_id, price_data)

            # 4. Add participants
            client.transaction_builder.add_buyer(transaction_id, {
                "firstName": "John",
                "lastName": "Buyer",
                "email": "john@example.com",
                "phoneNumber": "1(801) 555-1234"  # Include country code!
            })

            # 5. Add co-agent (this works immediately)
            co_agent_info = {
                "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
                "role": "REAL",
                "receivesInvoice": False
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_info)

            # Result: Complete working transaction with co-agent
            print(f"✅ Successfully created transaction {transaction_id} with co-agent")
            ```

        Builder Types:
            - "TRANSACTION": Standard real estate transaction
            - "LISTING": Property listing

        Args:
            builder_type: Type of builder to create ("TRANSACTION" or "LISTING")

        Returns:
            Dictionary with transaction builder ID: {"id": "transaction-id"}

        Raises:
            ValidationError: If builder_type is invalid
            RezenError: If transaction creation fails
        """
        endpoint = "transaction-builder"
        params = {"type": builder_type}
        response = self._request("POST", endpoint, params=params)

        # Ensure consistent response format
        # The API returns just the ID string, so we wrap it
        if isinstance(response, dict):
            # If already a dict with id, return as-is
            if "id" in response:
                return response
            # If dict with message, use message as ID
            elif "message" in response:
                return {"id": str(response["message"])}

        # If string response, wrap in dict
        return {"id": str(response)}

    def create_listing_builder(self) -> Dict[str, Any]:
        """Create a listing builder (wrapper for create_transaction_builder).

        Returns:
            Dictionary with listing builder ID: {"id": "listing-id"}
        """
        return self.create_transaction_builder(builder_type="LISTING")

    def convert_listing_to_transaction(self, listing_id: str) -> Dict[str, Any]:
        """Convert a listing to a transaction (wrapper for create_builder_from_transaction).

        Args:
            listing_id: Listing ID to convert

        Returns:
            Transaction builder response data
        """
        return self.create_builder_from_transaction(listing_id)

    def create_builder_from_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Create transaction builder from given transaction.

        Args:
            transaction_id: Transaction ID to create builder from

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/transaction-to-builder"
        return self.post(endpoint)

    def add_transaction_coordinator(
        self, transaction_id: str, yenta_id: str
    ) -> Dict[str, Any]:
        """Add transaction coordinator to transaction builder.

        Args:
            transaction_id: Transaction builder ID
            yenta_id: Coordinator user ID

        Returns:
            Transaction builder response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/transaction-coordinator/{yenta_id}"
        )
        return self.post(endpoint)

    def submit_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Submit a transaction builder to create a transaction.

        ⚠️ CRITICAL REQUIREMENT: Commission splits MUST be populated before submission! ⚠️

        The API will reject submission with error "commissionSplitsInfo cannot be empty"
        if commission splits are not properly configured.

        🔄 COMPLETE SUBMISSION WORKFLOW:

        1. Create transaction builder
        2. Add location info (street, city, state, zip, county, yearBuilt, mlsNumber)
        3. Add price/date info with BOTH commissions and required fields:
           - dealType: "SALE" (not "COMPENSATING")
           - propertyType: "RESIDENTIAL"
           - Both listingCommission and saleCommission with negativeOrEmpty: false
        4. Add buyer (required)
        5. Add seller (required - even for buyer representation!)
        6. Add owner agent (and co-agents if needed)
        6. Get transaction builder to retrieve participant IDs
        7. Add commission splits using PARTICIPANT IDs (not agent IDs!)
        8. Add commission payer (title company)
        9. Submit transaction

        WORKING EXAMPLE:
            ```python
            # After all setup steps...

            # Get participant IDs
            transaction = client.transaction_builder.get_transaction_builder(transaction_id)

            # Find participant IDs from agents
            owner_participant_id = None
            for agent in transaction["agentsInfo"]["ownerAgent"]:
                if agent["agentId"] == current_user_id:
                    owner_participant_id = agent["id"]
                    break

            # Add commission splits (REQUIRED!)
            commission_splits = [{
                "participantId": owner_participant_id,
                "commission": {
                    "commissionPercent": 100.0,
                    "percentEnabled": True,
                    "negativeOrEmpty": False
                }
            }]
            client.transaction_builder.update_commission_splits(
                transaction_id, commission_splits
            )

            # Now submit
            result = client.transaction_builder.submit_transaction(transaction_id)
            ```

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction preview response data with submitted transaction details

        Raises:
            ValidationError: If commission splits are missing or other required fields
        """
        endpoint = f"transaction-builder/{transaction_id}/submit"
        return self.post(endpoint)

    def update_title_contract(
        self, transaction_id: str, title_contract_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update title contract information.

        Args:
            transaction_id: Transaction builder ID
            title_contract_info: Title contract information data

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/title-contract"
        return self.put(endpoint, json_data=title_contract_info)

    def mortgage_ecp_opt_out(self, transaction_id: str) -> Dict[str, Any]:
        """Opt out of mortgage ECP for transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/mortgage-ecp-opt-out"
        return self.put(endpoint)

    def mortgage_ecp_opt_in(self, transaction_id: str) -> Dict[str, Any]:
        """Opt in to mortgage ECP for transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/mortgage-ecp-opt-in"
        return self.put(endpoint)

    # DELETE endpoints
    def delete_transaction_builder(self, transaction_id: str) -> Dict[str, Any]:
        """Delete transaction builder.

        Args:
            transaction_id: Transaction builder ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}"
        return self.delete(endpoint)

    # Individual resource endpoints
    def get_seller(self, transaction_id: str, seller_id: str) -> Dict[str, Any]:
        """Get specific seller information.

        Args:
            transaction_id: Transaction builder ID
            seller_id: Seller ID

        Returns:
            Seller data
        """
        endpoint = f"transaction-builder/{transaction_id}/seller/{seller_id}"
        return self.get(endpoint)

    def update_seller(
        self, transaction_id: str, seller_id: str, seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific seller information.

        Args:
            transaction_id: Transaction builder ID
            seller_id: Seller ID
            seller_info: Updated seller information

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/seller/{seller_id}"
        return self.put(endpoint, json_data=seller_info)

    def delete_seller(self, transaction_id: str, seller_id: str) -> Dict[str, Any]:
        """Delete specific seller.

        Args:
            transaction_id: Transaction builder ID
            seller_id: Seller ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}/seller/{seller_id}"
        return self.delete(endpoint)

    def get_referral_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get specific referral participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Referral participant data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/referral-info/{participant_id}"
        )
        return self.get(endpoint)

    def update_referral_participant(
        self, transaction_id: str, participant_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific referral participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID
            participant_info: Updated participant information

        Returns:
            Transaction builder response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/referral-info/{participant_id}"
        )
        return self.put(endpoint, json_data=participant_info)

    def delete_referral_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Delete specific referral participant.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Deletion response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/referral-info/{participant_id}"
        )
        return self.delete(endpoint)

    def get_other_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Get specific other participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Other participant data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/other-participants/{participant_id}"
        )
        return self.get(endpoint)

    def update_other_participant(
        self, transaction_id: str, participant_id: str, participant_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific other participant information.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID
            participant_info: Updated participant information

        Returns:
            Transaction builder response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/other-participants/{participant_id}"
        )
        return self.put(endpoint, json_data=participant_info)

    def delete_other_participant(
        self, transaction_id: str, participant_id: str
    ) -> Dict[str, Any]:
        """Delete specific other participant.

        Args:
            transaction_id: Transaction builder ID
            participant_id: Participant ID

        Returns:
            Deletion response data
        """
        endpoint = (
            f"transaction-builder/{transaction_id}/other-participants/{participant_id}"
        )
        return self.delete(endpoint)

    def get_co_agent(self, transaction_id: str, co_agent_id: str) -> Dict[str, Any]:
        """Get specific co-agent information.

        Args:
            transaction_id: Transaction builder ID
            co_agent_id: Co-agent ID

        Returns:
            Co-agent data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent/{co_agent_id}"
        return self.get(endpoint)

    def update_co_agent(
        self, transaction_id: str, co_agent_id: str, co_agent_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific co-agent information.

        Args:
            transaction_id: Transaction builder ID
            co_agent_id: Co-agent ID
            co_agent_info: Updated co-agent information

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent/{co_agent_id}"
        return self.put(endpoint, json_data=co_agent_info)

    def delete_co_agent(self, transaction_id: str, co_agent_id: str) -> Dict[str, Any]:
        """Delete specific co-agent.

        Args:
            transaction_id: Transaction builder ID
            co_agent_id: Co-agent ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}/co-agent/{co_agent_id}"
        return self.delete(endpoint)

    def get_buyer(self, transaction_id: str, buyer_id: str) -> Dict[str, Any]:
        """Get specific buyer information.

        Args:
            transaction_id: Transaction builder ID
            buyer_id: Buyer ID

        Returns:
            Buyer data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer/{buyer_id}"
        return self.get(endpoint)

    def update_buyer(
        self, transaction_id: str, buyer_id: str, buyer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update specific buyer information.

        Args:
            transaction_id: Transaction builder ID
            buyer_id: Buyer ID
            buyer_info: Updated buyer information

        Returns:
            Transaction builder response data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer/{buyer_id}"
        return self.put(endpoint, json_data=buyer_info)

    def delete_buyer(self, transaction_id: str, buyer_id: str) -> Dict[str, Any]:
        """Delete specific buyer.

        Args:
            transaction_id: Transaction builder ID
            buyer_id: Buyer ID

        Returns:
            Deletion response data
        """
        endpoint = f"transaction-builder/{transaction_id}/buyer/{buyer_id}"
        return self.delete(endpoint)

    # Backward compatibility aliases
    def put_buyer_to_draft(
        self, transaction_id: str, buyer_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new buyer (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            buyer_info: Buyer information data

        Returns:
            Transaction builder response data
        """
        return self.add_buyer(transaction_id, buyer_info)

    def put_seller_to_draft(
        self, transaction_id: str, seller_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a new seller (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            seller_info: Seller information data

        Returns:
            Transaction builder response data
        """
        return self.add_seller(transaction_id, seller_info)

    def put_location_to_draft(
        self, transaction_id: str, location_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update location information (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            location_info: Location information data

        Returns:
            Transaction builder response data
        """
        return self.update_location_info(transaction_id, location_info)

    def put_price_and_date_to_draft(
        self, transaction_id: str, price_date_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update price and date information (backward compatibility alias).

        Args:
            transaction_id: Transaction builder ID
            price_date_info: Price and date information data

        Returns:
            Transaction builder response data
        """
        return self.update_price_and_date_info(transaction_id, price_date_info)

    def update_commission_payer(
        self, transaction_id: str, commission_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update commission payer information (alias for add_commission_payer).

        Args:
            transaction_id: Transaction builder ID
            commission_info: Commission payer information data

        Returns:
            Transaction builder response data
        """
        return self.add_commission_payer(transaction_id, commission_info)

    def update_personal_deal(
        self, transaction_id: str, deal_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update personal deal (alias for update_personal_deal_info).

        Args:
            transaction_id: Transaction builder ID
            deal_info: Personal deal information data

        Returns:
            Transaction builder response data
        """
        return self.update_personal_deal_info(transaction_id, deal_info)

    def update_real_title(
        self, transaction_id: str, title_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update real title (alias for update_title_info).

        Args:
            transaction_id: Transaction builder ID
            title_info: Title information data

        Returns:
            Transaction builder response data
        """
        return self.update_title_info(transaction_id, title_info)

    def set_current_user_as_owner_agent(
        self, transaction_builder_id: str, role: str, users_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Set the current authenticated user as the owner agent with default team.

        ✅ WORKING CONVENIENCE METHOD

        ⚠️ **MULTIPLE TEAMS WARNING** ⚠️
        If you belong to multiple teams, this method will use your DEFAULT team (prefers LEADER role).
        To specify a particular team, use `set_current_user_as_owner_agent_with_team()` instead.

        This is a convenience method that automatically:
        1. Gets current user information (user ID and office ID)
        2. Determines default team using smart logic
        3. Sets up owner agent with all required fields

        🎯 SMART DEFAULT TEAM LOGIC:
        - Prefers teams where you have LEADER role
        - Falls back to teams where you have ADMIN role
        - Uses first available team as last resort

        Args:
            transaction_builder_id: UUID of the transaction builder
            role: Agent role ("BUYERS_AGENT" or "SELLERS_AGENT")
            users_client: Optional UsersClient instance. If None, will create one.

        Returns:
            Updated transaction builder data

        Raises:
            ValidationError: If owner agent info is invalid or user has no teams
            NotFoundError: If transaction builder not found
            AuthenticationError: If not authenticated
            ValueError: If user has no offices

        Example:
            ```python
            # Simple case - uses default team automatically
            result = client.transaction_builder.set_current_user_as_owner_agent(
                builder_id,
                "BUYERS_AGENT"
            )

            # For multiple teams - check first, then choose approach
            teams_info = client.transaction_builder.get_user_teams_and_offices()

            if teams_info["has_multiple_teams"]:
                print(f"You have {len(teams_info['teams'])} teams.")
                print(f"Will use default: {teams_info['default_team']['name']}")

                # Option 1: Use this method with default team
                result = client.transaction_builder.set_current_user_as_owner_agent(
                    builder_id, "BUYERS_AGENT"
                )

                # Option 2: Specify team explicitly
                # result = client.transaction_builder.set_current_user_as_owner_agent_with_team(
                #     builder_id, "BUYERS_AGENT", teams_info["teams"][1]["id"]
                # )
            else:
                # Single team - use this convenience method
                result = client.transaction_builder.set_current_user_as_owner_agent(
                    builder_id, "BUYERS_AGENT"
                )
            ```
        """
        # Import here to avoid circular imports
        if users_client is None:
            from .users import UsersClient

            users_client = UsersClient(api_key=self.api_key)

        # Get current user information
        user = users_client.get_current_user()

        # Check for multiple teams and warn
        user_teams = user.get("teams", [])
        if len(user_teams) > 1:
            team_names = [f"{t['teamName']} ({t['teamId']})" for t in user_teams]
            print(
                f"⚠️  WARNING: You belong to {len(user_teams)} teams: {', '.join(team_names)}"
            )
            print(
                f"Using default team. To specify a team, use set_current_user_as_owner_agent_with_team()"
            )

        # Use user ID as agent ID (they are equivalent in this system)
        agent_id = user["id"]

        # Use default team selection logic
        teams_info = self.get_user_teams_and_offices(users_client)
        if not teams_info["default_team"]:
            raise ValidationError(
                "User must belong to at least one team to be set as owner agent"
            )

        # Build owner agent info with default team
        owner_info = {
            "ownerAgent": {"agentId": agent_id, "role": role},
            "teamId": teams_info["default_team"]["id"],
        }

        # Get office ID from user's offices
        offices = user.get("offices", [])
        if offices:
            office_id = offices[0]["id"]  # Use the first office
            owner_info["officeId"] = office_id
        else:
            raise ValidationError(
                "User has no offices available. Cannot determine office ID for transaction creation."
            )

        return self.update_owner_agent_info(transaction_builder_id, owner_info)

    def get_user_teams_and_offices(
        self, users_client: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Get current user's teams and offices with smart default selection.

        ✅ WORKING METHOD - Handles multiple team scenarios automatically.

        This method helps handle users who belong to multiple teams by:
        1. Fetching all teams the user belongs to
        2. Determining a smart default team (prefers LEADER role over ADMIN)
        3. Extracting office information from user profile
        4. Providing clear guidance on team selection

        🎯 SMART DEFAULT LOGIC:
        - If user has LEADER role in any team → that team becomes default
        - If user only has ADMIN roles → first ADMIN team becomes default
        - If user has only one team → that team becomes default

        💡 USE CASES:
        - Check if user needs team selection before transaction creation
        - Get default team for automatic owner agent setup
        - Display available teams for user selection

        Args:
            users_client: Optional users client instance (uses parent client if None)

        Returns:
            Dictionary containing:
            - user: Full user profile data with offices array
            - teams: List of teams user belongs to with roles
            - offices: List of offices user belongs to
            - default_team: Recommended team (smart selection)
            - has_multiple_teams: Boolean indicating if user has multiple teams
            - team_selection_needed: Boolean indicating if explicit selection recommended
            - agent_id: User's agent ID (same as user ID)
            - office_id: Primary office ID from user.offices[0].id

        Example:
            ```python
            info = client.transaction_builder.get_user_teams_and_offices()

            print(f"Agent ID: {info['agent_id']}")
            print(f"Office ID: {info['office_id']}")

            if info["has_multiple_teams"]:
                print("\\nAvailable teams:")
                for team in info["teams"]:
                    role = team["role"]
                    name = team["name"]
                    is_default = team["id"] == info["default_team"]["id"]
                    marker = " (DEFAULT)" if is_default else ""
                    print(f"  - {name} (Role: {role}){marker}")

                # Use default team or let user choose
                selected_team = info["default_team"]
                print(f"\\nUsing default team: {selected_team['name']}")
            else:
                print(f"Single team: {info['default_team']['name']}")

            # Ready-to-use IDs for transaction setup
            team_id = info["default_team"]["id"]
            office_id = info["office_id"]
            agent_id = info["agent_id"]
            ```

        Team Data Structure:
            Each team in the teams list contains:
            - id: Team UUID
            - name: Team name
            - role: User's role in the team ("LEADER", "ADMIN", etc.)

        Raises:
            APIError: If user data cannot be retrieved
            ValueError: If user has no offices (required for transactions)
        """
        # Import here to avoid circular imports
        if users_client is None:
            from .users import UsersClient

            users_client = UsersClient(api_key=self.api_key)

        # Get current user information
        user = users_client.get_current_user()

        # Get teams from user data (they're included in the user profile)
        raw_teams = user.get("teams", [])

        # Transform teams to our standard format
        teams = []
        for team in raw_teams:
            # Determine the user's primary role in this team
            team_roles = team.get("teamRoles", [])
            primary_role = team_roles[0] if team_roles else "MEMBER"

            teams.append(
                {
                    "id": team["teamId"],
                    "name": team["teamName"],
                    "role": primary_role,
                    "type": team.get("teamType", "NORMAL"),
                    "raw_data": team,  # Keep original data for reference
                }
            )

        # Extract office information
        offices = user.get("offices", [])
        if not offices:
            raise ValueError(
                "User has no offices. Office information is required for transactions."
            )

        # Determine default team with smart logic
        default_team = None
        leader_teams = []
        admin_teams = []

        # Categorize teams by role
        for team in teams:
            if team.get("role") == "LEADER":
                leader_teams.append(team)
            elif team.get("role") == "ADMIN":
                admin_teams.append(team)

        # Smart default selection
        if leader_teams:
            default_team = leader_teams[0]  # Prefer first LEADER team
        elif admin_teams:
            default_team = admin_teams[0]  # Fallback to first ADMIN team
        elif teams:
            default_team = teams[0]  # Last resort: first team

        return {
            "user": user,
            "teams": teams,
            "offices": offices,
            "default_team": default_team,
            "has_multiple_teams": len(teams) > 1,
            "team_selection_needed": len(teams) > 1,
            "agent_id": user["id"],  # User ID = Agent ID in ReZEN
            "office_id": offices[0]["id"],  # Primary office
        }

    def set_current_user_as_owner_agent_with_team(
        self,
        transaction_builder_id: str,
        role: str,
        team_id: str,
        users_client: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Set current user as owner agent with explicit team selection.

        ✅ WORKING CONVENIENCE METHOD

        This method allows users to specify which team to use when they belong
        to multiple teams. This gives full control over team selection and is
        recommended when you need to be explicit about which team to use.

        🎯 PERFECT FOR:
        - Users who belong to multiple teams
        - When you need specific team for business reasons
        - Programmatic team selection based on criteria

        This method automatically:
        1. Gets current user information (user ID and office ID)
        2. Validates the user belongs to the specified team
        3. Sets up owner agent with all required fields

        Args:
            transaction_builder_id: UUID of the transaction builder
            role: Agent role ("BUYERS_AGENT" or "SELLERS_AGENT")
            team_id: Specific team ID to use for the transaction
            users_client: Optional UsersClient instance. If None, will create one.

        Returns:
            Updated transaction builder data

        Raises:
            ValidationError: If user is not a member of the specified team
            ValidationError: If team_id is invalid
            NotFoundError: If transaction builder not found
            AuthenticationError: If not authenticated
            ValueError: If user has no offices

        Example:
            ```python
            # Option 1: Get available teams and choose
            teams_info = client.transaction_builder.get_user_teams_and_offices()

            if teams_info["has_multiple_teams"]:
                print("Available teams:")
                for team in teams_info["teams"]:
                    print(f"  {team['name']} (ID: {team['id']}, Role: {team['role']})")

                # Choose a specific team (e.g., select LEADER team)
                leader_teams = [t for t in teams_info["teams"] if t["role"] == "LEADER"]
                selected_team_id = leader_teams[0]["id"] if leader_teams else teams_info["teams"][0]["id"]
            else:
                selected_team_id = teams_info["default_team"]["id"]

            # Set owner agent with specific team
            result = client.transaction_builder.set_current_user_as_owner_agent_with_team(
                builder_id,
                role="BUYERS_AGENT",
                team_id=selected_team_id
            )

            # Option 2: Direct usage if you know the team ID
            result = client.transaction_builder.set_current_user_as_owner_agent_with_team(
                builder_id,
                role="SELLERS_AGENT",
                team_id="12345678-1234-1234-1234-123456789012"
            )
            ```
        """
        # Import here to avoid circular imports
        if users_client is None:
            from .users import UsersClient

            users_client = UsersClient(api_key=self.api_key)

        # Get current user information
        user = users_client.get_current_user()

        # Validate that user is member of specified team
        user_teams = user.get("teams", [])
        selected_team = None
        for team in user_teams:
            if team["teamId"] == team_id:
                selected_team = team
                break

        if not selected_team:
            available_team_ids = [t["teamId"] for t in user_teams]
            raise ValidationError(
                f"User is not a member of team '{team_id}'. "
                f"Available teams: {available_team_ids}"
            )

        # Use user ID as agent ID (they are equivalent in this system)
        agent_id = user["id"]

        # Build owner agent info with specified team
        owner_info = {
            "ownerAgent": {"agentId": agent_id, "role": role},
            "teamId": team_id,
        }

        # Get office ID from user's offices
        offices = user.get("offices", [])
        if offices:
            office_id = offices[0]["id"]  # Use the first office
            owner_info["officeId"] = office_id
        else:
            raise ValidationError(
                "User has no offices available. Cannot determine office ID for transaction creation."
            )

        return self.update_owner_agent_info(transaction_builder_id, owner_info)

    def create_complete_transaction_example(self) -> str:
        """Returns a complete working example of creating and submitting a transaction.

        This method provides documentation showing the EXACT workflow that has been
        proven to work in production based on real-world usage.

        Returns:
            str: Complete working example code
        """
        return """
        # COMPLETE WORKING TRANSACTION SUBMISSION EXAMPLE
        # Based on production-proven workflow
        
        # Step 1: Create transaction builder
        builder_response = client.transaction_builder.create_transaction_builder()
        transaction_id = builder_response["id"]
        
        # Step 2: Add location info (ALL fields required)
        location_info = {
            "street": "123 Main Street",
            "city": "Salt Lake City",
            "state": "UTAH",  # Must be ALL CAPS
            "zip": "84101",
            "county": "Salt Lake",      # REQUIRED
            "yearBuilt": 2020,         # REQUIRED
            "mlsNumber": "MLS123456"   # REQUIRED
        }
        client.transaction_builder.update_location_info(transaction_id, location_info)
        
        # Step 3: Add price/date info with BOTH commissions
        price_data = {
            "dealType": "SALE",  # NOT "COMPENSATING"!
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 500000, "currency": "USD"},
            "representationType": "BUYER",
            "listingCommission": {  # REQUIRED even for buyer deals
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False  # CRITICAL!
            },
            "saleCommission": {  # REQUIRED even for buyer deals
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False  # CRITICAL!
            },
            "acceptanceDate": "2024-01-15",
            "closingDate": "2024-02-28"
        }
        client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
        
        # Step 4: Add buyer
        buyer_info = {
            "firstName": "John",
            "lastName": "Buyer",
            "email": "john@example.com",
            "phoneNumber": "1(801) 555-1234"  # Country code required!
        }
        client.transaction_builder.add_buyer(transaction_id, buyer_info)
        
        # Step 5: Add seller (REQUIRED even for buyer representation!)
        seller_info = {
            "firstName": "Jane",
            "lastName": "Seller",
            "email": "jane@example.com",
            "phoneNumber": "1(801) 555-9876"  # Country code required!
        }
        client.transaction_builder.add_seller(transaction_id, seller_info)
        
        # Step 6: Add owner agent
        user = client.users.get_current_user()
        owner_info = {
            "ownerAgent": {
                "agentId": user["id"],
                "role": "BUYERS_AGENT"  # Must match representationType
            },
            "officeId": user["offices"][0]["id"],
            "teamId": "your-team-uuid"
        }
        client.transaction_builder.update_owner_agent_info(transaction_id, owner_info)
        
        # Step 7: Get transaction to find participant IDs (CRITICAL!)
        transaction = client.transaction_builder.get_transaction_builder(transaction_id)
        
        # Find owner agent participant ID
        owner_participant_id = None
        for agent in transaction["agentsInfo"]["ownerAgent"]:
            if agent["agentId"] == user["id"]:
                owner_participant_id = agent["id"]  # This is participant ID!
                break
        
        # Step 8: Add commission splits using PARTICIPANT IDs
        commission_splits = [{
            "participantId": owner_participant_id,  # NOT agentId!
            "commission": {
                "commissionPercent": 100.0,
                "percentEnabled": True,
                "negativeOrEmpty": False
            }
        }]
        client.transaction_builder.update_commission_splits(transaction_id, commission_splits)
        
        # Step 9: Add commission payer (title company)
        commission_payer = {
            "role": "TITLE",
            "firstName": "ABC",
            "lastName": "Title",
            "email": "closing@abctitle.com",
            "phoneNumber": "1(801) 555-5555",
            "companyName": "ABC Title Company",
            "receivesInvoice": True
        }
        client.transaction_builder.add_commission_payer(transaction_id, commission_payer)
        
        # Step 10: Submit transaction
        result = client.transaction_builder.submit_transaction(transaction_id)
        
        # The transaction is now created!
        # result contains the preview data of the submitted transaction
        """
