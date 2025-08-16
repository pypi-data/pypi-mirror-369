# Users API

Access user information, team membership, and office details.

---

## Overview

!!! abstract "Users API Features"

    - **Current User Info**: Get authenticated user's profile and details
    - **User Lookup**: Find users by ID
    - **Team Information**: Access user's team and office membership
    - **Keymaker IDs**: Retrieve associated agent IDs for users
    - **Office Details**: Get user's office information

!!! info "New API Addition"
    The Users API was added to support owner agent functionality in transactions.

---

## Quick Start

```python
from rezen import RezenClient

client = RezenClient()

# Get current authenticated user
current_user = client.users.get_current_user()
print(f"User: {current_user['firstName']} {current_user['lastName']}")
print(f"Team ID: {current_user['team']['id']}")
print(f"Office ID: {current_user['office']['id']}")

# Get keymaker IDs for transaction owner setup
keymaker_ids = client.users.get_keymaker_ids(current_user['id'])
print(f"Agent ID: {keymaker_ids['id']}")
```

---

## Core Methods

### Get Current User

::: rezen.users.UsersClient.get_current_user
    options:
      show_source: false
      heading_level: 4

!!! example "Current User Information"

    ```python
    from typing import Dict, Any

    from rezen import RezenClient

    client: RezenClient = RezenClient()

    # Get current authenticated user details
    user: Dict[str, Any] = client.users.get_current_user()

    print(f"Name: {user['firstName']} {user['lastName']}")
    print(f"Email: {user['email']}")
    print(f"User ID: {user['id']}")

    # Access team information
    if 'team' in user:
        print(f"Team: {user['team']['name']}")
        print(f"Team ID: {user['team']['id']}")

    # Access office information
    if 'office' in user:
        print(f"Office: {user['office']['name']}")
        print(f"Office ID: {user['office']['id']}")
    ```

### Get User by ID

::: rezen.users.UsersClient.get_user_by_id
    options:
      show_source: false
      heading_level: 4

### Get Keymaker IDs

::: rezen.users.UsersClient.get_keymaker_ids
    options:
      show_source: false
      heading_level: 4

!!! important "Agent ID for Transactions"
    
    The `get_keymaker_ids()` method returns the agent ID needed for owner agent operations in transactions.

---

## Working with Owner Agents

!!! tip "Owner Agent Integration"

    The Users API is essential for setting up owner agents in transactions. Here's the complete workflow:

### Get Required IDs for Owner Agent

```python
from typing import Dict, Any

from rezen import RezenClient

client: RezenClient = RezenClient()

# Step 1: Get current user info
user: Dict[str, Any] = client.users.get_current_user()
team_id: str = user['team']['id']
office_id: str = user['office']['id']

# Step 2: Get agent ID from keymaker
keymaker: Dict[str, Any] = client.users.get_keymaker_ids(user['id'])
agent_id: str = keymaker['id']

# Step 3: Use in transaction owner agent setup
owner_data: Dict[str, Any] = {
    "ownerAgent": {
        "agentId": agent_id,
        "role": "BUYERS_AGENT"  # or "SELLERS_AGENT"
    },
    "officeId": office_id,
    "teamId": team_id
}

# Apply to transaction (after required setup steps)
client.transaction_builder.update_owner_agent_info(builder_id, owner_data)
```

### Convenience Method

!!! success "Simplified Approach"

    The Transaction Builder provides a convenience method that handles all the Users API calls for you:

```python
# Instead of manual steps above, use:
client.transaction_builder.set_current_user_as_owner_agent(
    builder_id,
    role="BUYERS_AGENT"
)
```

---

## Response Structures

### User Object

```python
{
    "id": "user-uuid",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1234567890",
    "team": {
        "id": "team-uuid",
        "name": "Team Excellence",
        "status": "ACTIVE"
    },
    "office": {
        "id": "office-uuid", 
        "name": "Main Office",
        "address": "123 Main St",
        "city": "Salt Lake City",
        "state": "UT"
    },
    "role": "AGENT",
    "status": "ACTIVE"
}
```

### Keymaker Response

```python
{
    "id": "agent-uuid",  # This is the agent ID for transactions
    "userId": "user-uuid",
    "agentStatus": "ACTIVE",
    "licenseNumber": "123456",
    "licenseState": "UT"
}
```

---

## Common Use Cases

!!! example "User Information Workflows"

    === "Owner Agent Setup"

        ```python
        from typing import Dict, Any

        from rezen import RezenClient

        client: RezenClient = RezenClient()

        # Get all required info for owner agent
        user: Dict[str, Any] = client.users.get_current_user()
        keymaker: Dict[str, Any] = client.users.get_keymaker_ids(user['id'])

        owner_info = {
            "agent_id": keymaker['id'],
            "team_id": user['team']['id'],
            "office_id": user['office']['id'],
            "user_name": f"{user['firstName']} {user['lastName']}"
        }

        print("Owner agent info collected:")
        print(f"  Agent: {owner_info['user_name']}")
        print(f"  Agent ID: {owner_info['agent_id']}")
        print(f"  Team ID: {owner_info['team_id']}")
        print(f"  Office ID: {owner_info['office_id']}")
        ```

    === "Team Member Lookup"

        ```python
        # Get team member details
        team_member_id = "member-user-uuid"
        member = client.users.get_user_by_id(team_member_id)

        # Get their agent ID if needed
        member_keymaker = client.users.get_keymaker_ids(team_member_id)

        print(f"Team member: {member['firstName']} {member['lastName']}")
        print(f"Agent ID: {member_keymaker['id']}")
        ```

---

## Error Handling

!!! warning "Common Errors"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import NotFoundError, UnauthorizedError

    client = RezenClient()

    try:
        user = client.users.get_current_user()
    except UnauthorizedError:
        print("Invalid or missing API key")
    except Exception as e:
        print(f"Error getting user info: {e}")

    # Handle missing keymaker data
    try:
        keymaker = client.users.get_keymaker_ids(user_id)
    except NotFoundError:
        print("User does not have associated agent ID")
    ```

---

## Integration with Transaction Builder

!!! danger "Critical Sequence for Owner Agents"

    When using Users API data for owner agents, you **MUST** follow this sequence:

    1. Create transaction (`create_transaction_builder`)
    2. Add location info (`update_location_info`) 
    3. Add price/date info (`update_price_and_date_info`)
    4. Add buyers/sellers (`add_buyer`/`add_seller`)
    5. **THEN** add owner agent using Users API data

    See [Transaction Builder - Owner Agents](transaction-builder.md#owner-agents) for complete details.

---

## Next Steps

<div class="grid cards" markdown>

-   [🔧 **Transaction Builder**](transaction-builder.md)

    Use user data to set up owner agents in transactions

-   [👥 **Teams API**](teams.md)

    Access more detailed team information

-   [👔 **Agents API**](agents.md)

    Search for agents beyond current user

</div> 