# Agents API

Comprehensive agent search, network management, and detailed information retrieval.

---

## Overview

!!! abstract "Agents API Features"

    - **Agent Search**: Find agents with advanced filtering including email and phone
    - **Agent Details**: Get individual agent information and cap details
    - **Network Management**: Access sponsor trees and downlines
    - **Contact Information**: Get agent details by email, ID, or phone
    - **Geographic Filtering**: Search by location and region

---

## Quick Start

=== "🚀 Basic Usage"

    ```python
    from rezen import RezenClient

    client = RezenClient()

    # Get a single agent by ID
    agent = client.agents.get_agent("agent-uuid")
    print(f"Agent: {agent['name']}")
    
    # Simple agent search by name
    agents = client.agents.search_active_agents(name="John", page_size=10)
    print(f"Found {len(agents)} agents named John")
    ```

=== "🔍 Search Options"

    ```python
    from rezen import RezenClient

    client = RezenClient()

    # Search by email
    agents = client.agents.search_active_agents(email="john@example.com")
    
    # Search by phone
    agents = client.agents.search_active_agents(phone="+1234567890")
    
    # Using backward compatibility method
    agents = client.agents.agent_search(email="john@example.com")
    agents = client.agents.agent_search(phone="+1234567890")
    ```

=== "⚙️ Advanced Filtering"

    ```python
    from rezen import RezenClient
    from rezen.enums import Country, StateOrProvince, AgentSortField

    client = RezenClient()

    # Geographic search with sorting
    agents = client.agents.search_active_agents(
        country=[Country.UNITED_STATES],
        state_or_province=[StateOrProvince.CALIFORNIA],
        sort_by=[AgentSortField.LAST_NAME],
        page_size=50
    )
    ```

=== "🛡️ Error Handling"

    ```python
    from rezen import RezenClient
    from rezen.exceptions import RezenError, NotFoundError

    client = RezenClient()

    try:
        agent = client.agents.get_agent("agent-uuid")
        print(f"Found agent: {agent['name']}")
    except NotFoundError:
        print("Agent not found")
    except RezenError as e:
        print(f"API error occurred: {e}")
    ```

---

## Core Methods

### Get Single Agent

::: rezen.agents.AgentsClient.get_agent
    options:
      show_source: false
      heading_level: 4

!!! tip "Endpoint"
    This calls `GET https://yenta.therealbrokerage.com/api/v1/agents/{id}`

```python
from rezen import RezenClient

client = RezenClient()
agent = client.agents.get_agent("5dc73abf-49b6-4926-b817-7da731a01813")
print(agent["firstName"], agent["lastName"])  # Example output
```

### Get Agent Cap Information

::: rezen.agents.AgentsClient.get_cap_info
    options:
      show_source: false
      heading_level: 4

### Search Active Agents

::: rezen.agents.AgentsClient.search_active_agents
    options:
      show_source: false
      heading_level: 4

!!! note "New Parameters"
    The `search_active_agents` method now supports `email` and `phone` parameters for direct contact search.

### Agent Search (Backward Compatibility)

::: rezen.agents.AgentsClient.agent_search
    options:
      show_source: false
      heading_level: 4

### Get Agent by Email

::: rezen.agents.AgentsClient.get_agents_by_email
    options:
      show_source: false
      heading_level: 4

### Get Agents by IDs

::: rezen.agents.AgentsClient.get_agents_by_ids
    options:
      show_source: false
      heading_level: 4

### Network Hierarchy

::: rezen.agents.AgentsClient.get_sponsor_tree
    options:
      show_source: false
      heading_level: 4

::: rezen.agents.AgentsClient.get_down_line_agents
    options:
      show_source: false
      heading_level: 4

---

## Search Examples

!!! example "Advanced Agent Search"

    === "Contact Search"

        ```python
        # Search by email
        agents = client.agents.search_active_agents(
            email="john.doe@example.com"
        )
        
        # Search by phone
        agents = client.agents.search_active_agents(
            phone="+1234567890"
        )
        
        # Using compatibility method
        agents = client.agents.agent_search(email="john@example.com")
        ```

    === "Geographic Search"

        ```python
        from rezen.enums import Country, StateOrProvince

        # Search California agents
        agents = client.agents.search_active_agents(
            country=[Country.UNITED_STATES],
            state_or_province=[StateOrProvince.CALIFORNIA],
            page_size=50
        )
        ```

    === "Sorted Results"

        ```python
        from rezen.enums import AgentSortField, SortDirection

        agents = client.agents.search_active_agents(
            sort_by=[AgentSortField.LAST_NAME, AgentSortField.FIRST_NAME],
            sort_direction=SortDirection.ASC,
            page_size=25
        )
        ```

---

## Agent Information

!!! info "Agent Details"

    Get comprehensive agent information including cap details and profile scores.

!!! example "Agent Information Retrieval"

    ```python
    # Get single agent details
    agent = client.agents.get_agent("agent-uuid")
    
    # Get agent cap information
    cap_info = client.agents.get_cap_info("agent-uuid")
    
    # Get profile score
    profile_score = client.agents.get_profile_score("agent-uuid")
    
    # Get payment details
    payment_details = client.agents.get_payment_details("agent-uuid")
    ```

---

## Network Management

!!! info "Agent Hierarchy"

    The ReZEN platform supports agent network hierarchies with sponsor trees and downlines.

!!! example "Network Analysis"

    ```python
    # Get agent's sponsor tree
    sponsor_tree = client.agents.get_sponsor_tree("agent-uuid")

    # Get first-tier downline
    downline = client.agents.get_down_line_agents(
        agent_id="agent-uuid",
        tier=1,
        status_in=["ACTIVE"]
    )
    
    # Get front line agents info
    front_line = client.agents.get_front_line_agents_info("agent-uuid")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [👥 **Teams API**](teams.md)

    Manage team information and memberships

-   [🔧 **Transaction Builder**](transaction-builder.md)

    Add agents to transactions

-   [📖 **Directory API**](directory.md)

    Access additional agent directory services

</div>
