# Transaction Builder API

Create and manage transaction builders with full participant and property management capabilities.

---

## Overview

!!! abstract "Transaction Builder Workflow"

    The Transaction Builder API allows you to:

    - **Create** new transaction builders for various types of real estate transactions
    - **Configure** property details, participants, and financial information
    - **Manage** buyers, sellers, agents, and other transaction participants
    - **Submit** completed transactions for processing
    - **Convert** listings to transactions
    - **Backward Compatibility** with legacy method names

!!! danger "🚨 CRITICAL API REQUIREMENTS"

    **These requirements are MANDATORY for successful API calls:**

    **Location Updates:**
    - Basic address fields (street, city, state, zip) alone will **FAIL**
    - Additional fields are **REQUIRED**: `county`, `yearBuilt`, `mlsNumber`

    **Price/Date Updates:**
    - Basic price fields alone will **FAIL**
    - **BOTH** commission objects are **REQUIRED**: `listingCommission` AND `saleCommission`
    - Commission objects MUST include `negativeOrEmpty: false` field

    **Commission Splits:**
    - ⚠️ **CRITICAL**: Use PARTICIPANT IDs, not agent IDs!
    - After adding agents, retrieve the transaction to get participant IDs
    - Commission splits are REQUIRED before submission

    **Co-Agent Roles:**
    - ✅ Working: `"REAL"`, `"BUYERS_AGENT"`, `"SELLERS_AGENT"`
    - ❌ Fails: `"LISTING_AGENT"`

    **Owner Agents:**
    - Require specific sequence: location → price/date → participants → owner agent
    - Need valid `officeId` and `teamId`

    **Transaction Types:**
    - Only two types available for draft stage: `"SALE"` or `"LEASE"`
    - Deal type (SALE/LEASE) is independent of representation type (BUYER/SELLER/DUAL)
    - `dealType` refers to the type of real estate transaction
    - `representationType` refers to which party the agent represents
    
    **Submission Requirements:**
    - Commission splits MUST be populated (error: "commissionSplitsInfo cannot be empty")
    - Commission payer (usually title company) is REQUIRED
    - Both buyer AND seller must be added (even for buyer-only representation)

---

## Quick Start

=== "🚀 Basic Transaction"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Step 1: Create transaction builder
    transaction_id: str = client.transaction_builder.create_transaction_builder()

    # Step 2: Add property information - CRITICAL REQUIREMENTS
    # ⚠️ Additional fields beyond basic address are REQUIRED
    location_data: Dict[str, Any] = {
        "street": "123 Main Street",  # Use 'street' not 'address'
        "city": "Salt Lake City",
        "state": "UTAH",  # MUST BE ALL CAPS
        "zip": "84101",   # Use 'zip' not 'zipCode'
        "county": "Salt Lake",      # REQUIRED - API fails without this
        "yearBuilt": 2020,         # REQUIRED - API fails without this
        "mlsNumber": "MLS123456"   # REQUIRED - API fails without this
    }
    client.transaction_builder.update_location_info(transaction_id, location_data)

    # Step 3: Add price/date information - CRITICAL REQUIREMENTS
    # ⚠️ BOTH commission objects are REQUIRED together
    
    # Option 1: Using the helper method (recommended)
    price_data = client.transaction_builder.prepare_price_and_date_data(
        sale_price=500000,
        representation_type="BUYER"
    )
    client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
    
    # Option 2: Manual construction (if you need full control)
    # price_data: Dict[str, Any] = {
    #     "dealType": "SALE",
    #     "propertyType": "RESIDENTIAL",
    #     "salePrice": {"amount": 500000, "currency": "USD"},
    #     "representationType": "BUYER",
    #     "listingCommission": {     # REQUIRED - cannot omit
    #         "commissionPercent": 3.0,
    #         "percentEnabled": True,
    #         "negativeOrEmpty": False
    #     },
    #     "saleCommission": {        # REQUIRED - cannot omit
    #         "commissionPercent": 3.0,
    #         "percentEnabled": True,
    #         "negativeOrEmpty": False
    #     }
    # }
    # client.transaction_builder.update_price_and_date_info(transaction_id, price_data)

    # Step 4: Add participants (use camelCase)
    buyer_data: Dict[str, Any] = {
        "firstName": "John",  # Use camelCase
        "lastName": "Doe",    # Use camelCase
        "email": "john.doe@email.com",
        "phoneNumber": "(555) 123-4567"  # Use camelCase
    }
    client.transaction_builder.add_buyer(transaction_id, buyer_data)

    # Step 5: Add co-agent (working roles only)
    co_agent_data: Dict[str, Any] = {
        "agentId": "bd465129-b224-43e3-b92f-524ea5f53783",
        "role": "REAL",  # ✅ Working role
        "receivesInvoice": False
    }
    client.transaction_builder.add_co_agent(transaction_id, co_agent_data)

    # Step 6: Submit transaction
    client.transaction_builder.submit_transaction(transaction_id)
    ```

=== "🏠 Listing Builder"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Create listing builder using dedicated method
    listing_id: str = client.transaction_builder.create_listing_builder()

    # Configure listing-specific details (use camelCase)
    seller_data: Dict[str, Any] = {
        "firstName": "Jane",      # Use camelCase
        "lastName": "Smith",      # Use camelCase
        "email": "jane.smith@email.com",
        "phoneNumber": "(555) 987-6543"  # Use camelCase
    }
    client.transaction_builder.add_seller(listing_id, seller_data)
    ```

=== "🔄 Convert Listing"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Convert existing listing to transaction
    listing_id: str = "existing-listing-id"
    response: Dict[str, Any] = client.transaction_builder.convert_listing_to_transaction(listing_id)
    transaction_id: str = response['id']
    print(f"Converted listing {listing_id} to transaction {transaction_id}")
    ```

---

## Core Transaction Management

### Create Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.create_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! note "Consistent Response Format"
    The method now returns a consistent `{"id": "transaction_id"}` format instead of a raw string.

### Create Listing Builder

::: rezen.transaction_builder.TransactionBuilderClient.create_listing_builder
    options:
      show_source: false
      heading_level: 4

!!! tip "Convenience Method"
    This is a wrapper around `create_transaction_builder(builder_type='LISTING')` for easier listing creation.

### Convert Listing to Transaction

::: rezen.transaction_builder.TransactionBuilderClient.convert_listing_to_transaction
    options:
      show_source: false
      heading_level: 4

!!! example "Create Different Builder Types"

    === "Transaction Builder"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Standard transaction builder
        response: Dict[str, Any] = client.transaction_builder.create_transaction_builder()
        print(f"Transaction ID: {response['id']}")
        # Returns: {"id": "transaction-id-here"}
        ```

    === "Listing Builder"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Using dedicated listing builder method
        response: Dict[str, Any] = client.transaction_builder.create_listing_builder()
        print(f"Listing ID: {response['id']}")
        ```

    === "Convert Existing Listing"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Convert listing to transaction
        listing_id = "existing-listing-id"
        response: Dict[str, Any] = client.transaction_builder.convert_listing_to_transaction(listing_id)
        print(f"New transaction ID: {response['id']}")
        ```

### Get Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.get_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! tip "Response Structure"

    The transaction builder response includes:

    - **Basic Information**: ID, type, status, creation date
    - **Participants**: All buyers, sellers, agents, and other participants
    - **Property Details**: Location, pricing, and property information
    - **Financial Data**: Commission splits and payment information

### Submit Transaction

::: rezen.transaction_builder.TransactionBuilderClient.submit_transaction
    options:
      show_source: false
      heading_level: 4

!!! warning "Submission Requirements"

    Before submitting, ensure:

    - [ ] At least one participant is added
    - [ ] Property location is specified
    - [ ] Required financial information is complete
    - [ ] All mandatory fields are populated

### Delete Transaction Builder

::: rezen.transaction_builder.TransactionBuilderClient.delete_transaction_builder
    options:
      show_source: false
      heading_level: 4

!!! danger "Deletion Warning"

    This operation is irreversible. Ensure you have backups of any critical data before deletion.

---

## Participant Management

### Buyers

=== "➕👤 Add Buyer"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_buyer
        options:
          show_source: false
          heading_level: 5

    **Required Buyer Fields:**

    | Field | Type | Description |
    |-------|------|-------------|
    | `firstName` | `str` | Buyer's first name (camelCase) |
    | `lastName` | `str` | Buyer's last name (camelCase) |
    | `email` | `str` | Valid email address |
    | `phoneNumber` | `str` | Phone number with country code (camelCase) |
    | `company` | `str` | Company name |
    | `address` | `str` | Mailing address |

    !!! warning "Phone Number Formatting"
        
        **All phone numbers MUST include the country code (1 for US)**:
        
        - ✅ Good: `"1(801) 555-1234"`, `"+1-801-555-1234"`, `"1-801-555-1234"`
        - ❌ Bad: `"(801) 555-1234"`, `"801-555-1234"`, `"555-1234"`
        
        The API requires phone numbers to start with the country code for proper validation.

    !!! example "Complete Buyer Example"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        buyer_data: Dict[str, Any] = {
            "firstName": "John",  # Use camelCase
            "lastName": "Doe",  # Use camelCase
            "email": "john.doe@email.com",
            "phoneNumber": "+1-555-123-4567",  # Use camelCase
            "company": "Doe Enterprises",
            "address": "456 Business Ave, Business City, BC 12345"
        }

        # Using new method name
        response: Dict[str, Any] = client.transaction_builder.add_buyer(transaction_id, buyer_data)
        
        # Or using backward compatibility alias
        response: Dict[str, Any] = client.transaction_builder.put_buyer_to_draft(transaction_id, buyer_data)
        ```

### Sellers

=== "➖👤 Add Seller"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_seller
        options:
          show_source: false
          heading_level: 5

    !!! example "Seller Configuration"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        seller_data: Dict[str, Any] = {
            "firstName": "Jane",  # Use camelCase
            "lastName": "Smith",  # Use camelCase
            "email": "jane.smith@email.com",
            "phoneNumber": "+1-555-987-6543"  # Use camelCase
        }

        # Using new method name
        response: Dict[str, Any] = client.transaction_builder.add_seller(transaction_id, seller_data)
        
        # Or using backward compatibility alias
        response: Dict[str, Any] = client.transaction_builder.put_seller_to_draft(transaction_id, seller_data)
        ```

### Agents & Co-Agents

=== "👔 Add Co-Agent"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_co_agent
        options:
          show_source: false
          heading_level: 5

    **Agent Roles:**

    !!! info "Available Agent Roles"

        - `BUYERS_AGENT`: Represents the buyer
        - `SELLERS_AGENT`: Represents the seller
        - `LISTING_AGENT`: Lists the property
        - `DUAL_AGENT`: Represents both parties

    !!! example "Co-Agent Examples"

        === "Buyer's Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            co_agent_data: Dict[str, Any] = {
                "agent_id": "agent-uuid-here",
                "role": "BUYERS_AGENT"
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
            ```

        === "Seller's Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            co_agent_data: Dict[str, Any] = {
                "agent_id": "seller-agent-uuid",
                "role": "SELLERS_AGENT"
            }
            client.transaction_builder.add_co_agent(transaction_id, co_agent_data)
            ```

### Owner Agents

=== "⭐👤 Update Owner Agent"

    ::: rezen.transaction_builder.TransactionBuilderClient.update_owner_agent_info
        options:
          show_source: false
          heading_level: 5

### Multiple Teams Support

!!! success "✅ New Feature: Multiple Teams Support"

    Many ReZEN users belong to multiple teams. These convenience methods help handle team selection automatically:

=== "👥 Get Teams & Offices"

    ::: rezen.transaction_builder.TransactionBuilderClient.get_user_teams_and_offices
        options:
          show_source: false
          heading_level: 5

    **Smart Default Logic:**
    - Prefers teams where you have **LEADER** role
    - Falls back to **ADMIN** teams
    - Uses first available team as last resort

=== "⭐👤 Set Owner Agent (Default Team)"

    ::: rezen.transaction_builder.TransactionBuilderClient.set_current_user_as_owner_agent
        options:
          show_source: false
          heading_level: 5

    **Best for:** Users with single team or who want automatic team selection.

=== "✅👤 Set Owner Agent (Specific Team)"

    ::: rezen.transaction_builder.TransactionBuilderClient.set_current_user_as_owner_agent_with_team
        options:
          show_source: false
          heading_level: 5

    **Best for:** Users with multiple teams who need explicit control.

    !!! danger "Prerequisites Required"

        **CRITICAL**: The owner agent endpoint requires the transaction to be properly set up BEFORE adding agents:

        1. **Location info** must be added first (`update_location_info`)
        2. **Price and date info** must be added second (`update_price_and_date_info`) 
        3. **Buyers/Sellers** must be added third (`add_buyer`/`add_seller`)
        4. **THEN** owner agent can be added successfully

    **Owner Data Structure:**
    ```python
    {
        "ownerAgent": {
            "agentId": "agent_uuid",
            "role": "BUYERS_AGENT"  # or "SELLERS_AGENT"
        },
        "officeId": "office_uuid", 
        "teamId": "team_uuid"
    }
    ```

    !!! tip "Multiple Teams Support"

        **New in ReZEN**: If you belong to multiple teams, use the enhanced methods:
        
        - `get_user_teams_and_offices()` - Discover available teams
        - `set_current_user_as_owner_agent_with_team()` - Specify exact team
        
        See [Multiple Teams Guide](../guides/transactions.md#handling-multiple-teams-offices) for details.

    !!! example "Complete Working Example"

        === "Manual Owner Agent"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()

            # Step 1: Create transaction
            builder_id = client.transaction_builder.create_transaction_builder()

            # Step 2: Add location (REQUIRED FIRST)
            location_data: Dict[str, Any] = {
                "street": "123 Main St",
                "city": "Salt Lake City", 
                "state": "UTAH",
                "zip": "84101"
            }
            client.transaction_builder.update_location_info(builder_id, location_data)

            # Step 3: Add price/date info (REQUIRED SECOND)
            price_data: Dict[str, Any] = {
                "dealType": "SALE",
                "propertyType": "RESIDENTIAL", 
                "salePrice": {"amount": 500000, "currency": "USD"},
                "representationType": "BUYER"  # Must match agent role
            }
            client.transaction_builder.update_price_and_date_info(builder_id, price_data)

            # Step 4: Add clients (REQUIRED THIRD)
            client.transaction_builder.add_buyer(builder_id, {
                "firstName": "John",
                "lastName": "Doe",
                "email": "john@example.com",
                "phoneNumber": "1(801) 555-1234"  # Include country code!
            })

            # Step 5: NOW add owner agent (will work!)
            owner_data: Dict[str, Any] = {
                "ownerAgent": {
                    "agentId": "your_agent_id",
                    "role": "BUYERS_AGENT"  # Must match representationType
                },
                "officeId": "your_office_id",
                "teamId": "your_team_id"
            }
            client.transaction_builder.update_owner_agent_info(builder_id, owner_data)
            ```

        === "Current User as Owner"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()

            # Set up transaction (same steps 1-4 as above)
            builder_id = client.transaction_builder.create_transaction_builder()
            # ... add location, price, and clients ...

            # Use convenience method for current user
            client.transaction_builder.set_current_user_as_owner_agent(
                builder_id, 
                role="BUYERS_AGENT"
            )
            ```

    !!! warning "Role Matching"
        
        The `role` in `ownerAgent` must match the `representationType` in the price/date info:
        
        - `representationType: "BUYER"` → `role: "BUYERS_AGENT"`
        - `representationType: "SELLER"` → `role: "SELLERS_AGENT"`

### Other Participants

=== "👥 Add Participant"

    ::: rezen.transaction_builder.TransactionBuilderClient.add_participant
        options:
          show_source: false
          heading_level: 5

    **Participant Types:**

    | Type | Description |
    |------|-------------|
    | `INSPECTOR` | Property inspector |
    | `APPRAISER` | Property appraiser |
    | `LENDER` | Mortgage lender |
    | `TITLE_COMPANY` | Title company representative |
    | `ATTORNEY` | Legal counsel |
    | `CONTRACTOR` | Contractor or repair specialist |

    !!! example "Service Provider Examples"

        === "Property Inspector"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            inspector_data: Dict[str, Any] = {
                "type": "INSPECTOR",
                "firstName": "Mike",  # Use camelCase
                "lastName": "Inspector",  # Use camelCase
                "company": "Quality Inspections Inc",
                "phoneNumber": "+1-555-INSPECT",  # Use camelCase
                "email": "mike@qualityinspections.com"
            }
            client.transaction_builder.add_participant(transaction_id, inspector_data)
            ```

        === "Mortgage Lender"

            ```python
            from typing import Dict, Any

            from rezen import RezenClient

            client: RezenClient = RezenClient()
            transaction_id: str = "your-transaction-id-here"

            lender_data: Dict[str, Any] = {
                "type": "LENDER",
                "firstName": "Sarah",  # Use camelCase
                "lastName": "Banker",  # Use camelCase
                "company": "First National Bank",
                "phoneNumber": "+1-555-LOANS",  # Use camelCase
                "email": "sarah.banker@firstnational.com"
            }
            client.transaction_builder.add_participant(transaction_id, lender_data)
            ```

---

## Property & Location Details

### Location Information

::: rezen.transaction_builder.TransactionBuilderClient.update_location_info
    options:
      show_source: false
      heading_level: 4

!!! note "Backward Compatibility"
    You can also use `put_location_to_draft()` which is an alias for `update_location_info()`.

!!! example "Property Location Examples"

    === "Residential Property"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        location_data: Dict[str, Any] = {
            "street": "123 Maple Street",  # Use 'street' not 'address'
            "street2": "",
            "city": "Springfield",
            "state": "UTAH",  # Must be UTAH (all caps)
            "zip": "84101",  # Use 'zip' not 'zipCode'
            "county": "Salt Lake",
            "unit": "Unit 2A",  # For condos/apartments
            "subdivision": "Maple Grove",
            "yearBuilt": 2020,  # Use camelCase
            "mlsNumber": "MLS123",  # Use camelCase
            "escrowNumber": ""
        }
        
        # Using new method name
        client.transaction_builder.update_location_info(transaction_id, location_data)
        
        # Or using backward compatibility alias
        client.transaction_builder.put_location_to_draft(transaction_id, location_data)
        ```

    === "Commercial Property"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        location_data: Dict[str, Any] = {
            "street": "456 Business Blvd",  # Use 'street' not 'address'
            "street2": "",
            "city": "Commerce City",
            "state": "UTAH",  # Must be UTAH (all caps)
            "zip": "84111",  # Use 'zip' not 'zipCode'
            "county": "Salt Lake",
            "yearBuilt": 2018,
            "mlsNumber": "COM456",
            "escrowNumber": "",
            "building_name": "Commerce Center",
            "floor": "15th Floor"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
        ```

### Pricing & Dates

::: rezen.transaction_builder.TransactionBuilderClient.update_price_and_date_info
    options:
      show_source: false
      heading_level: 4

!!! note "Backward Compatibility"
    You can also use `put_price_and_date_to_draft()` which is an alias for `update_price_and_date_info()`.

**Key Date Fields:**

| Field | Format | Description |
|-------|--------|-------------|
| `contractDate` | `YYYY-MM-DD` | Date contract was signed (camelCase) |
| `closingDate` | `YYYY-MM-DD` | Expected closing date (camelCase) |
| `inspectionDate` | `YYYY-MM-DD` | Property inspection date (camelCase) |
| `appraisalDate` | `YYYY-MM-DD` | Appraisal completion date (camelCase) |
| `acceptanceDate` | `YYYY-MM-DD` | Offer acceptance date (camelCase) |

!!! example "Pricing Information"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    price_date_data: Dict[str, Any] = {
        "salePrice": {  # Use camelCase and object structure
            "amount": 750000,
            "currency": "USD"
        },
        "earnestMoney": 15000,  # Use camelCase
        "downPayment": 150000,  # Use camelCase
        "loanAmount": 600000,  # Use camelCase
        "contractDate": "2024-02-01",  # Use camelCase
        "closingDate": "2024-03-15",  # Use camelCase
        "inspectionDate": "2024-02-10",  # Use camelCase
        "appraisalDate": "2024-02-20"  # Use camelCase
    }

    client.transaction_builder.update_price_and_date_info(
        transaction_id,
        price_date_data
    )
    ```

!!! danger "⚠️ Critical: Updating Dates on Existing Transactions"

    When adding or updating dates (acceptanceDate, closingDate) on a transaction that already has pricing information, you **CANNOT** send just the date fields. The API requires the complete price/date structure for any update to this endpoint.

    **❌ THIS FAILS:**
    ```python
    # Trying to add just dates to existing transaction
    date_update = {
        "acceptanceDate": "2025-06-16",
        "closingDate": "2025-07-16"
    }
    client.transaction_builder.update_price_and_date_info(transaction_id, date_update)
    # Returns: "Missing required fields: dealType, propertyType, salePrice, representationType, listingCommission, saleCommission..."
    ```

    **✅ THIS WORKS:**
    ```python
    # Must include ALL price/date fields, even if just updating dates
    price_date_update = {
        "dealType": "SALE",
        "propertyType": "RESIDENTIAL",
        "salePrice": {"amount": 500000, "currency": "USD"},
        "representationType": "BUYER",
        "listingCommission": {           # REQUIRED even for date updates
            "commissionPercent": 3.0,
            "percentEnabled": True,
            "negativeOrEmpty": False
        },
        "saleCommission": {              # REQUIRED even for date updates
            "commissionPercent": 3.0,
            "percentEnabled": True,
            "negativeOrEmpty": False
        },
        "acceptanceDate": "2025-06-16",  # New date
        "closingDate": "2025-07-16"      # New date
    }
    client.transaction_builder.update_price_and_date_info(transaction_id, price_date_update)
    ```

    **💡 Tip:** If you need to update dates on an existing transaction, first retrieve the current price/date info, then update the date fields while keeping all other required fields intact.

### Helper Method: prepare_price_and_date_data

To simplify creating properly formatted price/date data with all required fields, use the `prepare_price_and_date_data` helper method:

::: rezen.transaction_builder.TransactionBuilderClient.prepare_price_and_date_data
    options:
      show_source: false
      heading_level: 4

!!! success "Benefits of Using the Helper"
    - ✅ Automatically includes both commission objects with `negativeOrEmpty: false`
    - ✅ Properly formats the sale price as an object with amount and currency
    - ✅ Ensures all required fields are present
    - ✅ Provides sensible defaults for commission percentages (3%)
    - ✅ Optional fields are only included when provided

!!! example "Using the Helper Method"

    === "Simple Usage"

        ```python
        from rezen import RezenClient

        client = RezenClient()
        transaction_id = "your-transaction-id"

        # Simple usage with defaults
        price_data = client.transaction_builder.prepare_price_and_date_data(
            sale_price=500000,
            representation_type="BUYER",
            acceptance_date="2024-06-16",
            closing_date="2024-07-16"
        )
        
        # Update the transaction
        result = client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
        ```

    === "Custom Commissions"

        ```python
        # Custom commission percentages
        price_data = client.transaction_builder.prepare_price_and_date_data(
            sale_price=750000,
            representation_type="SELLER",
            listing_commission_percent=2.5,  # Custom 2.5%
            sale_commission_percent=2.5,     # Custom 2.5%
            acceptance_date="2024-06-16",
            closing_date="2024-07-16"
        )
        
        result = client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
        ```

    === "Complete Example"

        ```python
        # All optional fields included
        price_data = client.transaction_builder.prepare_price_and_date_data(
            sale_price=1000000,
            representation_type="BUYER",
            listing_commission_percent=2.75,
            sale_commission_percent=2.75,
            deal_type="SALE",               # Default is "SALE"
            property_type="COMMERCIAL",     # Default is "RESIDENTIAL"
            acceptance_date="2024-06-16",
            closing_date="2024-07-16",
            earnest_money=25000,
            down_payment=200000,
            loan_amount=800000
        )
        
        result = client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
        ```

    **💡 Tip:** This helper method is especially useful when you need to update dates on an existing transaction, as it ensures all required fields are included.

### Title Information

::: rezen.transaction_builder.TransactionBuilderClient.update_title_info
    options:
      show_source: false
      heading_level: 4

### Update Real Title

::: rezen.transaction_builder.TransactionBuilderClient.update_real_title
    options:
      show_source: false
      heading_level: 4

!!! tip "Alias Method"
    This is an alias for `update_title_info()` provided for backward compatibility.

!!! example "Title Company Details"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    title_data: Dict[str, Any] = {
        "company": "Premier Title Co",  # Use 'company' not 'title_company'
        "firstName": "Sarah",  # Use camelCase
        "lastName": "Johnson",  # Use camelCase
        "phoneNumber": "+1-555-789-0123",  # Use camelCase
        "email": "sarah@premiertitle.com",
        "address": "789 Title Lane, Title City, TC 54321",
        "policyNumber": "PT-2024-001234"  # Use camelCase
    }

    # Using either method works the same
    client.transaction_builder.update_title_info(transaction_id, title_data)
    # or
    client.transaction_builder.update_real_title(transaction_id, title_data)
    ```

### Personal Deal Information

::: rezen.transaction_builder.TransactionBuilderClient.update_personal_deal_info
    options:
      show_source: false
      heading_level: 4

### Update Personal Deal

::: rezen.transaction_builder.TransactionBuilderClient.update_personal_deal
    options:
      show_source: false
      heading_level: 4

!!! tip "Alias Method"
    This is an alias for `update_personal_deal_info()` provided for backward compatibility.

---

## Financial Management

### Commission Splits

::: rezen.transaction_builder.TransactionBuilderClient.update_commission_splits
    options:
      show_source: false
      heading_level: 4

!!! danger "⚠️ CRITICAL: Use PARTICIPANT IDs, not Agent IDs!"

    Commission splits require **PARTICIPANT IDs**, not agent IDs. After adding agents to the transaction, 
    each agent gets a unique participant ID. You MUST retrieve the transaction to get these IDs before 
    creating commission splits.

!!! example "Commission Split Examples"

    === "Working Example with Participant IDs"

        ```python
        from typing import Dict, List, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

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
        client.transaction_builder.update_commission_splits(transaction_id, commission_splits)
        ```

    === "Single Agent 100% Split"

        ```python
        from typing import Dict, List, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()
        transaction_id: str = "your-transaction-id-here"

        # Get transaction to find participant ID
        transaction = client.transaction_builder.get_transaction_builder(transaction_id)
        
        # Find owner agent participant ID
        owner_participant_id = None
        for agent in transaction["agentsInfo"]["ownerAgent"]:
            owner_participant_id = agent["id"]  # Participant ID, not agentId!
            break
        
        # Create commission split
        commission_splits = [{
            "participantId": owner_participant_id,
            "commission": {
                "commissionPercent": 100.0,
                "percentEnabled": True,
                "negativeOrEmpty": False
            }
        }]
        
        client.transaction_builder.update_commission_splits(transaction_id, commission_splits)
        ```

### Commission Payers

::: rezen.transaction_builder.TransactionBuilderClient.add_commission_payer
    options:
      show_source: false
      heading_level: 4

### Update Commission Payer

::: rezen.transaction_builder.TransactionBuilderClient.update_commission_payer
    options:
      show_source: false
      heading_level: 4

!!! tip "Alias Method"
    This is an alias for `add_commission_payer()` provided for backward compatibility.

**Payer Types:**

| Type | Description |
|------|-------------|
| `SELLER` | Seller pays commission |
| `BUYER` | Buyer pays commission |
| `BOTH` | Split between buyer and seller |

!!! example "Commission Payer Configuration"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()
    transaction_id: str = "your-transaction-id-here"

    payer_data: Dict[str, Any] = {
        "payerType": "SELLER",  # Use camelCase
        "commissionRate": 6.0,  # 6% commission, use camelCase
        "flatFee": False  # Percentage-based, not flat fee, use camelCase
    }

    # Using either method works the same
    client.transaction_builder.add_commission_payer(transaction_id, payer_data)
    # or
    client.transaction_builder.update_commission_payer(transaction_id, payer_data)
    ```

---

## Field Name Requirements

!!! danger "Critical Field Name Requirements"

    The ReZEN API has specific field name requirements that must be followed exactly:

    **Location Fields:**
    - ✅ Use `street` NOT `address`
    - ✅ Use `zip` NOT `zipCode`
    - ✅ State must be `UTAH` (all caps)
    - ✅ Use camelCase: `yearBuilt`, `mlsNumber`, `escrowNumber`

    **Contact Fields:**
    - ✅ Use `firstName` NOT `first_name`
    - ✅ Use `lastName` NOT `last_name`
    - ✅ Use `phoneNumber` NOT `phone`

    **Price Fields:**
    - ✅ `salePrice` must be an object with `amount` and `currency`
    - ✅ Use camelCase: `earnestMoney`, `downPayment`, `loanAmount`

    **Date Fields:**
    - ✅ Use camelCase: `contractDate`, `closingDate`, `acceptanceDate`
    - ✅ Format: `YYYY-MM-DD`

    **Commission Fields:**
    - ✅ Use camelCase: `agentId`, `splitPercentage`, `commissionAmount`

---

## Backward Compatibility

!!! info "Legacy Method Names"
    
    The library provides backward compatibility aliases for users migrating from older versions:
    
    | Old Method Name | New Method Name |
    |----------------|-----------------|
    | `put_buyer_to_draft()` | `add_buyer()` |
    | `put_seller_to_draft()` | `add_seller()` |
    | `put_location_to_draft()` | `update_location_info()` |
    | `put_price_and_date_to_draft()` | `update_price_and_date_info()` |
    | `update_commission_payer()` | `add_commission_payer()` |
    | `update_personal_deal()` | `update_personal_deal_info()` |
    | `update_real_title()` | `update_title_info()` |

!!! example "Using Backward Compatibility"

    ```python
    from rezen import RezenClient

    client = RezenClient()
    transaction_id = "your-transaction-id"

    # These method pairs do the same thing:
    
    # Add buyer
    client.transaction_builder.add_buyer(transaction_id, buyer_data)
    client.transaction_builder.put_buyer_to_draft(transaction_id, buyer_data)
    
    # Add seller
    client.transaction_builder.add_seller(transaction_id, seller_data)
    client.transaction_builder.put_seller_to_draft(transaction_id, seller_data)
    
    # Update location
    client.transaction_builder.update_location_info(transaction_id, location_data)
    client.transaction_builder.put_location_to_draft(transaction_id, location_data)
    
    # Update price and date
    client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
    client.transaction_builder.put_price_and_date_to_draft(transaction_id, price_data)
    ```

---

## Query & Search Operations

### List Transaction Builders

::: rezen.transaction_builder.TransactionBuilderClient.get_transaction_builders
    options:
      show_source: false
      heading_level: 4

!!! example "Advanced Filtering"

    === "Basic Pagination"

        ```python
        builders = client.transaction_builder.get_transaction_builders(
            limit=20,
            from_offset=0
        )

        print(f"Found {len(builders)} transaction builders")
        for builder in builders:
            print(f"ID: {builder['id']}, Status: {builder['status']}")
        ```

    === "User-Specific Search"

        ```python
        # Get builders for specific user
        user_builders = client.transaction_builder.get_transaction_builders(
            limit=50,
            from_offset=0,
            yenta_id="user-uuid-here",
            builder_type="TRANSACTION"
        )
        ```

    === "Listing Builders Only"

        ```python
        # Get only listing builders
        listings = client.transaction_builder.get_transaction_builders(
            limit=25,
            from_offset=0,
            builder_type="LISTING"
        )
        ```

---

## Error Handling

### Enhanced Error Messages

The Transaction Builder now includes enhanced error handling that catches common mistakes before they reach the API.

!!! success "New Error Types"

    - **`InvalidFieldNameError`**: Catches incorrect field names (e.g., `address` instead of `street`)
    - **`InvalidFieldValueError`**: Validates field formats (e.g., state must be uppercase)
    - **`TransactionSequenceError`**: Identifies when operations are called in wrong order
    - **`ValidationError`**: General validation failures with detailed messages

### Common Field Name Errors

!!! example "Field Name Validation"

    ```python
    from rezen.exceptions import InvalidFieldNameError

    try:
        # Using wrong field name
        location_data = {
            "address": "123 Main St",  # ❌ Wrong! Should be 'street'
            "city": "Salt Lake City",
            "state": "UTAH",
            "zipCode": "84101"  # ❌ Wrong! Should be 'zip'
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
    except InvalidFieldNameError as e:
        print(f"Field name error: {e}")
        print(f"Use '{e.correct_name}' instead of '{e.field_name}'")
    ```

### Field Value Validation

!!! example "Field Value Validation"

    ```python
    from rezen.exceptions import InvalidFieldValueError

    try:
        # Wrong state format
        location_data = {
            "street": "123 Main St",
            "city": "Salt Lake City",
            "state": "utah",  # ❌ Wrong! Must be uppercase
            "zip": "84101"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
    except InvalidFieldValueError as e:
        print(f"Invalid value for '{e.field_name}': {e.value}")
        print(f"Expected: {e.expected_format}")
    ```

### Transaction Sequence Errors

!!! danger "Sequence Requirements"

    The owner agent endpoint requires specific setup steps in order:

    ```python
    from rezen.exceptions import TransactionSequenceError

    try:
        # Trying to add owner agent without proper setup
        client.transaction_builder.update_owner_agent_info(builder_id, owner_data)
    except TransactionSequenceError as e:
        print(f"Sequence error: {e}")
        # Error message includes required steps:
        # 1. Create transaction (create_transaction_builder)
        # 2. Add location info (update_location_info) - REQUIRED FIRST
        # 3. Add price/date info (update_price_and_date_info) - REQUIRED SECOND
        # 4. Add buyers/sellers (add_buyer/add_seller) - REQUIRED THIRD
        # 5. THEN add owner agent (update_owner_agent_info)
    ```

### Price Structure Validation

!!! example "Price Field Validation"

    ```python
    from rezen.exceptions import InvalidFieldValueError, ValidationError

    try:
        price_data = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": 500000,  # ❌ Wrong! Must be object
            "representationType": "BUYERS_AGENT"  # ❌ Wrong! Should be 'BUYER'
        }
        client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
    except InvalidFieldValueError as e:
        # Catches: "Invalid value for 'salePrice': 500000. 
        # Expected: Object with 'amount' and 'currency' fields"
        print(f"Error: {e}")
    except ValidationError as e:
        # Catches missing required fields
        print(f"Validation error: {e}")
    ```

### Best Practices

!!! info "Error Handling Best Practices"

    - **Catch Specific Exceptions**: Use specific exception types for better error handling
    - **Check Field Names**: The enhanced validation catches common camelCase vs snake_case errors
    - **Validate Before Submission**: Required fields are now validated before API calls
    - **Follow Sequence Requirements**: Especially important for owner agent endpoints
    - **Use Error Details**: Exception objects contain helpful properties like `field_name` and `correct_name`

---

## Step-by-Step Transaction Creation

!!! example "Interactive Transaction Building"

    In real-world scenarios, transaction information is often gathered incrementally. This example shows how to build a transaction step by step as information becomes available.

    === "Step 1: Initialize"

        ```python
        from rezen import RezenClient
        from datetime import datetime, timedelta

        client = RezenClient()

        # Create empty transaction
        transaction_id = client.transaction_builder.create_transaction_builder()
        print(f"✅ Created transaction: {transaction_id}")
        
        # Check initial status
        transaction = client.transaction_builder.get_transaction_builder(transaction_id)
        print(f"📊 Status: Empty transaction ready for data")
        ```

    === "Step 2: Add Location"

        ```python
        # Location information becomes available
        location_data = {
            "street": "2207 E Wilson Ave",
            "city": "Salt Lake City",
            "state": "UTAH",             # Must be ALL CAPS
            "zip": "84108",
            "county": "Salt Lake",        # REQUIRED
            "yearBuilt": 1950,           # REQUIRED
            "mlsNumber": "n/a"           # REQUIRED (can use "n/a" if not available)
        }
        
        client.transaction_builder.update_location_info(transaction_id, location_data)
        print("✅ Location added")
        
        # Transaction now has: ✓ Location | ○ Price/Date | ○ Participants
        ```

    === "Step 3: Add Price Info"

        ```python
        # Price information becomes available
        price_data = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {"amount": 500000, "currency": "USD"},
            "representationType": "BUYER",   # You're representing the buyer
            "listingCommission": {            # REQUIRED even if just setting price
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False
            },
            "saleCommission": {               # REQUIRED even if just setting price
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False
            }
        }
        
        client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
        print("✅ Price information added")
        
        # Transaction now has: ✓ Location | ✓ Price | ○ Dates | ○ Participants
        ```

    === "Step 4: Add Dates"

        ```python
        # Dates are confirmed - but we need to include ALL price/date fields!
        today = datetime.now().date()
        closing_date = today + timedelta(days=30)
        
        # Must include ALL fields from price_data when updating dates
        price_date_update = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL", 
            "salePrice": {"amount": 500000, "currency": "USD"},
            "representationType": "BUYER",
            "listingCommission": {            # Still REQUIRED for date updates
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False
            },
            "saleCommission": {               # Still REQUIRED for date updates
                "commissionPercent": 3.0,
                "percentEnabled": True,
                "negativeOrEmpty": False
            },
            "acceptanceDate": today.strftime("%Y-%m-%d"),
            "closingDate": closing_date.strftime("%Y-%m-%d")
        }
        
        client.transaction_builder.update_price_and_date_info(transaction_id, price_date_update)
        print("✅ Dates added")
        
        # Transaction now has: ✓ Location | ✓ Price/Date | ○ Participants
        ```

    === "Step 5: Check Status"

        ```python
        # Check current transaction status
        transaction = client.transaction_builder.get_transaction_builder(transaction_id)
        
        print(f"\n📊 Transaction Status:")
        print(f"ID: {transaction['id']}")
        print(f"Property: {transaction['address']['street']}, {transaction['address']['city']}")
        print(f"Price: ${transaction['salePrice']['amount']:,}")
        print(f"Type: {transaction['dealType']} - {transaction['propertyType']}")
        print(f"Representation: {transaction['agentsInfo']['representationType']}")
        print(f"Acceptance: {transaction['acceptanceDate']}")
        print(f"Closing: {transaction['estimatedClosingDate']}")
        
        # Ready to add participants when their info becomes available
        ```

    === "Step 6: Add Participants"

        ```python
        # Add buyer when their information is available
        buyer_data = {
            "firstName": "Demo",
            "lastName": "Buyer",
            "email": "demo.buyer@example.com",
            "phoneNumber": "1(801) 555-0123"  # MUST include country code!
        }
        client.transaction_builder.add_buyer(transaction_id, buyer_data)
        print("✅ Buyer added")
        
        # Add seller
        seller_data = {
            "firstName": "John",
            "lastName": "Seller", 
            "email": "john.seller@example.com",
            "phoneNumber": "1(801) 555-9876"  # MUST include country code!
        }
        client.transaction_builder.add_seller(transaction_id, seller_data)
        print("✅ Seller added")
        
        # Transaction now has: ✓ Location | ✓ Price/Date | ✓ Buyer | ✓ Seller
        ```

    **Key Learnings:**
    
    - ✅ Transactions can be built incrementally as information becomes available
    - ✅ Location requires additional fields: `county`, `yearBuilt`, `mlsNumber`
    - ✅ Price updates always require both commission objects
    - ⚠️ Date-only updates still require the complete price/date structure
    - ✅ Use `get_transaction_builder()` to check progress at any time

---

## Complete Workflow Example

!!! example "End-to-End Transaction Creation"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError
    import logging

    def create_complete_transaction():
        """Create a complete transaction with all participants and details."""

        try:
            client = RezenClient()

            # Step 1: Create transaction builder
            print("Creating transaction builder...")
            response = client.transaction_builder.create_transaction_builder()
            transaction_id = response['id']
            print(f"✅ Created transaction: {transaction_id}")

            # Step 2: Add buyer
            print("Adding buyer...")
            buyer_data = {
                "firstName": "John",  # Use camelCase
                "lastName": "Doe",  # Use camelCase
                "email": "john.doe@email.com",
                "phoneNumber": "+1-555-123-4567"  # Use camelCase
            }
            client.transaction_builder.add_buyer(transaction_id, buyer_data)
            print("✅ Added buyer")

            # Step 3: Add seller
            print("Adding seller...")
            seller_data = {
                "firstName": "Jane",  # Use camelCase
                "lastName": "Smith",  # Use camelCase
                "email": "jane.smith@email.com",
                "phoneNumber": "+1-555-987-6543"  # Use camelCase
            }
            client.transaction_builder.add_seller(transaction_id, seller_data)
            print("✅ Added seller")

            # Step 4: Add property location
            print("Setting property location...")
            location_data = {
                "street": "123 Dream House Lane",  # Use 'street' not 'address'
                "street2": "",
                "city": "Salt Lake City",
                "state": "UTAH",  # Must be UTAH (all caps)
                "zip": "84101",  # Use 'zip' not 'zipCode'
                "county": "Salt Lake",
                "unit": "",
                "yearBuilt": 2020,  # Use camelCase
                "mlsNumber": "MLS123456",  # Use camelCase
                "escrowNumber": ""
            }
            client.transaction_builder.update_location_info(transaction_id, location_data)
            print("✅ Set property location")

            # Step 5: Set pricing and dates
            print("Setting pricing and dates...")
            price_data = {
                "salePrice": {  # Use camelCase and object structure
                    "amount": 850000,
                    "currency": "USD"
                },
                "earnestMoney": 17000,  # Use camelCase
                "acceptanceDate": "2024-02-01",  # Use camelCase
                "closingDate": "2024-03-15"  # Use camelCase
            }
            client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
            print("✅ Set pricing and dates")

            # Step 6: Add service providers
            print("Adding service providers...")
            inspector_data = {
                "type": "INSPECTOR",
                "firstName": "Mike",  # Use camelCase
                "lastName": "Inspector",  # Use camelCase
                "company": "Quality Inspections Inc",
                "phoneNumber": "+1-555-INSPECT",  # Use camelCase
                "email": "mike@qualityinspections.com"
            }
            client.transaction_builder.add_participant(transaction_id, inspector_data)
            print("✅ Added inspector")

            # Step 7: Submit transaction
            print("Submitting transaction...")
            submit_response = client.transaction_builder.submit_transaction(transaction_id)
            print("✅ Transaction submitted successfully!")

            return {
                "success": True,
                "transaction_id": transaction_id,
                "submit_response": submit_response
            }

        except RezenError as e:
            logging.error(f"ReZEN API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "transaction_id": transaction_id if 'transaction_id' in locals() else None
            }
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    # Run the example
    result = create_complete_transaction()
    if result["success"]:
        print(f"🎉 Transaction {result['transaction_id']} created successfully!")
    else:
        print(f"❌ Failed to create transaction: {result['error']}")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [🤝 **Transactions API**](transactions.md)

    Work with live transactions and manage ongoing deals

-   [👥 **Teams API**](teams.md)

    Search and manage team information

-   [👔 **Agents API**](agents.md)

    Find and manage agent information

-   [📄 **Examples**](../guides/examples.md)

    See more practical usage examples

</div>

## Complete Transaction Submission Workflow

!!! danger "Critical: Commission Splits and Submission Requirements"

    The following example shows the **EXACT** workflow proven to work in production, including all critical requirements for successful transaction submission.

    ```python
    # COMPLETE WORKING TRANSACTION SUBMISSION EXAMPLE
    # Based on production-proven workflow
    
    from rezen import RezenClient
    
    client = RezenClient()
    
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
    ```

    !!! warning "Common Submission Failures"
    
        1. **"commissionSplitsInfo cannot be empty"** - You MUST add commission splits before submission
        2. **"Bad request: Invalid request"** - Check that you're using participant IDs, not agent IDs
        3. **Missing commission payer** - Title company or other payer is required
        4. **Wrong commission structure** - Each split needs the nested `commission` object

## Known Issues

1. **Date-only updates require complete price/date structure** - You cannot update dates without including all price and commission fields
2. **Team selection on owner agent** - Currently, the API does not properly set the `teamId` field on the owner agent object, even when using explicit team selection methods. The team ID is only stored at the `agentsInfo` level, which prevents transaction submission. This is a limitation in the current API implementation.
3. **All phone numbers must include country code** - Phone numbers without the country code prefix (e.g., starting with "1" for US) will fail validation
4. **Commission splits require participant IDs** - You must retrieve the transaction after adding agents to get their participant IDs for commission splits
5. **Both buyer AND seller required** - Even for buyer-only representation, you must add both a buyer and seller to the transaction for successful submission
