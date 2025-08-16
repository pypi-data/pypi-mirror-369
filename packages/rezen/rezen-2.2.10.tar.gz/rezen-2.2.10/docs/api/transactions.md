# Transactions API

Work with live transactions, manage participants, and handle financial operations.

---

## Overview

!!! abstract "Transactions API Features"

    - **Transaction Management**: Get and update live transactions
    - **Participant Management**: Add and modify transaction participants
    - **Financial Operations**: Process payments and commission splits
    - **Document Management**: Generate reports and handle transaction documents
    - **Agent Transactions**: Retrieve agent-specific transaction lists
    - **Termination**: Request transaction termination

---

## Quick Start

```python
from rezen import RezenClient

client = RezenClient()

# Get transaction details
transaction = client.transactions.get_transaction("tx-12345")

# Get agent's current transactions
agent_transactions = client.transactions.get_agent_current_transactions("agent-uuid")

# Add participant to existing transaction
participant = {
    "type": "LENDER",
    "first_name": "Bank",
    "last_name": "Officer",
    "company": "First National Bank"
}
client.transactions.create_participant(transaction_id, participant)
```

---

## Core Methods

### Transaction Operations

::: rezen.transactions.TransactionsClient.get_transaction
    options:
      show_source: false
      heading_level: 4

### Agent Transaction Methods

::: rezen.transactions.TransactionsClient.get_agent_transactions
    options:
      show_source: false
      heading_level: 4

::: rezen.transactions.TransactionsClient.get_agent_current_transactions
    options:
      show_source: false
      heading_level: 4

::: rezen.transactions.TransactionsClient.get_agent_current_listings
    options:
      show_source: false
      heading_level: 4

!!! note "Wrapper Methods"
    The agent transaction methods are convenience wrappers around the participant transaction methods for backward compatibility.

### Transaction Termination

::: rezen.transactions.TransactionsClient.request_termination
    options:
      show_source: false
      heading_level: 4

### Participant Management

::: rezen.transactions.TransactionsClient.create_participant
    options:
      show_source: false
      heading_level: 4

::: rezen.transactions.TransactionsClient.get_participant_transactions
    options:
      show_source: false
      heading_level: 4

::: rezen.transactions.TransactionsClient.get_participant_current_transactions
    options:
      show_source: false
      heading_level: 4

### Financial Operations

::: rezen.transactions.TransactionsClient.get_payment_info
    options:
      show_source: false
      heading_level: 4

::: rezen.transactions.TransactionsClient.get_money_transfers
    options:
      show_source: false
      heading_level: 4

### Document Operations

::: rezen.transactions.TransactionsClient.get_transaction_summary_pdf
    options:
      show_source: false
      heading_level: 4

---

## Usage Examples

!!! example "Transaction Management"

    === "Get Transaction"

        ```python
        transaction = client.transactions.get_transaction("tx-12345")
        print(f"Status: {transaction['status']}")
        print(f"Property: {transaction['property']['address']}")
        ```

    === "Agent Transactions"

        ```python
        # Get all agent transactions
        all_transactions = client.transactions.get_agent_transactions("agent-uuid")
        
        # Get current active transactions
        current_transactions = client.transactions.get_agent_current_transactions("agent-uuid")
        
        # Get current listings only
        current_listings = client.transactions.get_agent_current_listings("agent-uuid")
        
        for listing in current_listings:
            print(f"Listing: {listing['address']} - Status: {listing['status']}")
        ```

    === "Add Participant"

        ```python
        lender = {
            "type": "LENDER",
            "first_name": "Sarah",
            "last_name": "Banker",
            "company": "Community Bank",
            "email": "sarah@communitybank.com"
        }

        response = client.transactions.create_participant(
            transaction_id,
            lender
        )
        ```

    === "Get Payment Info"

        ```python
        # Get payment information for an agent
        payment_info = client.transactions.get_payment_info(
            transaction_id,
            agent_id
        )

        print(f"Payment amount: {payment_info['amount']}")
        print(f"Payment status: {payment_info['status']}")
        ```

    === "Request Termination"

        ```python
        # Request to terminate a transaction
        termination_response = client.transactions.request_termination("tx-12345")
        print(f"Termination status: {termination_response['status']}")
        ```

---

## Agent Transaction Retrieval

!!! info "Transaction Filtering"

    The library provides several methods to retrieve agent-specific transactions:

    - **All Transactions**: Get complete transaction history
    - **Current Transactions**: Get only active/current transactions
    - **Current Listings**: Get only listing-type transactions that are current

!!! example "Agent Transaction Examples"

    ```python
    from rezen import RezenClient

    client = RezenClient()
    agent_id = "agent-uuid-here"

    # Get all transactions for an agent
    all_transactions = client.transactions.get_agent_transactions(agent_id)
    print(f"Total transactions: {len(all_transactions)}")

    # Get only current/active transactions
    current = client.transactions.get_agent_current_transactions(agent_id)
    print(f"Active transactions: {len(current)}")

    # Get only current listings
    listings = client.transactions.get_agent_current_listings(agent_id)
    for listing in listings:
        print(f"Property: {listing['property']['address']}")
        print(f"List price: ${listing['listPrice']:,}")
    ```

---

## Document Management

!!! info "Document Types"

    Available document operations include:

    - **Summary PDFs**: Generate transaction summary reports
    - **Document Lists**: Get all transaction-related documents
    - **Status Reports**: Track transaction progress

!!! example "Document Operations"

    ```python
    # Generate summary PDF
    pdf_data = client.transactions.get_transaction_summary_pdf(transaction_id)

    # Get money transfers
    transfers = client.transactions.get_money_transfers(transaction_id)
    for transfer in transfers:
        print(f"Transfer: {transfer['amount']} - Status: {transfer['status']}")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [🔧 **Transaction Builder**](transaction-builder.md)

    Create new transactions from scratch

-   [👔 **Agents API**](agents.md)

    Find agents to add to transactions

-   [✅📄 **Checklist API**](checklist.md)

    Manage transaction checklists and documents

-   [⚠️ **Exceptions**](../reference/exceptions.md)

    Handle transaction-related errors

</div>
