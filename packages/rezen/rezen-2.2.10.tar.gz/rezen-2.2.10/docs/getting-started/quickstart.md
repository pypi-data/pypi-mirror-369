# Quick Start Guide

Get up and running with the ReZEN API in 5 minutes! This guide walks you through your first API calls.

## 🎯 Goal

By the end of this guide, you'll:
- ✅ Set up authentication
- ✅ Make your first API call
- ✅ Search for teams and agents
- ✅ Create a simple transaction

## 📋 Prerequisites

- Python 3.7+ installed
- ReZEN API key ([get one here](https://platform.rezen.com))
- 5 minutes ⏱️

## 🚀 Step 1: Install & Setup

### Install the Package

```bash
pip install rezen
```

### Set Your API Key

```bash
# Set environment variable (recommended)
export REZEN_API_KEY="your_api_key_here"
```

## 🔌 Step 2: First Connection

Create a file called `quickstart.py`:

```python
from typing import Optional

from rezen import RezenClient

# Initialize client (uses REZEN_API_KEY environment variable)
client: RezenClient = RezenClient()

print("🚀 ReZEN Client initialized!")
print(f"📦 Version: {client.__module__}")
```

Run it:
```bash
python quickstart.py
```

## 👥 Step 3: Search for Teams

Let's find some teams to work with:

```python
from typing import Dict, List, Any

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError, AuthenticationError

client: RezenClient = RezenClient()

# Search for active teams
try:
    teams: List[Dict[str, Any]] = client.teams.search_teams(
        status="ACTIVE",
        limit=5
    )

    print(f"✅ Found {len(teams)} teams")

    for team in teams:
        print(f"🏢 Team: {team.get('name', 'N/A')}")
        print(f"   ID: {team.get('id')}")
        print(f"   Type: {team.get('type', 'N/A')}")
        print()

except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
except RezenError as e:
    print(f"❌ API error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

**Expected Output:**
```
✅ Found 3 teams
🏢 Team: Downtown Realty
   ID: team-12345
   Type: NORMAL

🏢 Team: Premier Properties
   ID: team-67890
   Type: PLATINUM
```

## 🤝 Step 4: Search for Agents

Now let's find some agents:

```python
from typing import Dict, List, Any

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError, AuthenticationError

client: RezenClient = RezenClient()

# Search for active agents
try:
    agents: List[Dict[str, Any]] = client.agents.search_active_agents(
        name="John",  # Search by name
        limit=3
    )

    print(f"✅ Found {len(agents)} agents")

    for agent in agents:
        print(f"👤 Agent: {agent.get('first_name', '')} {agent.get('last_name', '')}")
        print(f"   ID: {agent.get('id')}")
        print(f"   Email: {agent.get('email', 'N/A')}")
        print()

except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
except RezenError as e:
    print(f"❌ API error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## 🏗️ Step 5: Create a Transaction Builder

Let's create your first transaction:

```python
from typing import Dict, Any, Optional

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError, AuthenticationError

client: RezenClient = RezenClient()

# Create a simple purchase transaction
transaction_data: Dict[str, Any] = {
    "type": "PURCHASE",
    "property": {
        "address": "123 Main Street",
        "city": "Anytown",
        "state": "CA",
        "zipCode": "90210"
    },
    "purchase_price": 500000
}

try:
    # Create transaction builder
    response: Dict[str, Any] = client.transaction_builder.create_transaction_builder(transaction_data)

    transaction_id: str = response.get('id')
    print(f"✅ Transaction created!")
    print(f"🆔 Transaction ID: {transaction_id}")
    print(f"🏠 Property: {transaction_data['property']['address']}")
    print(f"💰 Price: ${transaction_data['purchase_price']:,}")

except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
except RezenError as e:
    print(f"❌ API error: {e}")
except Exception as e:
    print(f"❌ Unexpected error creating transaction: {e}")
```

## 📋 Step 6: Add Participants

Let's add a buyer to our transaction:

```python
from typing import Dict, Any

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError, AuthenticationError

client: RezenClient = RezenClient()

# Assuming you have a transaction_id from Step 5
transaction_id: str = "your-transaction-id-here"

buyer_data: Dict[str, Any] = {
    "type": "BUYER",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@email.com",
    "phone": "+1-555-123-4567"
}

try:
    # Add buyer to transaction
    buyer_response: Dict[str, Any] = client.transaction_builder.add_buyer(
        transaction_id=transaction_id,
        buyer_data=buyer_data
    )

    print(f"✅ Buyer added!")
    print(f"👤 Name: {buyer_data['first_name']} {buyer_data['last_name']}")
    print(f"📧 Email: {buyer_data['email']}")

except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
except RezenError as e:
    print(f"❌ API error: {e}")
except Exception as e:
    print(f"❌ Unexpected error adding buyer: {e}")
```

## 📊 Step 7: Get Transaction Status

Check your transaction:

```python
from typing import Dict, List, Any

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError, AuthenticationError, NotFoundError

client: RezenClient = RezenClient()
transaction_id: str = "your-transaction-id-here"

try:
    # Get transaction details
    transaction: Dict[str, Any] = client.transactions.get_transaction(transaction_id)

    print(f"✅ Transaction Details:")
    print(f"🆔 ID: {transaction.get('id')}")
    print(f"📍 Status: {transaction.get('status', 'N/A')}")
    print(f"🏠 Property: {transaction.get('property', {}).get('address', 'N/A')}")

    # Show participants
    participants: List[Dict[str, Any]] = transaction.get('participants', [])
    print(f"👥 Participants: {len(participants)}")

    for participant in participants:
        print(f"   - {participant.get('type')}: {participant.get('first_name')} {participant.get('last_name')}")

except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
except NotFoundError as e:
    print(f"❌ Transaction not found: {e}")
except ValidationError as e:
    print(f"❌ Validation error: {e}")
except RezenError as e:
    print(f"❌ API error: {e}")
except Exception as e:
    print(f"❌ Unexpected error getting transaction: {e}")
```

## 🎯 Complete Example

Here's everything together in one script:

```python
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from rezen import RezenClient
from rezen.exceptions import RezenError, ValidationError, AuthenticationError, NotFoundError


def main() -> None:
    """Main function demonstrating ReZEN API usage.

    This function shows a complete workflow including:
    - Searching for teams and agents
    - Creating a transaction
    - Adding participants
    - Checking transaction status

    Raises:
        RezenError: If API requests fail
        AuthenticationError: If API key is invalid
        ValidationError: If request data is invalid
    """
    # Initialize client
    print("🚀 Initializing ReZEN client...")
    client: RezenClient = RezenClient()

    # 1. Search for teams
    print("\n1️⃣ Searching for teams...")
    try:
        teams: List[Dict[str, Any]] = client.teams.search_teams(status="ACTIVE", limit=2)
        print(f"✅ Found {len(teams)} teams")
        for team in teams[:1]:  # Show first team
            print(f"   🏢 {team.get('name', 'N/A')} (ID: {team.get('id')})")
    except (AuthenticationError, ValidationError, RezenError) as e:
        print(f"❌ Teams error: {e}")

    # 2. Search for agents
    print("\n2️⃣ Searching for agents...")
    try:
        agents: List[Dict[str, Any]] = client.agents.search_active_agents(limit=2)
        print(f"✅ Found {len(agents)} agents")
        for agent in agents[:1]:  # Show first agent
            name: str = f"{agent.get('first_name', '')} {agent.get('last_name', '')}"
            print(f"   👤 {name} (ID: {agent.get('id')})")
    except (AuthenticationError, ValidationError, RezenError) as e:
        print(f"❌ Agents error: {e}")

    # 3. Create transaction
    print("\n3️⃣ Creating transaction...")
    transaction_data: Dict[str, Any] = {
        "type": "PURCHASE",
        "property": {
            "address": "123 Quick Start Ave",
            "city": "Demo City",
            "state": "CA",
            "zipCode": "90210"
        },
        "purchase_price": 750000
    }

    try:
        response: Dict[str, Any] = client.transaction_builder.create_transaction_builder(transaction_data)
        transaction_id: str = response.get('id')
        print(f"✅ Transaction created: {transaction_id}")
    except (AuthenticationError, ValidationError, RezenError) as e:
        print(f"❌ Transaction error: {e}")
        return

    # 4. Add buyer
    print("\n4️⃣ Adding buyer...")
    buyer_data: Dict[str, Any] = {
        "type": "BUYER",
        "first_name": "Quick",
        "last_name": "Start",
        "email": "quickstart@demo.com",
        "phone": "+1-555-DEMO-123"
    }

    try:
        client.transaction_builder.add_buyer(
            transaction_id=transaction_id,
            buyer_data=buyer_data
        )
        print(f"✅ Buyer added: {buyer_data['first_name']} {buyer_data['last_name']}")
    except (AuthenticationError, ValidationError, RezenError) as e:
        print(f"❌ Buyer error: {e}")

    # 5. Get final status
    print("\n5️⃣ Checking transaction status...")
    try:
        transaction: Dict[str, Any] = client.transactions.get_transaction(transaction_id)
        print(f"✅ Transaction Status: {transaction.get('status', 'N/A')}")
        print(f"👥 Participants: {len(transaction.get('participants', []))}")
    except (AuthenticationError, NotFoundError, ValidationError, RezenError) as e:
        print(f"❌ Status error: {e}")

    print("\n🎉 Quick start complete!")
    print(f"🆔 Your transaction ID: {transaction_id}")


if __name__ == "__main__":
    main()
```

## 🚨 Error Handling

Add proper error handling for production code:

```python
from typing import List, Dict, Any

from rezen import RezenClient
from rezen.exceptions import (
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    RezenError
)

client: RezenClient = RezenClient()

try:
    teams: List[Dict[str, Any]] = client.teams.search_teams()
    print(f"Success: {len(teams)} teams found")

except AuthenticationError as e:
    print(f"❌ Check your API key: {e}")

except ValidationError as e:
    print(f"❌ Invalid request: {e}")

except NotFoundError as e:
    print(f"❌ Resource not found: {e}")

except RateLimitError as e:
    print(f"❌ Rate limit exceeded - wait and retry: {e}")

except RezenError as e:
    print(f"❌ API error: {e}")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
```

## 🎯 What's Next?

Now that you've completed the quick start:

### 📚 Learn More
- **[API Reference](../api/index.md)** - Complete endpoint documentation
- **[Examples](../guides/examples.md)** - Real-world usage patterns
- **[Error Handling](../guides/troubleshooting.md)** - Robust error handling

### 🔧 Common Tasks
- **Transaction Management** - Work with existing transactions
- **Batch Operations** - Process multiple items efficiently
- **Advanced Queries** - Complex search and filtering

### 🏗️ Production Ready
- **Environment Configuration** - Staging vs production
- **Logging & Monitoring** - Track API usage
- **Testing Strategies** - Unit and integration tests

## 💡 Tips for Success

### 🔍 **Explore the API**
```python
from rezen import RezenClient

client: RezenClient = RezenClient()

# Get help on any client
help(client.transaction_builder)
help(client.transactions)
help(client.teams)
help(client.agents)
```

### 📝 **Keep Transaction IDs**
Save transaction IDs for later operations:
```python
from typing import List

# Store important IDs
important_transactions: List[str] = []
response = client.transaction_builder.create_transaction_builder(data)
important_transactions.append(response['id'])
```

### ⚡ **Use Type Hints**
Get better IDE support:
```python
from typing import List, Dict, Any

from rezen import RezenClient

client: RezenClient = RezenClient()
teams: List[Dict[str, Any]] = client.teams.search_teams()
```

## 🆘 Need Help?

- **📖 Documentation**: [Full API Reference](../api/index.md)
- **💡 Examples**: [Common Patterns](../guides/examples.md)
- **🐛 Issues**: [Troubleshooting Guide](../guides/troubleshooting.md)
- **💬 Support**: [Contact Support](mailto:support@rezen.com)

---

**🎉 Congratulations!** You've successfully:
- ✅ Connected to the ReZEN API
- ✅ Searched teams and agents
- ✅ Created a transaction
- ✅ Added participants
- ✅ Retrieved transaction status

**Ready for more?** Continue to the [API Reference](../api/index.md) for complete documentation.
