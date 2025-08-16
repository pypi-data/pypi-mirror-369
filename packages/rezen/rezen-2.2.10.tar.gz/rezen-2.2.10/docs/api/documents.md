# Documents API

Manage documents, digital signatures, and document workflows.

---

## Overview

!!! abstract "Documents API Features"

    - **Document Management**: Upload and manage documents
    - **Digital Signatures**: Send documents for electronic signature
    - **Workflow Tracking**: Monitor document status and audit trails
    - **Template Support**: Create documents from templates
    - **Bulk Operations**: Handle multiple documents efficiently

!!! note "Alias Names"
    This API is available as both `client.documents` and `client.signature` for backward compatibility.

---

## Quick Start

```python
from rezen import RezenClient

client = RezenClient()

# Upload document for signature
with open("contract.pdf", "rb") as file:
    document = client.documents.post_document(
        data={
            "title": "Purchase Agreement",
            "signers": [
                {"email": "buyer@example.com", "name": "John Buyer"},
                {"email": "seller@example.com", "name": "Jane Seller"}
            ]
        },
        file=file
    )

# Send for signature
result = client.documents.send_document_for_signature(
    document_id=document['id'],
    data={"message": "Please review and sign the purchase agreement"}
)
```

---

## Core Methods

### Upload Document

::: rezen.documents.DocumentClient.post_document
    options:
      show_source: false
      heading_level: 4

### Get Document

::: rezen.documents.DocumentClient.get_document
    options:
      show_source: false
      heading_level: 4

### Send for Signature

::: rezen.documents.DocumentClient.send_document_for_signature
    options:
      show_source: false
      heading_level: 4

### Get Document Status

::: rezen.documents.DocumentClient.get_document_status
    options:
      show_source: false
      heading_level: 4

### Cancel Signature Request

::: rezen.documents.DocumentClient.cancel_signature_request
    options:
      show_source: false
      heading_level: 4

---

## Document Operations

!!! example "Document Management"

    === "Upload Document"

        ```python
        # Upload document with signers
        with open("contract.pdf", "rb") as file:
            document = client.documents.post_document(
                data={
                    "title": "Sales Contract",
                    "description": "Property sales agreement",
                    "signers": [
                        {
                            "email": "john@example.com",
                            "name": "John Doe",
                            "role": "buyer"
                        },
                        {
                            "email": "jane@example.com",
                            "name": "Jane Smith",
                            "role": "seller"
                        }
                    ],
                    "fields": [
                        {
                            "type": "signature",
                            "page": 1,
                            "x": 100,
                            "y": 200,
                            "signer": "john@example.com"
                        },
                        {
                            "type": "date",
                            "page": 1,
                            "x": 100,
                            "y": 250,
                            "signer": "john@example.com"
                        }
                    ]
                },
                file=file
            )
            
            print(f"Document ID: {document['id']}")
        ```

    === "Check Status"

        ```python
        # Get document status
        status = client.documents.get_document_status(document_id)
        
        print(f"Status: {status['status']}")
        print(f"Completed: {status['completed_count']}/{status['total_signers']}")
        
        for signer in status['signers']:
            print(f"- {signer['name']}: {signer['status']}")
        ```

    === "Send Reminders"

        ```python
        # Send reminder to specific signer
        for signer in document['signers']:
            if signer['status'] == 'pending':
                client.documents.remind_signer(
                    document_id=document['id'],
                    signer_id=signer['id'],
                    message="Gentle reminder to sign the document"
                )
                print(f"Reminder sent to {signer['email']}")
        ```

---

## Signature Workflow

!!! info "Signature Process"

    1. **Upload**: Upload document with signer information
    2. **Configure**: Set signature fields and requirements
    3. **Send**: Send document for signature
    4. **Track**: Monitor signature progress
    5. **Complete**: Download signed document

!!! example "Complete Signature Workflow"

    ```python
    from rezen import RezenClient
    import time
    
    def signature_workflow(file_path: str):
        """Complete document signature workflow."""
        
        client = RezenClient()
        
        # Step 1: Upload document
        with open(file_path, "rb") as file:
            document = client.documents.post_document(
                data={
                    "title": "Contract Agreement",
                    "signers": [
                        {
                            "email": "signer1@example.com",
                            "name": "First Signer",
                            "order": 1
                        },
                        {
                            "email": "signer2@example.com",
                            "name": "Second Signer",
                            "order": 2
                        }
                    ]
                },
                file=file
            )
        
        document_id = document['id']
        print(f"Document uploaded: {document_id}")
        
        # Step 2: Send for signature
        client.documents.send_document_for_signature(
            document_id=document_id,
            data={
                "message": "Please sign this agreement",
                "subject": "Contract Ready for Signature"
            }
        )
        print("Document sent for signature")
        
        # Step 3: Monitor progress
        while True:
            status = client.documents.get_document_status(document_id)
            
            print(f"\nStatus: {status['status']}")
            print(f"Signed: {status['completed_count']}/{status['total_signers']}")
            
            if status['status'] == 'completed':
                break
            elif status['status'] == 'cancelled':
                print("Signature request was cancelled")
                return None
                
            time.sleep(60)  # Check every minute
        
        # Step 4: Download signed document
        download = client.documents.download_document(document_id)
        print(f"\nSigned document available at: {download['url']}")
        
        # Step 5: Get audit trail
        audit = client.documents.get_audit_trail(document_id)
        print("\nAudit Trail:")
        for event in audit['events']:
            print(f"- {event['timestamp']}: {event['action']} by {event['user']}")
        
        return document_id
    ```

---

## Template Management

### Get Templates

::: rezen.documents.DocumentClient.get_document_templates
    options:
      show_source: false
      heading_level: 4

### Create from Template

::: rezen.documents.DocumentClient.create_document_from_template
    options:
      show_source: false
      heading_level: 4

!!! example "Using Templates"

    ```python
    # Get available templates
    templates = client.documents.get_document_templates(page_size=50)
    
    for template in templates['templates']:
        print(f"Template: {template['name']}")
        print(f"  Type: {template['document_type']}")
        print(f"  Fields: {len(template['fields'])}")
    
    # Create document from template
    document = client.documents.create_document_from_template(
        template_id="template-001",
        data={
            "title": "New Purchase Agreement",
            "signers": [
                {"email": "buyer@example.com", "name": "Buyer Name"},
                {"email": "seller@example.com", "name": "Seller Name"}
            ],
            "field_values": {
                "property_address": "123 Main St",
                "purchase_price": "$500,000",
                "closing_date": "2024-03-15"
            }
        }
    )
    
    print(f"Created document from template: {document['id']}")
    ```

---

## Bulk Operations

### Bulk Send

::: rezen.documents.DocumentClient.bulk_send_documents
    options:
      show_source: false
      heading_level: 4

!!! example "Bulk Document Sending"

    ```python
    # Prepare multiple documents
    documents = [
        {
            "template_id": "disclosure-template",
            "title": "Disclosure Form - Unit 101",
            "signers": [{"email": "tenant101@example.com", "name": "Tenant 101"}]
        },
        {
            "template_id": "disclosure-template",
            "title": "Disclosure Form - Unit 102",
            "signers": [{"email": "tenant102@example.com", "name": "Tenant 102"}]
        },
        {
            "template_id": "disclosure-template",
            "title": "Disclosure Form - Unit 103",
            "signers": [{"email": "tenant103@example.com", "name": "Tenant 103"}]
        }
    ]
    
    # Send all documents at once
    result = client.documents.bulk_send_documents(documents)
    
    print(f"Sent {len(result['sent'])} documents")
    print(f"Failed: {len(result['failed'])}")
    
    for doc in result['sent']:
        print(f"✓ Sent: {doc['title']} (ID: {doc['id']})")
    
    for error in result['failed']:
        print(f"✗ Failed: {error['title']} - {error['error']}")
    ```

---

## Signer Management

### Get Signer Link

::: rezen.documents.DocumentClient.get_signer_link
    options:
      show_source: false
      heading_level: 4

### Send Reminder

::: rezen.documents.DocumentClient.remind_signer
    options:
      show_source: false
      heading_level: 4

!!! example "Managing Signers"

    ```python
    # Get signing links for all signers
    document = client.documents.get_document(document_id)
    
    for signer in document['signers']:
        if signer['status'] == 'pending':
            # Get unique signing link
            link = client.documents.get_signer_link(
                document_id=document_id,
                signer_id=signer['id']
            )
            
            print(f"Signing link for {signer['name']}: {link['url']}")
            
            # Send reminder if needed
            client.documents.remind_signer(
                document_id=document_id,
                signer_id=signer['id'],
                message="Please sign at your earliest convenience"
            )
    ```

---

## Audit & Compliance

### Get Audit Trail

::: rezen.documents.DocumentClient.get_audit_trail
    options:
      show_source: false
      heading_level: 4

### Download Document

::: rezen.documents.DocumentClient.download_document
    options:
      show_source: false
      heading_level: 4

!!! example "Compliance Tracking"

    ```python
    # Get complete audit trail
    audit = client.documents.get_audit_trail(document_id)
    
    print("Document Audit Trail:")
    print(f"Document: {audit['document_title']}")
    print(f"Created: {audit['created_at']}")
    print(f"Status: {audit['status']}")
    
    print("\nEvents:")
    for event in audit['events']:
        print(f"{event['timestamp']} - {event['action']}")
        print(f"  By: {event['user_email']}")
        print(f"  IP: {event['ip_address']}")
        
    # Download for records
    if audit['status'] == 'completed':
        download = client.documents.download_document(document_id)
        print(f"\nDownload URL: {download['url']}")
        print(f"Expires: {download['expires_at']}")
    ```

---

## Error Handling

!!! warning "Common Errors"

    - **Invalid Signers**: Ensure all signer emails are valid
    - **Missing Fields**: Check required document fields
    - **Template Errors**: Verify template ID exists
    - **File Size**: Maximum file size is typically 25MB

!!! example "Error Handling"

    ```python
    from rezen.exceptions import ValidationError, NotFoundError
    
    try:
        # Attempt to send document
        document = client.documents.post_document(data=document_data, file=file)
        
    except ValidationError as e:
        print(f"Validation error: {e}")
        print(f"Invalid fields: {e.invalid_fields}")
        
    except NotFoundError as e:
        print(f"Document or template not found: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")
    ```

---

## Next Steps

<div class="grid cards" markdown>

-   [☑️ **Checklist API**](checklist.md)

    Manage transaction checklists

-   [🔄 **Transactions API**](transactions.md)

    Work with transaction documents

-   [🔧 **Transaction Builder**](transaction-builder.md)

    Create transactions with documents

</div> 