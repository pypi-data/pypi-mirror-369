# Checklist API

Comprehensive API for managing checklists, checklist items, documents, and progress tracking.

---

## Overview

!!! abstract "Checklist API Features"

    The ChecklistClient provides complete access to ReZEN's checklist functionality:
    
    - **✅ Checklist Management**: Create, retrieve, and update checklists
    - **📋 Item Operations**: Add, update, delete, and complete checklist items
    - **📄 Document Handling**: Upload documents and manage versions
    - **📊 Progress Tracking**: Monitor checklist completion status
    - **🔄 Batch Operations**: Update multiple checklists efficiently
    - **💾 File Downloads**: Retrieve document versions

---

## Quick Start

```python
from rezen import ChecklistClient

# Initialize client (uses REZEN_API_KEY from environment)
client = ChecklistClient()

# Get a checklist
checklist = client.get_checklist("3fa85f64-5717-4562-b3fc-2c963f66afa6")

# Get checklist item details
item = client.get_checklist_item("4fa85f64-5717-4562-b3fc-2c963f66afa7")

# Mark item as complete
client.complete_checklist_item(item["id"], is_complete=True)
```

---

## Endpoint Reference

### Checklist Operations

#### Get Checklist

::: rezen.checklist.ChecklistClient.get_checklist
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
checklist = client.get_checklist("3fa85f64-5717-4562-b3fc-2c963f66afa6")

# Response structure
{
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "createdAt": 1640995200000,
    "name": "Transaction Checklist",
    "items": [...],
    "approved": False,
    "locked": False,
    "checklistDefinitionId": "...",
    "fileApiVersion": "V1"
}
```

#### Create Checklist

::: rezen.checklist.ChecklistClient.create_checklist
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
checklist_data = {
    "parentId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "parentType": "TRANSACTION",
    "assignees": {
        "agent1": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "agent2": "4fa85f64-5717-4562-b3fc-2c963f66afa7"
    },
    "brokerAgentId": "broker-123",
    "ownerAgentId": "owner-123"
}

result = client.create_checklist(
    checklist_definition_id="def-123",
    checklist_data=checklist_data
)
```

#### Get Checklist Progress

::: rezen.checklist.ChecklistClient.get_checklists_progress
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
checklist_ids = ["checklist-1", "checklist-2", "checklist-3"]
progress = client.get_checklists_progress(checklist_ids)

# Response structure (list of progress objects)
[
    {
        "checklistId": "checklist-1",
        "itemCount": 10,
        "completedCount": 7,
        "itemCountIncludingOptionals": 12,
        "completedCountIncludingOptionals": 8
    },
    ...
]
```

#### Batch Update Checklists

::: rezen.checklist.ChecklistClient.batch_update_checklists
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
batch_items = [
    {
        "checklistId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "patch": {"locked": True}
    },
    {
        "checklistId": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
        "patch": {"approved": True}
    }
]

result = client.batch_update_checklists(batch_items)
```

---

### Checklist Item Operations

#### Get Checklist Item

::: rezen.checklist.ChecklistClient.get_checklist_item
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
item = client.get_checklist_item("3fa85f64-5717-4562-b3fc-2c963f66afa6")

# Response structure
{
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "createdAt": 1640995200000,
    "name": "Property Inspection",
    "checklistId": "...",
    "description": "Complete property inspection",
    "position": 1,
    "dueDate": "2025-06-09",
    "required": True,
    "urgent": False,
    "complete": False,
    "documents": [...],
    "labels": [...]
}
```

#### Create Checklist Item

::: rezen.checklist.ChecklistClient.create_checklist_item
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
item_data = {
    "item": {
        "name": "Final Walkthrough",
        "description": "Conduct final property walkthrough with buyer",
        "position": 10,
        "dueDate": "2025-06-09",
        "required": True,
        "urgent": False,
        "labels": [
            {
                "text": "Buyer Required"
            }
        ]
    }
}

result = client.create_checklist_item(
    checklist_id="checklist-123",
    item_data=item_data
)
```

#### Update Checklist Item

::: rezen.checklist.ChecklistClient.update_checklist_item
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
update_data = {
    "item": {
        "id": "item-123",
        "name": "Updated Item Name",
        "description": "Updated description",
        "dueDate": "2025-07-01",
        "urgent": True,
        "complete": False
    }
}

result = client.update_checklist_item(
    checklist_item_id="item-123",
    item_data=update_data
)
```

#### Delete Checklist Item

::: rezen.checklist.ChecklistClient.delete_checklist_item
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
result = client.delete_checklist_item("item-123")

# Response
{
    "status": True,
    "message": "Checklist item deleted successfully"
}
```

#### Complete Checklist Item

::: rezen.checklist.ChecklistClient.complete_checklist_item
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
# Mark as complete
client.complete_checklist_item("item-123", is_complete=True)

# Mark as incomplete
client.complete_checklist_item("item-123", is_complete=False)
```

---

### Document Upload Approaches

!!! important "Two Ways to Upload Documents"

    The ReZEN API supports two different approaches for uploading documents to checklist items:

#### 1. Direct Upload (Traditional Method)

Use `add_document_to_checklist_item` when:
- The transaction doesn't have Dropbox integration
- The transaction's `dropboxId` field is null or missing
- You want a simple one-step upload

```python
# Check if transaction has Dropbox
transaction = client.transactions.get_transaction(transaction_id)
if not transaction.get("dropboxId"):
    # Use direct upload
    with open("document.pdf", "rb") as file:
        result = client.checklist.add_document_to_checklist_item(
            checklist_item_id="item-123",
            name="MLS Sheet",
            description="Property listing details",
            uploader_id="user-456",
            transaction_id=transaction_id,
            file=file
        )
```

#### 2. Dropbox Upload (Two-Step Process)

Use this approach when:
- The transaction has a `dropboxId` field
- Direct upload fails with 403 Forbidden
- You need to integrate with the transaction's Dropbox storage

**Step 1: Upload to Dropbox**
```python
import requests

# Get transaction details
transaction = client.transactions.get_transaction(transaction_id)
dropbox_id = transaction["dropboxId"]

# Upload to Dropbox
api_key = client.transactions.api_key  # Get API key from sub-client
headers = {"Authorization": f"Bearer {api_key}"}
files = {"file": ("document.pdf", open("document.pdf", "rb"), "application/pdf")}
data = {"uploadedBy": user_id}

response = requests.post(
    f"https://dropbox.therealbrokerage.com/api/v1/dropboxes/{dropbox_id}/files",
    headers=headers,
    files=files,
    data=data
)

file_info = response.json()
file_id = file_info["id"]
```

**Step 2: Link to Checklist Item**
```python
# Link the uploaded file to the checklist item
result = client.checklist.link_file_to_checklist_item(
    checklist_item_id="item-123",
    file_references=[{
        "fileId": file_id,
        "filename": file_info["filename"]
    }]
)
```

#### Link File to Checklist Item

::: rezen.checklist.ChecklistClient.link_file_to_checklist_item
    options:
      show_source: false
      heading_level: 4

**Complete Dropbox Upload Example:**
```python
# See examples/upload_to_checklist_via_dropbox.py for a full working example
def upload_via_dropbox(transaction_id: str, checklist_item_id: str, file_path: str):
    """Upload document using Dropbox approach."""
    client = RezenClient()
    
    # Get transaction and user info
    transaction = client.transactions.get_transaction(transaction_id)
    dropbox_id = transaction.get("dropboxId")
    if not dropbox_id:
        raise ValueError("Transaction doesn't have Dropbox integration")
    
    user = client.users.get_current_user()
    user_id = user["id"]
    
    # Step 1: Upload to Dropbox
    api_key = client.transactions.api_key
    headers = {"Authorization": f"Bearer {api_key}"}
    
    with open(file_path, "rb") as file:
        files = {"file": (os.path.basename(file_path), file, "application/pdf")}
        data = {"uploadedBy": user_id}
        
        response = requests.post(
            f"https://dropbox.therealbrokerage.com/api/v1/dropboxes/{dropbox_id}/files",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Dropbox upload failed: {response.status_code}")
        
        file_info = response.json()
    
    # Step 2: Link to checklist item
    result = client.checklist.link_file_to_checklist_item(
        checklist_item_id=checklist_item_id,
        file_references=[{
            "fileId": file_info["id"],
            "filename": file_info["filename"]
        }]
    )
    
    return result
```

---

### Document Operations

#### Get Checklist Document

::: rezen.checklist.ChecklistClient.get_checklist_document
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
document = client.get_checklist_document("doc-123")

# Response structure
{
    "id": "doc-123",
    "createdAt": 1640995200000,
    "name": "Purchase Agreement",
    "description": "Signed purchase agreement",
    "versions": [
        {
            "id": "version-1",
            "name": "Version 1.0",
            "number": 1,
            "uploaderId": "user-123",
            "path": "documents/purchase-agreement-v1.pdf"
        }
    ],
    "currentVersion": {...},
    "documentDefinitionId": "..."
}
```

#### Update Checklist Document

::: rezen.checklist.ChecklistClient.update_checklist_document
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
document_data = {
    "id": "doc-123",
    "name": "Updated Purchase Agreement",
    "description": "Updated with amendments",
    "currentVersion": {
        "id": "version-2"
    }
}

result = client.update_checklist_document(
    document_id="doc-123",
    document_data=document_data
)
```

#### Delete Checklist Document

::: rezen.checklist.ChecklistClient.delete_checklist_document
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
result = client.delete_checklist_document("doc-123")
```

#### Add Document to Checklist Item

::: rezen.checklist.ChecklistClient.add_document_to_checklist_item
    options:
      show_source: false
      heading_level: 4

!!! warning "Document Upload Approaches"

    There are two ways to upload documents to checklist items:
    
    1. **Direct Upload** (this method) - Use when the transaction doesn't have Dropbox integration
    2. **Dropbox Upload** (two-step process) - Use when transaction has a `dropboxId`
    
    See the [Document Upload Approaches](#document-upload-approaches) section for details.

**Example:**
```python
# Direct upload approach
with open("contract.pdf", "rb") as file:
    result = client.add_document_to_checklist_item(
        checklist_item_id="item-123",
        name="Purchase Contract",
        description="Signed purchase contract",
        uploader_id="user-456",
        transaction_id="txn-789",
        file=file
    )

# Note: This may fail with 403 if:
# - User is not a participant on the transaction
# - Transaction uses Dropbox storage instead
```

#### Add Document Version

::: rezen.checklist.ChecklistClient.add_document_version
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
with open("contract-v2.pdf", "rb") as file:
    result = client.add_document_version(
        checklist_document_id="doc-123",
        name="Version 2.0",
        description="Updated with amendments",
        uploader_id="user-456",
        transaction_id="txn-789",
        file=file
    )

# Response includes new version details
{
    "id": "version-2",
    "name": "Version 2.0",
    "description": "Updated with amendments",
    "number": 2,
    "uploaderId": "user-456",
    "path": "documents/contract-v2.pdf"
}
```

#### Download Document Version

::: rezen.checklist.ChecklistClient.download_document_version
    options:
      show_source: false
      heading_level: 4

**Example:**
```python
result = client.download_document_version("version-123")

# Response contains download URL
{
    "downloadUrl": "https://example.com/secure/download/doc.pdf"
}
```

---

## Usage Examples

### Complete Checklist Workflow

!!! example "End-to-End Checklist Management"

    ```python
    from rezen import ChecklistClient
    from rezen.exceptions import NotFoundError, ValidationError
    
    def manage_transaction_checklist(transaction_id: str):
        """Complete checklist workflow for a transaction."""
        client = ChecklistClient()
        
        try:
            # 1. Create a new checklist
            print("Creating checklist...")
            checklist_data = {
                "parentId": transaction_id,
                "parentType": "TRANSACTION",
                "assignees": {
                    "listing_agent": "agent-123",
                    "buyer_agent": "agent-456"
                }
            }
            
            checklist_result = client.create_checklist(
                checklist_definition_id="standard-purchase",
                checklist_data=checklist_data
            )
            checklist_id = checklist_result["checklistId"]
            
            # 2. Get the checklist details
            checklist = client.get_checklist(checklist_id)
            print(f"Created checklist: {checklist['name']}")
            
            # 3. Add custom items
            custom_item = {
                "item": {
                    "name": "Home Warranty Decision",
                    "description": "Buyer to decide on home warranty",
                    "required": False,
                    "position": 99,
                    "dueDate": "2025-06-15"
                }
            }
            
            item_result = client.create_checklist_item(
                checklist_id=checklist_id,
                item_data=custom_item
            )
            print(f"Added custom item: {item_result['id']}")
            
            # 4. Process existing items
            checklist = client.get_checklist(checklist_id)
            for item in checklist["items"]:
                if item["required"] and not item["complete"]:
                    print(f"\nProcessing: {item['name']}")
                    
                    # Upload document if needed
                    if "inspection" in item["name"].lower():
                        upload_inspection_report(client, item["id"], transaction_id)
                    
                    # Mark as complete
                    client.complete_checklist_item(item["id"])
                    print(f"✓ Completed: {item['name']}")
            
            # 5. Check progress
            progress = client.get_checklists_progress([checklist_id])
            if progress:
                prog = progress[0] if isinstance(progress, list) else progress
                print(f"\nProgress: {prog['completedCount']}/{prog['itemCount']} items")
            
            # 6. Lock checklist when done
            client.batch_update_checklists([
                {
                    "checklistId": checklist_id,
                    "patch": {"locked": True, "approved": True}
                }
            ])
            print("Checklist locked and approved!")
            
            return checklist_id
            
        except NotFoundError as e:
            print(f"Resource not found: {e}")
        except ValidationError as e:
            print(f"Validation error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None
    
    def upload_inspection_report(client, item_id, transaction_id):
        """Upload inspection report to checklist item."""
        try:
            with open("inspection_report.pdf", "rb") as file:
                result = client.add_document_to_checklist_item(
                    checklist_item_id=item_id,
                    name="Property Inspection Report",
                    description="Complete inspection findings",
                    uploader_id="inspector-001",
                    transaction_id=transaction_id,
                    file=file
                )
                print(f"  Uploaded: {result['name']}")
        except FileNotFoundError:
            print("  ⚠️  Inspection report not found")
    ```

### Document Version Management

!!! example "Managing Document Versions"

    ```python
    def manage_document_versions(doc_id: str):
        """Demonstrate document version management."""
        client = ChecklistClient()
        
        # Get current document info
        document = client.get_checklist_document(doc_id)
        print(f"Document: {document['name']}")
        print(f"Current version: {document['currentVersion']['number']}")
        
        # Upload new version
        with open("contract-amended.pdf", "rb") as file:
            new_version = client.add_document_version(
                checklist_document_id=doc_id,
                name=f"Version {len(document['versions']) + 1}",
                description="Added inspection contingency",
                uploader_id="agent-123",
                transaction_id="txn-456",
                file=file
            )
        
        print(f"Uploaded version {new_version['number']}")
        
        # Update document to use new version
        client.update_checklist_document(
            document_id=doc_id,
            document_data={
                "currentVersion": {"id": new_version["id"]}
            }
        )
        
        # Get download URL for specific version
        download_info = client.download_document_version(new_version["id"])
        print(f"Download URL: {download_info['downloadUrl']}")
    ```

### Progress Monitoring

!!! example "Monitor Multiple Checklists"

    ```python
    def monitor_checklist_progress(checklist_ids: list):
        """Monitor progress across multiple checklists."""
        client = ChecklistClient()
        
        # Get progress for all checklists
        progress_list = client.get_checklists_progress(checklist_ids)
        
        total_items = 0
        total_completed = 0
        
        print("Checklist Progress Report")
        print("=" * 50)
        
        for progress in progress_list:
            checklist_id = progress["checklistId"]
            completed = progress["completedCount"]
            total = progress["itemCount"]
            percentage = (completed / total * 100) if total > 0 else 0
            
            print(f"\nChecklist: {checklist_id}")
            print(f"Progress: {completed}/{total} ({percentage:.1f}%)")
            print(f"Optional items: {progress['itemCountIncludingOptionals'] - total}")
            
            total_items += total
            total_completed += completed
        
        # Overall summary
        overall_percentage = (total_completed / total_items * 100) if total_items > 0 else 0
        print(f"\n{'=' * 50}")
        print(f"Overall: {total_completed}/{total_items} ({overall_percentage:.1f}%)")
        
        return overall_percentage >= 100
    ```

---

## Error Handling

!!! warning "Common Errors"

    The ChecklistClient properly handles various error scenarios:

    ```python
    from rezen import ChecklistClient
    from rezen.exceptions import (
        NotFoundError,
        ValidationError,
        AuthenticationError,
        ServerError
    )
    
    client = ChecklistClient()
    
    try:
        checklist = client.get_checklist("invalid-id")
    except NotFoundError as e:
        print(f"Checklist not found: {e}")
    except ValidationError as e:
        print(f"Invalid request: {e}")
    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
    except ServerError as e:
        print(f"Server error: {e}")
    ```

---

## Best Practices

!!! tip "Recommended Patterns"

    1. **Always handle exceptions** - Wrap API calls in try-except blocks
    2. **Check item requirements** - Only mark required items as complete when truly done
    3. **Use batch operations** - Update multiple checklists in one call when possible
    4. **Version documents** - Use the version system for document updates
    5. **Monitor progress** - Regularly check completion status
    6. **Validate before locking** - Ensure all required items are complete before locking

!!! info "File Upload Tips"

    - Always use context managers (`with` statement) for file operations
    - Provide meaningful names and descriptions for documents
    - Include the transaction ID for proper association
    - Handle `FileNotFoundError` gracefully

---

## API Reference

### Base Configuration

- **Base URL**: `https://sherlock.therealbrokerage.com/api/v1`
- **Authentication**: Bearer token (API key)
- **Content-Type**: `application/json` (except for file uploads)

### Rate Limits

!!! warning "API Rate Limits"
    
    - Standard rate limit: 100 requests per minute
    - File upload limit: 10 MB per file
    - Batch operations: Maximum 100 items per request

---

## Migration Guide

!!! info "Migrating from Legacy Methods"

    If you're using the old checklist methods, here's how to migrate:

    | Old Method | New Method |
    |------------|------------|
    | `get_checklist_item(checklist_id, item_id)` | `get_checklist_item(item_id)` |
    | `update_checklist_item(checklist_id, item_id, data)` | `update_checklist_item(item_id, data)` |
    | `mark_checklist_item_complete(checklist_id, item_id)` | `complete_checklist_item(item_id, True)` |
    | `post_document_to_checklist(item_id, data, file)` | `add_document_to_checklist_item(...)` |
    | `delete_checklist_item_document(item_id, doc_id)` | `delete_checklist_document(doc_id)` |

---

## Next Steps

<div class="grid cards" markdown>

-   [📄 **Documents API**](documents.md)

    Deep dive into document management

-   [🔄 **Transactions API**](transactions.md)

    Learn about transaction operations

-   [🔌 **API Overview**](index.md)

    Explore other API endpoints

</div> 