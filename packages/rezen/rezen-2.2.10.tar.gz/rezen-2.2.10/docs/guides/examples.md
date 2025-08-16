# Examples & Patterns

Real-world usage examples for the ReZEN Python API client. These examples demonstrate common patterns and best practices.

## 📋 Table of Contents

- [Basic Examples](#basic-examples)
- [Transaction Workflows](#transaction-workflows)
- [Agent Management](#agent-management)
- [Team Operations](#team-operations)
- [Error Handling Patterns](#error-handling-patterns)
- [Batch Operations](#batch-operations)
- [Integration Patterns](#integration-patterns)

---

## Basic Examples

### Simple Client Setup

```python
import os
from typing import Optional

from rezen import RezenClient

# Environment variable setup
client: RezenClient = RezenClient()

# Direct API key
client: RezenClient = RezenClient(api_key="your_api_key")

# Custom environment
api_key: Optional[str] = os.getenv('REZEN_API_KEY')
client: RezenClient = RezenClient(
    api_key=api_key,
    base_url="https://staging-api.rezen.com"
)
```

### Basic Search Operations

```python
from typing import List, Dict, Any

from rezen import RezenClient, TeamStatus, AgentStatus

client: RezenClient = RezenClient()

# Quick team search
teams: List[Dict[str, Any]] = client.teams.search_teams(status=TeamStatus.ACTIVE, page_size=10)
print(f"Found {len(teams)} active teams")

# Quick agent search
agents: List[Dict[str, Any]] = client.agents.search_active_agents(name="John", page_size=5)
print(f"Found {len(agents)} agents named John")
```

---

## Transaction Workflows

### Complete Purchase Transaction

```python
from datetime import datetime, timedelta
from typing import Dict, Any

from rezen import RezenClient

def create_purchase_transaction() -> str:
    """Create a complete purchase transaction with all participants.

    Returns:
        Transaction ID of the created transaction

    Raises:
        RezenError: If API requests fail
        ValidationError: If transaction data is invalid
    """
    client: RezenClient = RezenClient()

    # 1. Create transaction builder
    response: Dict[str, Any] = client.transaction_builder.create_transaction_builder("TRANSACTION")
    transaction_id: str = response['id']
    print(f"Created transaction: {transaction_id}")

    # 2. Set property details
    location_data: Dict[str, Any] = {
        "address": "1234 Elm Street",
        "city": "San Francisco",
        "state": "CA",
        "zipCode": "94102",
        "county": "San Francisco"
    }
    client.transaction_builder.update_location_info(transaction_id, location_data)

    # 3. Set pricing and dates
    closing_date: str = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
    price_data: Dict[str, Any] = {
        "purchase_price": 850000,
        "closing_date": closing_date,
        "contract_date": datetime.now().strftime("%Y-%m-%d")
    }
    client.transaction_builder.update_price_and_date_info(transaction_id, price_data)

    # 4. Add buyer
    buyer_data: Dict[str, Any] = {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice.johnson@email.com",
        "phone": "+1-415-555-0123"
    }
    client.transaction_builder.add_buyer(transaction_id, buyer_data)

    # 5. Add seller
    seller_data: Dict[str, Any] = {
        "first_name": "Bob",
        "last_name": "Smith",
        "email": "bob.smith@email.com",
        "phone": "+1-415-555-0456"
    }
    client.transaction_builder.add_seller(transaction_id, seller_data)

    # 6. Add title company
    title_data: Dict[str, Any] = {
        "title_company": "Bay Area Title Company",
        "title_contact": "Sarah Wilson",
        "title_phone": "+1-415-555-0789",
        "title_email": "sarah@bayareatitle.com"
    }
    client.transaction_builder.update_title_info(transaction_id, title_data)

    # 7. Submit transaction
    result: Dict[str, Any] = client.transaction_builder.submit_transaction(transaction_id)
    print(f"Transaction submitted: {result}")

    return transaction_id

# Run example
transaction_id: str = create_purchase_transaction()
```

### Adding Multiple Participants

```python
from typing import List, Dict, Any

from rezen import RezenClient
from rezen.exceptions import RezenError

def add_transaction_participants(transaction_id: str) -> None:
    """Add multiple participants to a transaction.

    Args:
        transaction_id: ID of the transaction to add participants to

    Raises:
        RezenError: If API requests fail
    """
    client: RezenClient = RezenClient()

    # Add various participants
    participants: List[Dict[str, Any]] = [
        {
            "type": "INSPECTOR",
            "first_name": "Mike",
            "last_name": "Inspector",
            "company": "Quality Home Inspections",
            "phone": "+1-415-555-1000"
        },
        {
            "type": "APPRAISER",
            "first_name": "Lisa",
            "last_name": "Appraiser",
            "company": "Bay Area Appraisals",
            "phone": "+1-415-555-2000"
        },
        {
            "type": "LENDER",
            "first_name": "David",
            "last_name": "Banker",
            "company": "First National Bank",
            "phone": "+1-415-555-3000"
        }
    ]

    for participant in participants:
        try:
            response: Dict[str, Any] = client.transaction_builder.add_participant(
                transaction_id, participant
            )
            print(f"Added {participant['type']}: {participant['first_name']} {participant['last_name']}")
        except RezenError as e:
            print(f"Failed to add {participant['type']}: {e}")

# Usage
add_transaction_participants("your-transaction-id")
```

### Commission Setup

```python
from typing import Dict, Any, Optional

from rezen import RezenClient
from rezen.exceptions import RezenError

def setup_commission_splits(transaction_id: str, agent_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Setup commission splits for a transaction.

    Args:
        transaction_id: ID of the transaction
        agent_info: Dictionary containing agent IDs

    Returns:
        Response from API if successful, None if failed

    Raises:
        RezenError: If API request fails
    """
    client: RezenClient = RezenClient()

    # Set commission splits
    commission_splits: List[Dict[str, Any]] = [
        {
            "agent_id": agent_info["listing_agent_id"],
            "role": "LISTING_AGENT",
            "split_percentage": 50.0,
            "commission_amount": 25500  # 3% of $850k
        },
        {
            "agent_id": agent_info["buyers_agent_id"],
            "role": "BUYERS_AGENT",
            "split_percentage": 50.0,
            "commission_amount": 25500  # 3% of $850k
        }
    ]

    try:
        response: Dict[str, Any] = client.transaction_builder.update_commission_splits(
            transaction_id, commission_splits
        )
        print("Commission splits updated successfully")
        return response
    except RezenError as e:
        print(f"Failed to update commission splits: {e}")
        return None

# Usage
agent_data: Dict[str, str] = {
    "listing_agent_id": "agent-uuid-1",
    "buyers_agent_id": "agent-uuid-2"
}
setup_commission_splits("transaction-id", agent_data)
```

### Owner Agent Setup

```python
from typing import Dict, Any

from rezen import RezenClient
from rezen.exceptions import RezenError

def add_owner_agent_to_transaction(transaction_id: str) -> bool:
    """Add owner agent to a transaction using the proper sequence.
    
    ⚠️ CRITICAL: Owner agent endpoint requires the transaction to be set up in this exact order:
    1. Location info (update_location_info)
    2. Price/date info (update_price_and_date_info)
    3. Buyers/Sellers (add_buyer/add_seller)
    4. THEN owner agent can be added
    
    Args:
        transaction_id: ID of an already setup transaction
        
    Returns:
        True if owner agent was added successfully
        
    Raises:
        RezenError: If API request fails
    """
    client: RezenClient = RezenClient()
    
    try:
        # Method 1: Manual owner agent setup
        # Get current user info
        user: Dict[str, Any] = client.users.get_current_user()
        team_id: str = user['team']['id']
        office_id: str = user['office']['id']
        
        # Get agent ID from keymaker
        keymaker: Dict[str, Any] = client.users.get_keymaker_ids(user['id'])
        agent_id: str = keymaker['id']
        
        # Create owner data structure
        owner_data: Dict[str, Any] = {
            "ownerAgent": {
                "agentId": agent_id,
                "role": "BUYERS_AGENT"  # Must match representationType in price/date info
            },
            "officeId": office_id,
            "teamId": team_id
        }
        
        # Add owner agent
        response: Dict[str, Any] = client.transaction_builder.update_owner_agent_info(
            transaction_id, 
            owner_data
        )
        
        print(f"✅ Owner agent added: {user['firstName']} {user['lastName']}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Team: {user['team']['name']}")
        print(f"   Office: {user['office']['name']}")
        
        return True
        
    except RezenError as e:
        print(f"❌ Failed to add owner agent: {e}")
        return False

def create_transaction_with_owner_agent() -> str:
    """Create a complete transaction with owner agent following the proper sequence.
    
    Returns:
        Transaction ID if successful
        
    Raises:
        RezenError: If any step fails
    """
    client: RezenClient = RezenClient()
    
    # Step 1: Create transaction
    response: Dict[str, Any] = client.transaction_builder.create_transaction_builder()
    transaction_id: str = response['id']
    print(f"1️⃣ Created transaction: {transaction_id}")
    
    try:
        # Step 2: Add location (REQUIRED FIRST)
        location_data: Dict[str, Any] = {
            "street": "2158 E Wilson Ave",
            "city": "Salt Lake City",
            "state": "UTAH",  # Must be all caps
            "zip": "84108",  # Use 'zip' not 'zipCode'
            "yearBuilt": 2020,
            "mlsNumber": "MLS123456"
        }
        client.transaction_builder.update_location_info(transaction_id, location_data)
        print("2️⃣ Added location info")
        
        # Step 3: Add price/date (REQUIRED SECOND)
        price_data: Dict[str, Any] = {
            "dealType": "SALE",
            "propertyType": "RESIDENTIAL",
            "salePrice": {
                "amount": 565000,
                "currency": "USD"
            },
            "acceptanceDate": "2024-01-15",
            "closingDate": "2024-02-28",
            "representationType": "BUYER"  # This determines owner agent role
        }
        client.transaction_builder.update_price_and_date_info(transaction_id, price_data)
        print("3️⃣ Added price and dates")
        
        # Step 4: Add buyer (REQUIRED THIRD)
        buyer_data: Dict[str, Any] = {
            "firstName": "John",  # Use camelCase
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phoneNumber": "(801) 555-1234"  # Use camelCase
        }
        client.transaction_builder.add_buyer(transaction_id, buyer_data)
        print("4️⃣ Added buyer")
        
        # Step 5: NOW add owner agent using convenience method
        client.transaction_builder.set_current_user_as_owner_agent(
            transaction_id,
            role="BUYERS_AGENT"  # Must match representationType
        )
        print("5️⃣ Added owner agent - SUCCESS! 🎉")
        
        # Verify owner agent was added
        transaction: Dict[str, Any] = client.transaction_builder.get_transaction_builder(transaction_id)
        owner_agents: List[Dict[str, Any]] = transaction.get('agentsInfo', {}).get('ownerAgent', [])
        
        if owner_agents:
            agent: Dict[str, Any] = owner_agents[0]
            print(f"\n✅ Owner Agent Verified:")
            print(f"   Agent ID: {agent.get('agentId')}")
            print(f"   Role: {agent.get('role')}")
            print(f"   Office ID: {transaction['agentsInfo'].get('officeId')}")
            print(f"   Team ID: {transaction['agentsInfo'].get('teamId')}")
        
        return transaction_id
        
    except RezenError as e:
        print(f"❌ Transaction creation failed: {e}")
        # Clean up
        client.transaction_builder.delete_transaction_builder(transaction_id)
        raise

# Usage examples
# Example 1: Add owner to existing transaction
add_owner_agent_to_transaction("existing-transaction-id")

# Example 2: Create new transaction with owner
transaction_id: str = create_transaction_with_owner_agent()
```

---

## Agent Management

### Agent Search and Analysis

```python
from typing import List, Dict, Any

from rezen import RezenClient, AgentSortField, AgentSortDirection, StateOrProvince
from rezen.exceptions import RezenError

def find_and_analyze_agents() -> None:
    """Find and analyze agents in California.

    Raises:
        RezenError: If API requests fail
    """
    client: RezenClient = RezenClient()

    # Search for agents in California
    california_agents: List[Dict[str, Any]] = client.agents.search_active_agents(
        state_or_province=[StateOrProvince.CALIFORNIA],
        sort_by=[AgentSortField.LAST_NAME, AgentSortField.FIRST_NAME],
        sort_direction=AgentSortDirection.ASC,
        page_size=50
    )

    print(f"Found {len(california_agents)} agents in California")

    # Analyze each agent's network
    for agent in california_agents[:5]:  # Analyze first 5
        agent_id: str = agent['id']
        agent_name: str = f"{agent.get('first_name', '')} {agent.get('last_name', '')}"

        try:
            # Get network size
            network_stats: List[Dict[str, Any]] = client.agents.get_network_size_by_tier(agent_id)

            # Get front line agents
            front_line: List[Dict[str, Any]] = client.agents.get_front_line_agents_info(agent_id)

            print(f"\n{agent_name}:")
            print(f"  Network tiers: {len(network_stats)}")
            print(f"  Front line agents: {len(front_line)}")

        except RezenError as e:
            print(f"  Could not analyze {agent_name}: {e}")

find_and_analyze_agents()
```

### Agent Network Mapping

```python
from typing import Dict, List, Any

from rezen import RezenClient
from rezen.exceptions import RezenError

def map_agent_downline(agent_id: str, max_tier: int = 3) -> Dict[str, Any]:
    """Map an agent's downline network by tier.

    Args:
        agent_id: ID of the agent to map
        max_tier: Maximum tier depth to map

    Returns:
        Dictionary containing network mapping by tier

    Raises:
        RezenError: If API requests fail
    """
    client: RezenClient = RezenClient()

    network_map: Dict[str, Any] = {}

    for tier in range(1, max_tier + 1):
        try:
            downline: List[Dict[str, Any]] = client.agents.get_down_line_agents(
                agent_id=agent_id,
                tier=tier,
                status_in=["ACTIVE"],
                page_size=100
            )

            network_map[f"tier_{tier}"] = {
                "count": len(downline),
                "agents": [
                    {
                        "id": agent["id"],
                        "name": f"{agent.get('first_name', '')} {agent.get('last_name', '')}",
                        "email": agent.get("email", "")
                    }
                    for agent in downline
                ]
            }

            print(f"Tier {tier}: {len(downline)} agents")

        except RezenError as e:
            print(f"Error getting tier {tier}: {e}")
            break

    return network_map

# Usage
agent_network: Dict[str, Any] = map_agent_downline("agent-uuid-here", max_tier=2)
```

---

## Team Operations

### Team Discovery and Management

```python
from typing import Dict, List, Any

from rezen import RezenClient, TeamType, SortField, SortDirection
from rezen.exceptions import RezenError

def discover_teams() -> Dict[str, List[Dict[str, Any]]]:
    """Discover teams by type and analyze them.

    Returns:
        Dictionary of teams organized by type

    Raises:
        RezenError: If API requests fail
    """
    client: RezenClient = RezenClient()

    # Find all team types
    team_types: List[TeamType] = [TeamType.NORMAL, TeamType.PLATINUM, TeamType.GROUP]

    all_teams: Dict[str, List[Dict[str, Any]]] = {}

    for team_type in team_types:
        try:
            teams: List[Dict[str, Any]] = client.teams.search_teams(
                team_type=team_type,
                status="ACTIVE",
                sort_by=[SortField.NAME],
                sort_direction=SortDirection.ASC,
                page_size=100
            )

            all_teams[team_type.value] = teams
            print(f"{team_type.value}: {len(teams)} teams")

            # Show top 3 teams for each type
            for team in teams[:3]:
                print(f"  - {team.get('name', 'N/A')} (ID: {team.get('id')})")

        except RezenError as e:
            print(f"Error getting {team_type.value} teams: {e}")

    return all_teams

teams_by_type: Dict[str, List[Dict[str, Any]]] = discover_teams()
```

### Team Details Analysis

```python
from typing import List, Dict, Any

from rezen import RezenClient
from rezen.exceptions import RezenError

def analyze_team_details(team_ids: List[str]) -> List[Dict[str, Any]]:
    """Analyze details for multiple teams.

    Args:
        team_ids: List of team IDs to analyze

    Returns:
        List of team analysis data

    Raises:
        RezenError: If API requests fail
    """
    client: RezenClient = RezenClient()

    team_analysis: List[Dict[str, Any]] = []

    for team_id in team_ids:
        try:
            team: Dict[str, Any] = client.teams.get_team_without_agents(team_id)

            analysis: Dict[str, Any] = {
                "id": team.get("id"),
                "name": team.get("name"),
                "type": team.get("type"),
                "status": team.get("status"),
                "created_at": team.get("created_at"),
                "leader_name": team.get("leader_name")
            }

            team_analysis.append(analysis)

            print(f"✅ {team.get('name')} - {team.get('type')} ({team.get('status')})")

        except RezenError as e:
            print(f"❌ Error analyzing team {team_id}: {e}")

    return team_analysis

# Usage
team_ids: List[str] = ["team-1", "team-2", "team-3"]
analysis: List[Dict[str, Any]] = analyze_team_details(team_ids)
```

---

## Error Handling Patterns

### Robust API Calls

```python
import time
from typing import Callable, Any, TypeVar

from rezen.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    NetworkError
)

T = TypeVar('T')

def robust_api_call(func: Callable[..., T], *args: Any, max_retries: int = 3, **kwargs: Any) -> T:
    """Make a robust API call with retries and error handling.

    Args:
        func: Function to call
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the function call

    Raises:
        AuthenticationError: If authentication fails (not retried)
        ValidationError: If validation fails (not retried)
        NotFoundError: If resource not found (not retried)
        RateLimitError: If rate limited after all retries
        ServerError: If server error after all retries
        NetworkError: If network error after all retries
        Exception: For unexpected errors
    """
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)

        except AuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            raise  # Don't retry auth errors

        except ValidationError as e:
            print(f"❌ Validation error: {e}")
            raise  # Don't retry validation errors

        except NotFoundError as e:
            print(f"❌ Resource not found: {e}")
            raise  # Don't retry not found errors

        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time: int = 2 ** attempt  # Exponential backoff
                print(f"⚠️ Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            raise

        except (ServerError, NetworkError) as e:
            if attempt < max_retries - 1:
                wait_time: int = 2 ** attempt
                print(f"⚠️ Server/Network error. Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            print(f"❌ Failed after {max_retries} attempts: {e}")
            raise

        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

# Usage examples
from typing import List, Dict, Any

from rezen import RezenClient

client: RezenClient = RezenClient()

# Robust team search
teams: List[Dict[str, Any]] = robust_api_call(
    client.teams.search_teams,
    status="ACTIVE",
    page_size=50
)

# Robust transaction creation
transaction: Dict[str, Any] = robust_api_call(
    client.transaction_builder.create_transaction_builder,
    "TRANSACTION"
)
```

### Validation Helper

```python
from typing import Dict, List, Any

from rezen.exceptions import ValidationError

def validate_transaction_data(transaction_data: Dict[str, Any]) -> bool:
    """Validate transaction data before API calls.

    Args:
        transaction_data: Dictionary containing transaction information

    Returns:
        True if validation passes

    Raises:
        ValidationError: If validation fails with detailed error messages
    """
    errors: List[str] = []

    # Required fields
    required_fields: List[str] = ['address', 'city', 'state', 'zipCode']
    property_data: Dict[str, Any] = transaction_data.get('property', {})

    for field in required_fields:
        if not property_data.get(field):
            errors.append(f"Missing required property field: {field}")

    # Price validation
    price = transaction_data.get('purchase_price')
    if price and (not isinstance(price, (int, float)) or price <= 0):
        errors.append("Purchase price must be a positive number")

    # Email validation (basic)
    participants: List[Dict[str, Any]] = transaction_data.get('participants', [])
    for participant in participants:
        email: str = participant.get('email', '')
        if email and '@' not in email:
            errors.append(f"Invalid email for {participant.get('first_name', 'participant')}: {email}")

    if errors:
        raise ValidationError(f"Transaction validation failed: {'; '.join(errors)}")

    return True

# Usage
transaction_data: Dict[str, Any] = {
    "property": {
        "address": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zipCode": "90210"
    },
    "purchase_price": 500000,
    "participants": [
        {"first_name": "John", "email": "john@email.com"}
    ]
}

try:
    validate_transaction_data(transaction_data)
    print("✅ Transaction data is valid")
except ValidationError as e:
    print(f"❌ Validation failed: {e}")
```

---

## Batch Operations

### Batch Agent Lookup

```python
def batch_agent_lookup(agent_identifiers, lookup_type="email"):
    """Look up multiple agents by email or ID."""
    client = RezenClient()

    results = {
        "found": [],
        "not_found": [],
        "errors": []
    }

    for identifier in agent_identifiers:
        try:
            if lookup_type == "email":
                agents = client.agents.get_agents_by_email(identifier)
            elif lookup_type == "id":
                agents = client.agents.get_agents_by_ids([identifier])
            else:
                raise ValueError(f"Unknown lookup_type: {lookup_type}")

            if agents:
                results["found"].extend(agents)
                print(f"✅ Found agent(s) for {identifier}")
            else:
                results["not_found"].append(identifier)
                print(f"❌ No agent found for {identifier}")

        except Exception as e:
            results["errors"].append({"identifier": identifier, "error": str(e)})
            print(f"❌ Error looking up {identifier}: {e}")

    return results

# Usage
emails = ["agent1@email.com", "agent2@email.com", "nonexistent@email.com"]
results = batch_agent_lookup(emails, lookup_type="email")

print(f"\nResults: {len(results['found'])} found, {len(results['not_found'])} not found, {len(results['errors'])} errors")
```

### Bulk Team Analysis

```python
def bulk_team_analysis(team_search_criteria):
    """Analyze multiple teams based on search criteria."""
    client = RezenClient()

    all_teams = []
    analysis_results = []

    # Get teams for each criteria
    for criteria in team_search_criteria:
        try:
            teams = client.teams.search_teams(**criteria)
            all_teams.extend(teams)
            print(f"Found {len(teams)} teams for criteria: {criteria}")
        except Exception as e:
            print(f"Error searching teams with {criteria}: {e}")

    # Analyze each team
    for team in all_teams:
        team_id = team.get('id')
        try:
            team_details = client.teams.get_team_without_agents(team_id)

            analysis = {
                "id": team_id,
                "name": team_details.get("name"),
                "type": team_details.get("type"),
                "status": team_details.get("status"),
                "analysis_date": datetime.now().isoformat()
            }

            analysis_results.append(analysis)

        except Exception as e:
            print(f"Error analyzing team {team_id}: {e}")

    return analysis_results

# Usage
search_criteria = [
    {"team_type": "PLATINUM", "status": "ACTIVE"},
    {"team_type": "NORMAL", "status": "ACTIVE", "page_size": 20},
    {"search_text": "sales"}
]

analysis = bulk_team_analysis(search_criteria)
print(f"Analyzed {len(analysis)} teams total")
```

---

## Integration Patterns

### Flask Web Application Integration

```python
from flask import Flask, jsonify, request
from rezen import RezenClient
from rezen.exceptions import RezenError

app = Flask(__name__)
client = RezenClient()

@app.route('/api/teams/search')
def search_teams():
    try:
        # Get query parameters
        status = request.args.get('status', 'ACTIVE')
        team_type = request.args.get('team_type')
        page_size = int(request.args.get('page_size', 20))

        # Search teams
        teams = client.teams.search_teams(
            status=status,
            team_type=team_type,
            page_size=page_size
        )

        return jsonify({
            "success": True,
            "data": teams,
            "count": len(teams)
        })

    except RezenError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal server error"
        }), 500

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    try:
        data = request.get_json()

        # Create transaction
        response = client.transaction_builder.create_transaction_builder()
        transaction_id = response['id']

        # Add property details if provided
        if 'property' in data:
            client.transaction_builder.update_location_info(
                transaction_id, data['property']
            )

        return jsonify({
            "success": True,
            "transaction_id": transaction_id
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400

if __name__ == '__main__':
    app.run(debug=True)
```

### Data Export Utility

```python
import csv
from datetime import datetime

def export_teams_to_csv(filename=None):
    """Export team data to CSV file."""
    if not filename:
        filename = f"teams_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    client = RezenClient()

    # Get all active teams
    teams = client.teams.search_teams(status="ACTIVE", page_size=1000)

    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'name', 'type', 'status', 'leader_name', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for team in teams:
            # Get detailed team info
            try:
                team_details = client.teams.get_team_without_agents(team['id'])

                row = {
                    'id': team_details.get('id'),
                    'name': team_details.get('name'),
                    'type': team_details.get('type'),
                    'status': team_details.get('status'),
                    'leader_name': team_details.get('leader_name'),
                    'created_at': team_details.get('created_at')
                }

                writer.writerow(row)

            except Exception as e:
                print(f"Error processing team {team['id']}: {e}")

    print(f"Exported {len(teams)} teams to {filename}")
    return filename

# Usage
filename = export_teams_to_csv()
```

### Configuration Management

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class RezenConfig:
    """Configuration management for ReZEN client."""
    api_key: str
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3

    @classmethod
    def from_environment(cls):
        """Load configuration from environment variables."""
        api_key = os.getenv('REZEN_API_KEY')
        if not api_key:
            raise ValueError("REZEN_API_KEY environment variable is required")

        return cls(
            api_key=api_key,
            base_url=os.getenv('REZEN_BASE_URL'),
            timeout=int(os.getenv('REZEN_TIMEOUT', 30)),
            max_retries=int(os.getenv('REZEN_MAX_RETRIES', 3))
        )

    def create_client(self):
        """Create a ReZEN client with this configuration."""
        return RezenClient(
            api_key=self.api_key,
            base_url=self.base_url
        )

# Usage
config = RezenConfig.from_environment()
client = config.create_client()
```

---

## Testing Patterns

### Mock Testing Setup

```python
import unittest
from unittest.mock import Mock, patch
from rezen import RezenClient

class TestRezenIntegration(unittest.TestCase):

    def setUp(self):
        self.client = RezenClient(api_key="test_key")

    @patch('rezen.teams.TeamsClient.search_teams')
    def test_team_search(self, mock_search):
        # Mock response
        mock_search.return_value = [
            {"id": "team-1", "name": "Test Team", "type": "NORMAL"}
        ]

        # Test
        teams = self.client.teams.search_teams(status="ACTIVE")

        # Assertions
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0]["name"], "Test Team")
        mock_search.assert_called_once_with(status="ACTIVE")

    @patch('rezen.transaction_builder.TransactionBuilderClient.create_transaction_builder')
    def test_transaction_creation(self, mock_create):
        # Mock response
        mock_create.return_value = {"id": "tx-12345"}

        # Test
        response = self.client.transaction_builder.create_transaction_builder()

        # Assertions
        self.assertEqual(response["id"], "tx-12345")
        mock_create.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

---

These examples demonstrate real-world usage patterns and best practices for the ReZEN API client. Each pattern can be adapted and combined based on your specific integration needs.

For more specific use cases or custom patterns, refer to the [API Reference](../api/index.md) for detailed method documentation.
