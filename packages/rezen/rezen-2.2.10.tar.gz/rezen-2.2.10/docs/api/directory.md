# Directory API

Access directory services for agent and contact information with dedicated client functionality.

---

## Overview

!!! abstract "Directory API Features"

    - **Dedicated Client**: Separate client for directory services
    - **Contact Search**: Find contacts and agent information
    - **Different Endpoint**: Uses specialized directory API endpoint
    - **Enhanced Search**: Advanced contact discovery capabilities

---

## Client Setup

!!! info "Separate Directory Client"

    The Directory API uses a dedicated client with its own endpoint configuration.

```python
from rezen import DirectoryClient

# Initialize directory client
directory = DirectoryClient()

# Or with explicit configuration
directory = DirectoryClient(
    api_key="your_api_key_here",
    base_url="https://yenta.therealbrokerage.com/api/v1"
)
```

---

## Core Methods

### Directory Client Operations

::: rezen.directory.DirectoryClient
    options:
      show_source: false
      heading_level: 4
      filters: ["!^_"]

---

## Usage Examples

!!! example "Directory Operations"

    === "Basic Contact Search"

        ```python
        from rezen import DirectoryClient

        directory = DirectoryClient()

        # Search for contacts
        contacts = directory.search_contacts(name="John Doe")

        for contact in contacts:
            print(f"Contact: {contact['name']} - {contact['email']}")
        ```

    === "Advanced Directory Search"

        ```python
        # Advanced search with multiple criteria
        results = directory.advanced_search(
            name="Smith",
            location="California",
            agent_type="LISTING_AGENT"
        )
        ```

---

## Directory vs Main API

!!! note "API Differences"

    | Feature | Main API | Directory API |
    |---------|----------|---------------|
    | **Endpoint** | Standard ReZEN API | Specialized directory endpoint |
    | **Client** | `RezenClient` | `DirectoryClient` |
    | **Purpose** | Transaction management | Contact/agent discovery |
    | **Authentication** | Same API key | Same API key |

!!! tip "Combined Usage"

    You can use both clients together in your application:

    ```python
    from rezen import RezenClient, DirectoryClient

    # Main client for transactions
    client = RezenClient()

    # Directory client for contact search
    directory = DirectoryClient()

    # Find contacts, then use in transactions
    contacts = directory.search_contacts(name="John Doe")
    if contacts:
        # Use contact info in transaction builder
        buyer_data = {
            "type": "BUYER",
            "first_name": contacts[0]['first_name'],
            "last_name": contacts[0]['last_name'],
            "email": contacts[0]['email']
        }
        # ... continue with transaction creation
    ```

---

## Best Practices

!!! warning "Endpoint Considerations"

    - The Directory API uses a different base URL than the main API
    - Ensure your API key has access to directory services
    - Consider rate limiting for directory searches

!!! example "Production Usage"

    ```python
    import logging
    from rezen import DirectoryClient
    from rezen.exceptions import RezenError

    def safe_directory_search(name: str):
        """Safely search directory with error handling."""
        try:
            directory = DirectoryClient()
            results = directory.search_contacts(name=name)
            return {"success": True, "contacts": results}
        except RezenError as e:
            logging.error(f"Directory search failed: {e}")
            return {"success": False, "error": str(e)}
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [👔 **Agents API**](agents.md)

    Use agent data from directory in main API

-   [🔧 **Transaction Builder**](transaction-builder.md)

    Add directory contacts to transactions

-   [🚀 **Getting Started**](../getting-started/quickstart.md)

    Complete setup guide for ReZEN clients

</div>
