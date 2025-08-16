# Dropbox Integration

::: rezen.dropbox.DropboxClient

The Dropbox integration allows agents to connect their Dropbox accounts and manage files and folders within the ReZEN platform.

## Overview

The Dropbox API provides seamless integration between ReZEN and Dropbox, enabling:

- OAuth authentication flow for secure account linking
- File uploads to agent's Dropbox accounts
- Folder creation and navigation
- Document storage for transactions

## Quick Start

```python
from rezen import RezenClient

# Initialize the client
client = RezenClient(api_key="your_api_key")

# Get Dropbox auth URL for agent to authorize
auth_url_response = client.dropbox.get_auth_url()
auth_url = auth_url_response["url"]

# After agent authorizes, save the token
client.dropbox.save_token(code="authorization_code_from_callback")

# Now you can interact with agent's Dropbox
agent_id = "550e8400-e29b-41d4-a716-446655440000"

# List folders
folders = client.dropbox.get_folders(agent_id)

# Create a folder
client.dropbox.create_folder(agent_id, "/Transactions/2024")

# Upload a file
with open("contract.pdf", "rb") as f:
    client.dropbox.upload_file(agent_id, f, "/Transactions/2024/contract.pdf")
```

## Authentication Flow

The Dropbox integration uses OAuth 2.0 for secure authentication:

1. **Get Authorization URL**: Call `get_auth_url()` to get the Dropbox OAuth URL
2. **User Authorization**: Redirect the agent to the URL to authorize access
3. **Save Access Token**: After authorization, save the token using `save_token()`
4. **Use API**: Once authorized, all other endpoints become available

```python
# Step 1: Get auth URL
auth_response = client.dropbox.get_auth_url()
print(f"Please visit: {auth_response['url']}")

# Step 2: Agent authorizes (happens externally)

# Step 3: Save the authorization code
client.dropbox.save_token(code="auth_code_from_callback")

# Step 4: Now you can use the API
folders = client.dropbox.get_folders(agent_id)
```

## Working with Folders

### Listing Folders

List folders in the agent's Dropbox account:

```python
# List root folders
folders = client.dropbox.get_folders(agent_id)

# List folders in a specific path
folders = client.dropbox.get_folders(agent_id, path="/Documents")

# Each folder contains:
# - name: Folder name
# - path: Full path in Dropbox
for folder in folders:
    print(f"{folder['name']} at {folder['path']}")
```

### Creating Folders

Create new folders for organizing documents:

```python
# Create a single folder
client.dropbox.create_folder(agent_id, "/Transactions")

# Create nested folders
client.dropbox.create_folder(agent_id, "/Transactions/2024/January")

# Create folders for specific transaction types
client.dropbox.create_folder(agent_id, "/Transactions/Sales")
client.dropbox.create_folder(agent_id, "/Transactions/Purchases")
```

## File Uploads

Upload files to the agent's Dropbox:

```python
# Upload a PDF document
with open("purchase_agreement.pdf", "rb") as f:
    client.dropbox.upload_file(
        agent_id=agent_id,
        file=f,
        path="/Transactions/2024/purchase_agreement.pdf"
    )

# Upload multiple files
documents = ["contract.pdf", "disclosure.pdf", "inspection.pdf"]
for doc in documents:
    with open(doc, "rb") as f:
        client.dropbox.upload_file(
            agent_id=agent_id,
            file=f,
            path=f"/Transactions/2024/{doc}"
        )
```

## Error Handling

The Dropbox client includes comprehensive error handling:

```python
from rezen.exceptions import ValidationError, NotFoundError, AuthenticationError

try:
    # Attempt to get folders
    folders = client.dropbox.get_folders(agent_id)
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except NotFoundError as e:
    print(f"Agent not found or not authorized: {e}")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

## Best Practices

### 1. Path Naming Conventions

Use consistent path naming for easy organization:

```python
# Good path structure
"/Transactions/2024/01-January/Sale-123MainSt"
"/Clients/John-Doe/Documents"
"/Templates/Contracts"

# Avoid spaces in paths when possible
path = "/Transactions/2024/January"  # Good
path = "/Transactions/2024/January Sales"  # Works but less ideal
```

### 2. File Organization

Organize files by transaction or client:

```python
# Transaction-based organization
transaction_id = "TX-2024-001"
base_path = f"/Transactions/{transaction_id}"

# Create structure
client.dropbox.create_folder(agent_id, base_path)
client.dropbox.create_folder(agent_id, f"{base_path}/Contracts")
client.dropbox.create_folder(agent_id, f"{base_path}/Disclosures")
client.dropbox.create_folder(agent_id, f"{base_path}/Inspections")

# Upload files to appropriate folders
with open("contract.pdf", "rb") as f:
    client.dropbox.upload_file(
        agent_id, f, f"{base_path}/Contracts/purchase_agreement.pdf"
    )
```

### 3. Error Recovery

Implement retry logic for transient failures:

```python
import time
from rezen.exceptions import NetworkError

def upload_with_retry(client, agent_id, file_path, dropbox_path, max_retries=3):
    """Upload file with retry logic."""
    for attempt in range(max_retries):
        try:
            with open(file_path, "rb") as f:
                return client.dropbox.upload_file(agent_id, f, dropbox_path)
        except NetworkError as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

### 4. Batch Operations

For multiple operations, batch them efficiently:

```python
def setup_transaction_folders(client, agent_id, transaction_id):
    """Create standard folder structure for a transaction."""
    base_path = f"/Transactions/{transaction_id}"
    folders = [
        base_path,
        f"{base_path}/Contracts",
        f"{base_path}/Disclosures",
        f"{base_path}/Inspections",
        f"{base_path}/Correspondence",
        f"{base_path}/Financials"
    ]
    
    for folder in folders:
        try:
            client.dropbox.create_folder(agent_id, folder)
            print(f"Created: {folder}")
        except ValidationError:
            print(f"Folder already exists: {folder}")
```

## Complete Examples

### Example 1: Transaction Document Management

```python
from rezen import RezenClient
from datetime import datetime

client = RezenClient()

def setup_transaction_dropbox(agent_id, transaction_id, property_address):
    """Set up Dropbox folders for a new transaction."""
    
    # Create transaction folder
    year = datetime.now().year
    base_path = f"/Transactions/{year}/{transaction_id}"
    
    # Create folder structure
    folders = [
        base_path,
        f"{base_path}/01-Listing",
        f"{base_path}/02-Offers",
        f"{base_path}/03-Contracts",
        f"{base_path}/04-Inspections",
        f"{base_path}/05-Closing"
    ]
    
    for folder in folders:
        client.dropbox.create_folder(agent_id, folder)
    
    # Create info file
    info_content = f"""Transaction: {transaction_id}
Property: {property_address}
Created: {datetime.now().isoformat()}
"""
    
    with open("transaction_info.txt", "w") as f:
        f.write(info_content)
    
    with open("transaction_info.txt", "rb") as f:
        client.dropbox.upload_file(
            agent_id, f, f"{base_path}/transaction_info.txt"
        )
    
    return base_path
```

### Example 2: OAuth Flow Implementation

```python
def implement_dropbox_oauth(client, agent_id):
    """Complete OAuth flow for Dropbox integration."""
    
    # Step 1: Get authorization URL
    auth_response = client.dropbox.get_auth_url()
    auth_url = auth_response["url"]
    
    print(f"Please authorize Dropbox access: {auth_url}")
    
    # Step 2: Wait for callback (in a real app, this would be a webhook)
    auth_code = input("Enter authorization code: ")
    
    # Step 3: Save the token
    try:
        client.dropbox.save_token(code=auth_code)
        print("Successfully connected to Dropbox!")
        
        # Test the connection
        folders = client.dropbox.get_folders(agent_id)
        print(f"Found {len(folders)} folders in Dropbox")
        
        return True
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False
```

### Example 3: Document Upload Workflow

```python
def upload_transaction_documents(client, agent_id, transaction_id, documents):
    """Upload multiple documents for a transaction."""
    
    base_path = f"/Transactions/{transaction_id}"
    results = []
    
    for doc_type, file_path in documents.items():
        # Determine subfolder based on document type
        if "contract" in doc_type.lower():
            subfolder = "Contracts"
        elif "inspection" in doc_type.lower():
            subfolder = "Inspections"
        elif "disclosure" in doc_type.lower():
            subfolder = "Disclosures"
        else:
            subfolder = "Other"
        
        # Upload file
        dropbox_path = f"{base_path}/{subfolder}/{doc_type}.pdf"
        
        try:
            with open(file_path, "rb") as f:
                client.dropbox.upload_file(agent_id, f, dropbox_path)
                results.append({"document": doc_type, "status": "success", "path": dropbox_path})
        except Exception as e:
            results.append({"document": doc_type, "status": "failed", "error": str(e)})
    
    return results

# Usage
documents = {
    "Purchase_Contract": "/tmp/contract.pdf",
    "Property_Disclosure": "/tmp/disclosure.pdf",
    "Home_Inspection": "/tmp/inspection.pdf"
}

results = upload_transaction_documents(
    client, agent_id, "TX-2024-001", documents
)
```

## API Reference

See the [DropboxClient API Reference](../reference/dropbox.md) for detailed method documentation.

## Integration with Checklists

The Dropbox integration is often used in conjunction with transaction checklists. Key points:

- Transactions have a `dropboxId` field that links to their Dropbox storage
- Document uploads to checklist items may require the agent to have Dropbox connected
- Files uploaded through the Dropbox API can be associated with checklist items
- The typical workflow is:
  1. Ensure agent has Dropbox connected (via OAuth flow)
  2. Upload document to Dropbox under transaction folder
  3. Link the Dropbox file to the checklist item

## OAuth Flow 