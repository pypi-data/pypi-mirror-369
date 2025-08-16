# Teams API

Search and manage team information with comprehensive filtering and sorting capabilities.

---

## Overview

!!! abstract "Teams API Capabilities"

    - **Search Teams**: Find teams with advanced filtering options
    - **Team Details**: Get comprehensive team information including members
    - **Flexible Sorting**: Sort results by various criteria
    - **Pagination**: Handle large result sets efficiently
    - **Member Management**: Access team member details

---

## Quick Start

```python
from rezen import RezenClient
from rezen.enums import TeamStatus, SortDirection

client = RezenClient()

# Simple team search
teams = client.teams.search_teams(status="ACTIVE", page_size=10)

# Get team with full details
team = client.teams.get_team("team-uuid")

# Get team members
members = client.teams.get_team_members("team-uuid")

# Advanced search with enums
teams = client.teams.search_teams(
    status=TeamStatus.ACTIVE,
    sort_direction=SortDirection.DESC,
    page_size=50
)
```

---

## API Methods

### Search Teams

::: rezen.teams.TeamsClient.search_teams
    options:
      show_source: false
      heading_level: 4

!!! example "Search Examples"

    === "Basic Search"

        ```python
        teams = client.teams.search_teams(
            status="ACTIVE",
            page_size=20
        )
        ```

    === "Advanced Filtering"

        ```python
        from rezen.enums import TeamStatus, TeamSortField, SortDirection

        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            name="Sales Team",
            sort_by=[TeamSortField.NAME, TeamSortField.CREATED_AT],
            sort_direction=SortDirection.ASC,
            page_size=50
        )
        ```

### Get Team Details

::: rezen.teams.TeamsClient.get_team_without_agents
    options:
      show_source: false
      heading_level: 4

::: rezen.teams.TeamsClient.get_team
    options:
      show_source: false
      heading_level: 4

!!! tip "Team Details Methods"
    - Use `get_team_without_agents()` for basic team information without member details
    - Use `get_team()` for full team information including all agents/members

### Get Team Members

::: rezen.teams.TeamsClient.get_team_members
    options:
      show_source: false
      heading_level: 4

!!! example "Team Member Examples"

    === "Get All Members"

        ```python
        # Get team members
        team_id = "550e8400-e29b-41d4-a716-446655440000"
        members = client.teams.get_team_members(team_id)
        
        print(f"Team has {len(members.get('members', []))} members")
        for member in members.get('members', []):
            print(f"Member: {member['name']} - Role: {member['role']}")
        ```

    === "Get Full Team Info"

        ```python
        # Get complete team information with agents
        team = client.teams.get_team(team_id)
        
        print(f"Team: {team['name']}")
        print(f"Status: {team['status']}")
        print(f"Type: {team['team_type']}")
        print(f"Total agents: {len(team.get('agents', []))}")
        
        # Process team agents
        for agent in team.get('agents', []):
            print(f"Agent: {agent['first_name']} {agent['last_name']}")
        ```

---

## Parameters Reference

### Search Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page_number` | `Optional[int]` | Page number (default: 0) |
| `page_size` | `Optional[int]` | Results per page (default: 20) |
| `sort_direction` | `Optional[SortDirection]` | ASC or DESC |
| `sort_by` | `Optional[List[TeamSortField]]` | Fields to sort by |
| `team_id` | `Optional[str]` | Filter by team UUID |
| `name` | `Optional[str]` | Filter by team name |
| `search_text` | `Optional[str]` | General search text |
| `status` | `Optional[TeamStatus]` | ACTIVE or INACTIVE |
| `created_at_start` | `Optional[str]` | Date filter start (YYYY-MM-DD) |
| `created_at_end` | `Optional[str]` | Date filter end (YYYY-MM-DD) |
| `team_type` | `Optional[TeamType]` | Team type filter |

---

## Complete Examples

!!! example "Comprehensive Team Management"

    ```python
    from rezen import RezenClient
    from rezen.enums import TeamStatus, TeamType, SortDirection, TeamSortField

    def comprehensive_team_management():
        client = RezenClient()

        # Search for active teams
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            team_type=TeamType.PLATINUM,
            sort_by=[TeamSortField.NAME, TeamSortField.CREATED_AT],
            sort_direction=SortDirection.DESC,
            page_size=25,
            created_at_start="2024-01-01",
            created_at_end="2024-12-31"
        )

        print(f"Found {len(teams)} teams")
        
        # Get detailed information for each team
        for team_summary in teams[:5]:  # Process first 5 teams
            team_id = team_summary['id']
            
            # Get full team details
            full_team = client.teams.get_team(team_id)
            print(f"\nTeam: {full_team['name']}")
            print(f"Status: {full_team['status']}")
            print(f"Type: {full_team['team_type']}")
            
            # Get team members
            members = client.teams.get_team_members(team_id)
            print(f"Members: {len(members.get('members', []))}")
            
            # List member details
            for member in members.get('members', [])[:3]:  # Show first 3 members
                print(f"  - {member['name']} ({member['role']})")

        return teams
    ```

---

## Team Types and Statuses

!!! info "Team Types"

    | Type | Description |
    |------|-------------|
    | `NORMAL` | Standard team |
    | `PLATINUM` | Platinum-level team |
    | `GROUP` | Group team |
    | `DOMESTIC` | Domestic team |
    | `PRO` | Professional team |

!!! info "Team Statuses"

    | Status | Description |
    |--------|-------------|
    | `ACTIVE` | Team is currently active |
    | `INACTIVE` | Team is inactive/archived |

---

## Next Steps

<div class="grid cards" markdown>

-   [👔 **Agents API**](agents.md)

    Search and manage agent information

-   [🔧 **Transaction Builder**](transaction-builder.md)

    Create transactions with team members

-   [📝 **Data Types**](../reference/data-types.md)

    Learn about team-related enums and types

</div>
