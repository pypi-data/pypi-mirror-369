# Client Setup

The ReZEN Python API client provides multiple ways to authenticate and configure your connection to the ReZEN API platform.

!!! critical "Authentication Method"
    The ReZEN API uses **X-API-KEY header authentication**, not Authorization Bearer tokens. The Python client handles this automatically.

---

## Installation

!!! tip "Python Package Index"

    Install the ReZEN client using pip:

    ```bash
    pip install rezen
    ```

!!! info "Development Installation"

    For development or contributing:

    ```bash
    git clone https://github.com/theperrygroup/rezen.git
    cd rezen
    pip install -e ".[dev]"
    ```

---

## Authentication

### API Key Configuration

=== "🔧 Automatic (Recommended)"

    The client automatically reads from the `REZEN_API_KEY` environment variable:

    ```python
    import os
    from typing import Optional

    from rezen import RezenClient

    # Set environment variable (in your shell or .env file)
    os.environ['REZEN_API_KEY'] = 'your_api_key_here'

    # Client automatically uses the environment variable
    client: RezenClient = RezenClient()
    ```

    !!! tip "Environment Files"

        Use a `.env` file with python-dotenv for local development:

        ```bash title=".env"
        REZEN_API_KEY=your_api_key_here
        ```

        ```python
        from dotenv import load_dotenv

        from rezen import RezenClient

        load_dotenv()  # Load .env file
        client: RezenClient = RezenClient()  # Uses REZEN_API_KEY from .env
        ```

=== ":material-key-variant: Explicit"

    Pass the API key directly to the client:

    ```python
    from rezen import RezenClient

    client: RezenClient = RezenClient(api_key="your_api_key_here")
    ```

    !!! warning "Security Best Practice"

        Never hardcode API keys in your source code. Use environment variables or secure configuration management.

=== "⚙️ Custom Configuration"

    Configure both API key and base URL:

    ```python
    from rezen import RezenClient

    client: RezenClient = RezenClient(
        api_key="your_api_key_here",
        base_url="https://custom.api.endpoint.com"
    )
    ```

---

## Client Initialization

### Main RezenClient

The primary client provides access to all API modules:

```python title="Basic Setup"
from rezen import RezenClient

# Initialize with default settings
client: RezenClient = RezenClient()

# Access specialized API modules
transaction_builder = client.transaction_builder
transactions = client.transactions
teams = client.teams
agents = client.agents
```

!!! abstract "Available Modules"

    | Module | Purpose |
    |--------|---------|
    | `client.transaction_builder` | Create and configure new transactions |
    | `client.transactions` | Manage live transactions and participants |
    | `client.teams` | Search and filter team information |
    | `client.agents` | Agent search and network management |

### Directory Client

The Directory API uses a separate client with its own endpoint:

=== ":material-database: Dedicated Client"

    ```python
    from rezen import DirectoryClient

    # Directory client with separate authentication
    directory: DirectoryClient = DirectoryClient()

    # Or with explicit configuration
    directory: DirectoryClient = DirectoryClient(
        api_key="your_api_key_here",
        base_url="https://yenta.therealbrokerage.com/api/v1"
    )
    ```

=== ":material-connection: Unified Access"

    ```python
    from typing import Dict, List, Any

    from rezen import RezenClient, DirectoryClient

    # Main client for core APIs
    client: RezenClient = RezenClient()

    # Separate directory client
    directory: DirectoryClient = DirectoryClient()

    # Use both in your application
    teams: List[Dict[str, Any]] = client.teams.search_teams(status="ACTIVE")
    contacts: List[Dict[str, Any]] = directory.search_contacts(name="John Doe")
    ```

---

## Configuration Options

### Base Client Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `Optional[str]` | `None` | API authentication key |
| `base_url` | `Optional[str]` | API default | Custom API endpoint URL |
| `timeout` | `Optional[int]` | `30` | Request timeout in seconds |
| `retry_attempts` | `Optional[int]` | `3` | Number of retry attempts |

### Advanced Configuration

=== ":material-timer: Timeouts & Retries"

    ```python
    from rezen import RezenClient

    client: RezenClient = RezenClient(
        api_key="your_api_key_here",
        timeout=60,  # 60 second timeout
        retry_attempts=5  # 5 retry attempts
    )
    ```

=== "🔒 SSL & Headers"

    ```python
    from typing import Dict, str

    from rezen import RezenClient

    # Custom headers and SSL verification
    custom_headers: Dict[str, str] = {
        "User-Agent": "MyApp/1.0",
        "X-Custom-Header": "custom-value"
    }

    client: RezenClient = RezenClient(
        api_key="your_api_key_here",
        verify_ssl=True,  # Verify SSL certificates
        custom_headers=custom_headers
    )
    ```

---

## Error Handling

!!! failure "Common Authentication Errors"

    ```python
    from typing import List, Dict, Any

    from rezen import RezenClient
    from rezen.exceptions import AuthenticationError, RezenError

    try:
        client: RezenClient = RezenClient(api_key="invalid_key")
        teams: List[Dict[str, Any]] = client.teams.search_teams()
    except AuthenticationError as e:
        print(f"Invalid API key provided: {e}")
    except RezenError as e:
        print(f"API error: {e}")
    ```

!!! info "Connection Troubleshooting"

    - **401 Unauthorized**: Check your API key
    - **403 Forbidden**: Verify API key permissions
    - **429 Rate Limited**: Implement retry logic with backoff
    - **500 Server Error**: Check API status or contact support

---

## Best Practices

### 🛡️ Security

!!! warning "API Key Security"

    - Store API keys in environment variables
    - Use secrets management in production
    - Never commit API keys to version control
    - Rotate API keys regularly

### ⏱️ Performance

!!! tip "Optimization Tips"

    - Reuse client instances across requests
    - Implement connection pooling for high-volume applications
    - Use appropriate timeouts for your use case
    - Handle rate limiting with exponential backoff

### 🐛 Debugging

!!! example "Logging Configuration"

    ```python
    import logging

    from rezen import RezenClient

    # Enable debug logging
    logging.basicConfig(level=logging.DEBUG)

    # Client will log request/response details
    client: RezenClient = RezenClient()
    ```

---

## Quick Verification

Test your client setup with a simple API call:

=== "✅ Test Connection"

    ```python
    from typing import List, Dict, Any

    from rezen import RezenClient
    from rezen.exceptions import RezenError

    def test_connection() -> bool:
        """Test connection to the ReZEN API.

        Returns:
            True if connection successful, False otherwise

        Raises:
            RezenError: If API request fails
        """
        try:
            client: RezenClient = RezenClient()
            teams: List[Dict[str, Any]] = client.teams.search_teams(page_size=1)
            print("✅ Connection successful!")
            return True
        except RezenError as e:
            print(f"❌ Connection failed: {e}")
            return False

    # Run the test
    test_connection()
    ```

=== ":material-information: Environment Check"

    ```python
    import os
    from typing import Optional

    from rezen import RezenClient

    def check_environment() -> bool:
        """Check environment configuration for ReZEN API.

        Returns:
            True if environment is properly configured, False otherwise

        Raises:
            Exception: If client initialization fails
        """
        api_key: Optional[str] = os.getenv('REZEN_API_KEY')

        if not api_key:
            print("❌ REZEN_API_KEY environment variable not set")
            return False

        print(f"✅ API key found: {api_key[:8]}...")

        try:
            client: RezenClient = RezenClient()
            print("✅ Client initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Client initialization failed: {e}")
            return False

    # Check your environment
    check_environment()
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [🔧 **Transaction Builder**](../api/transaction-builder.md)

    Start creating transactions with the Transaction Builder API

-   [👥 **Teams API**](../api/teams.md)

    Search and manage team information

-   [👔 **Agents API**](../api/agents.md)

    Access comprehensive agent search and management

-   [📄 **Examples**](../guides/examples.md)

    See practical examples and use cases

</div>
