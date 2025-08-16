# Data Types & Enums

The ReZEN API client provides comprehensive type definitions and enums for type-safe development and better IDE support.

---

## Overview

!!! abstract "Type System Benefits"

    - **Type Safety**: Full type hints for all API methods and data structures
    - **IDE Support**: Enhanced autocompletion and error detection
    - **Validation**: Automatic data validation using Pydantic models
    - **Documentation**: Self-documenting code with clear type definitions

---

## Enums

### Teams & Organization

=== "👥 Team Management"

    #### TeamStatus

    ```python
    from rezen.enums import TeamStatus

    # Available team statuses
    TeamStatus.ACTIVE      # Active teams
    TeamStatus.INACTIVE    # Inactive teams
    ```

    #### TeamType

    ```python
    from rezen.enums import TeamType

    # Team classification types
    TeamType.PLATINUM      # Platinum level teams
    TeamType.GOLD          # Gold level teams
    TeamType.SILVER        # Silver level teams
    TeamType.BRONZE        # Bronze level teams
    ```

    #### SortDirection

    ```python
    from rezen.enums import SortDirection

    # Sorting options
    SortDirection.ASC      # Ascending order
    SortDirection.DESC     # Descending order
    ```

=== "🔀 Team Sorting"

    #### SortField

    ```python
    from rezen.enums import SortField

    # Available sort fields for teams
    SortField.NAME         # Sort by team name
    SortField.CREATED_AT   # Sort by creation date
    SortField.UPDATED_AT   # Sort by last update
    SortField.STATUS       # Sort by status
    ```

    !!! example "Usage Example"

        ```python
        from rezen import RezenClient
        from rezen.enums import TeamStatus, SortField, SortDirection

        client = RezenClient()
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            sort_by=[SortField.NAME, SortField.CREATED_AT],
            sort_direction=SortDirection.ASC
        )
        ```

### Agents & People

=== "👔 Agent Management"

    #### AgentSortDirection

    ```python
    from rezen.enums import AgentSortDirection

    # Agent-specific sorting
    AgentSortDirection.ASC     # Ascending order
    AgentSortDirection.DESC    # Descending order
    ```

    #### AgentSortField

    ```python
    from rezen.enums import AgentSortField

    # Agent sort fields
    AgentSortField.FIRST_NAME     # Sort by first name
    AgentSortField.LAST_NAME      # Sort by last name
    AgentSortField.EMAIL          # Sort by email address
    AgentSortField.CREATED_AT     # Sort by creation date
    ```

=== "🌍 Geography"

    #### Country

    ```python
    from rezen.enums import Country

    # Supported countries
    Country.UNITED_STATES     # United States
    Country.CANADA            # Canada
    ```

    #### StateOrProvince

    ```python
    from rezen.enums import StateOrProvince

    # US States
    StateOrProvince.ALABAMA
    StateOrProvince.ALASKA
    StateOrProvince.ARIZONA
    StateOrProvince.CALIFORNIA
    StateOrProvince.TEXAS
    # ... (all US states available)

    # Canadian Provinces
    StateOrProvince.ALBERTA
    StateOrProvince.BRITISH_COLUMBIA
    StateOrProvince.ONTARIO
    # ... (all Canadian provinces available)
    ```

### Transactions & Business

=== "🤝 Transaction Types"

    #### ParticipantType

    ```python
    from rezen.enums import ParticipantType

    # Transaction participant types
    ParticipantType.BUYER         # Buyer in transaction
    ParticipantType.SELLER        # Seller in transaction
    ParticipantType.AGENT         # Real estate agent
    ParticipantType.LENDER        # Mortgage lender
    ParticipantType.INSPECTOR     # Property inspector
    ParticipantType.APPRAISER     # Property appraiser
    ParticipantType.TITLE_COMPANY # Title company
    ```

    #### TransactionStatus

    ```python
    from rezen.enums import TransactionStatus

    # Transaction lifecycle states
    TransactionStatus.DRAFT       # Draft transaction
    TransactionStatus.ACTIVE      # Active transaction
    TransactionStatus.PENDING     # Pending transaction
    TransactionStatus.CLOSED      # Closed transaction
    TransactionStatus.CANCELLED   # Cancelled transaction
    ```

---

## Auto-Generated API Documentation

The following sections provide auto-generated documentation from the source code:

### Core Enums Module

::: rezen.enums
    options:
      show_source: false
      show_root_heading: true
      heading_level: 3

---

## Usage Patterns

### Type-Safe Development

=== "🛡️ Type Safety"

    ```python
    from typing import List, Optional
    from rezen import RezenClient
    from rezen.enums import TeamStatus, SortDirection

    def get_active_teams(
        client: RezenClient,
        limit: int = 20
    ) -> List[dict]:
        """Get active teams with type safety."""
        return client.teams.search_teams(
            status=TeamStatus.ACTIVE,  # Type-safe enum usage
            sort_direction=SortDirection.DESC,
            page_size=limit
        )
    ```

=== "🔧 IDE Integration"

    ```python
    from rezen.enums import StateOrProvince, Country

    # IDE will provide autocompletion for enum values
    def search_california_agents():
        return client.agents.search_active_agents(
            country=[Country.UNITED_STATES],
            state_or_province=[StateOrProvince.CALIFORNIA]
        )
    ```

### Validation Examples

=== "✅ Input Validation"

    ```python
    from rezen.enums import TeamStatus

    def validate_team_status(status: str) -> bool:
        """Validate team status input."""
        try:
            TeamStatus(status)
            return True
        except ValueError:
            return False

    # Usage
    if validate_team_status("ACTIVE"):
        print("Valid status")
    ```

=== "🔽 Filtering with Enums"

    ```python
    from rezen.enums import (
        TeamStatus,
        AgentSortField,
        StateOrProvince
    )

    # Advanced filtering with multiple enums
    def advanced_search_example():
        client = RezenClient()

        # Search active teams
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE
        )

        # Search California agents sorted by name
        agents = client.agents.search_active_agents(
            state_or_province=[StateOrProvince.CALIFORNIA],
            sort_by=[AgentSortField.LAST_NAME]
        )

        return teams, agents
    ```

---

## Best Practices

### 🏷️ Type Hints

!!! tip "Always Use Type Hints"

    ```python
    from typing import List, Optional
    from rezen.enums import TeamStatus

    def process_teams(
        statuses: List[TeamStatus],
        limit: Optional[int] = None
    ) -> List[dict]:
        """Process teams with proper type hints."""
        # Implementation with type safety
        pass
    ```

### 📥 Import Patterns

!!! example "Recommended Import Style"

    ```python
    # Specific imports for better performance and clarity
    from rezen.enums import (
        TeamStatus,
        SortDirection,
        AgentSortField,
        StateOrProvince
    )

    # Avoid importing the entire module
    # from rezen import enums  # Less preferred
    ```

### 🐛 Error Handling

!!! warning "Enum Validation"

    ```python
    from rezen.enums import TeamStatus

    def safe_enum_conversion(value: str) -> Optional[TeamStatus]:
        """Safely convert string to enum."""
        try:
            return TeamStatus(value)
        except ValueError:
            print(f"Invalid team status: {value}")
            return None
    ```

---

## Complete Enum Reference

### Quick Reference Table

| Category | Enum | Values | Description |
|----------|------|--------|-------------|
| **Teams** | `TeamStatus` | `ACTIVE`, `INACTIVE` | Team status states |
| **Teams** | `TeamType` | `PLATINUM`, `GOLD`, `SILVER`, `BRONZE` | Team classification |
| **Sorting** | `SortDirection` | `ASC`, `DESC` | Sort order direction |
| **Teams** | `SortField` | `NAME`, `CREATED_AT`, `UPDATED_AT`, `STATUS` | Team sort fields |
| **Agents** | `AgentSortDirection` | `ASC`, `DESC` | Agent sort direction |
| **Agents** | `AgentSortField` | `FIRST_NAME`, `LAST_NAME`, `EMAIL`, `CREATED_AT` | Agent sort fields |
| **Geography** | `Country` | `UNITED_STATES`, `CANADA` | Supported countries |
| **Geography** | `StateOrProvince` | All US states & Canadian provinces | Geographic regions |
| **Transactions** | `ParticipantType` | `BUYER`, `SELLER`, `AGENT`, etc. | Transaction participants |
| **Transactions** | `TransactionStatus` | `DRAFT`, `ACTIVE`, `PENDING`, etc. | Transaction states |

---

## Migration Guide

!!! note "Upgrading from String Values"

    If you're migrating from string-based values to enums:

    === "Before (String Values)"

        ```python
        # Old approach with strings
        teams = client.teams.search_teams(
            status="ACTIVE",
            sort_direction="DESC"
        )
        ```

    === "After (Type-Safe Enums)"

        ```python
        from rezen.enums import TeamStatus, SortDirection

        # New approach with enums
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            sort_direction=SortDirection.DESC
        )
        ```

---

## Next Steps

<div class="grid cards" markdown>

-   [🔧 **Transaction Builder**](../api/transaction-builder.md)

    Learn about transaction creation and management

-   [⚠️ **Exceptions**](exceptions.md)

    Understand error handling and exception types

-   [📄 **Examples**](../guides/examples.md)

    See practical usage examples

-   [📖 **API Reference**](../api/index.md)

    Return to the main API reference

</div>
