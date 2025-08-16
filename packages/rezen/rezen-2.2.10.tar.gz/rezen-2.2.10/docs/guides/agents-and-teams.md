# Working with Agents & Teams

Comprehensive guide to managing agents, teams, and professional networks using the ReZEN API.

---

## 🎯 Overview

The ReZEN API provides powerful tools for working with real estate professionals:

- **Agent Search & Discovery** - Find agents by location, specialization, or network
- **Team Management** - Search and organize team structures
- **Network Mapping** - Track agent relationships and hierarchies
- **Directory Services** - Access professional contact information

---

## 👤 Agent Management

### Basic Agent Search

```python
from rezen import RezenClient
from rezen.exceptions import RezenError

def search_active_agents():
    """Find active agents with basic search."""
    client = RezenClient()

    try:
        # Search for active agents
        agents = client.agents.search_active_agents(
            name="John",
            limit=20
        )

        print(f"Found {len(agents)} active agents:")
        for agent in agents:
            print(f"  - {agent['first_name']} {agent['last_name']}")
            print(f"    Email: {agent.get('email', 'N/A')}")
            print(f"    Phone: {agent.get('phone', 'N/A')}")
            print(f"    Location: {agent.get('city', 'N/A')}, {agent.get('state', 'N/A')}")
            print()

        return agents

    except RezenError as e:
        print(f"❌ Agent search failed: {e}")
        return []
```

---

## 👥 Team Management

### Team Search & Discovery

```python
from rezen.enums import TeamStatus

def search_teams():
    """Search for teams with basic criteria."""
    client = RezenClient()

    try:
        # Search active teams
        teams = client.teams.search_teams(
            status=TeamStatus.ACTIVE,
            limit=25
        )

        print(f"Found {len(teams)} active teams:")
        for team in teams:
            print(f"  📋 {team['team_name']}")
            print(f"     Leader: {team.get('team_lead', 'N/A')}")
            print(f"     Members: {team.get('member_count', 'N/A')}")
            print(f"     Location: {team.get('city', 'N/A')}, {team.get('state', 'N/A')}")
            print()

        return teams

    except RezenError as e:
        print(f"❌ Team search failed: {e}")
        return []
```

---

## 📖 Directory Services

### Contact Information Management

```python
def search_directory():
    """Search the professional directory."""
    client = RezenClient()

    try:
        # Search directory
        contacts = client.directory.search_directory(
            name="Johnson",
            email="@remax.com",  # Email domain search
            limit=30
        )

        print(f"📞 Directory Search Results ({len(contacts)} contacts)")

        # Group by organization
        by_org = {}
        for contact in contacts:
            org = contact.get('organization', 'Independent')
            if org not in by_org:
                by_org[org] = []
            by_org[org].append(contact)

        # Display by organization
        for org, org_contacts in by_org.items():
            print(f"\n🏢 {org} ({len(org_contacts)} contacts):")
            for contact in org_contacts:
                print(f"  - {contact['name']}")
                print(f"    📧 {contact.get('email', 'N/A')}")
                print(f"    📱 {contact.get('phone', 'N/A')}")

        return contacts

    except RezenError as e:
        print(f"❌ Directory search failed: {e}")
        return []
```

---

## 🔗 Related Documentation

- **[Agents API Reference](../api/agents.md)** - Complete agents API documentation
- **[Teams API Reference](../api/teams.md)** - Detailed teams API reference
- **[Directory API Reference](../api/directory.md)** - Directory services documentation
- **[Error Handling](../reference/exceptions.md)** - Comprehensive error handling guide
- **[Examples](examples.md)** - Additional code examples and patterns
