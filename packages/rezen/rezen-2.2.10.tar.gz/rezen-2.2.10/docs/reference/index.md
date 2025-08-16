# Reference

Technical reference materials for the ReZEN Python API client, including data types, error handling, and version history.

---

## 📚 Reference Materials

<div class="grid cards" markdown>

-   📝 **Data Types & Enums**

    ---

    Complete reference for all data types, enums, and constants used in the API

    [:octicons-arrow-right-24: Data Types Reference](data-types.md)

-   ⚠️ **Exception Reference**

    ---

    Comprehensive error handling guide with all exception types and patterns

    [:octicons-arrow-right-24: Exception Guide](exceptions.md)

-   🏷️ **Version History**

    ---

    Release notes, changelog, and version compatibility information

    [:octicons-arrow-right-24: Changelog](changelog.md)

</div>

---

## 🎯 Quick Lookup

### **Data Types**
Essential type information for development:

- **[Enums](data-types.md#enums)** - All enumerated values (status types, sort directions, etc.)
- **[Type Hints](data-types.md#usage-patterns)** - Python type annotations and validation
- **[Constants](data-types.md#complete-enum-reference)** - API constants and field values

### **Error Handling**
Everything you need for robust error management:

- **[Exception Types](exceptions.md#core-exception-types)** - All available exception classes
- **[Error Codes](exceptions.md#common-error-codes)** - HTTP status codes and meanings
- **[Handling Patterns](exceptions.md#error-handling-patterns)** - Best practices for error handling

### **Version Information**
Track changes and compatibility:

- **[Latest Release](changelog.md)** - Most recent version information
- **[Breaking Changes](changelog.md)** - Important migration notes
- **[Version Compatibility](changelog.md)** - Python version support

---

## 🔍 Common Reference Tasks

### **Type Safety Development**
Building type-safe applications:

```python
from typing import List, Optional
from rezen.enums import TeamStatus, SortDirection

def get_teams(
    status: TeamStatus = TeamStatus.ACTIVE,
    limit: Optional[int] = None
) -> List[dict]:
    """Type-safe team retrieval."""
    # Implementation with full type safety
```

### **Error Handling Setup**
Implementing comprehensive error handling:

```python
from rezen.exceptions import (
    RezenError,
    AuthenticationError,
    NotFoundError
)

try:
    # API operations
    pass
except AuthenticationError:
    # Handle auth issues
    pass
except NotFoundError:
    # Handle missing resources
    pass
except RezenError as e:
    # Handle general API errors
    pass
```

### **Enum Usage**
Working with API enums:

```python
from rezen.enums import TeamStatus, SortDirection

# Type-safe API calls
teams = client.teams.search_teams(
    status=TeamStatus.ACTIVE,
    sort_direction=SortDirection.DESC
)
```

---

## 📖 Detailed References

### **🔤 Data Types & Enums** → [Complete Guide](data-types.md)
- All enumerated values used in the API
- Type hints and validation patterns
- Migration guides for type safety
- Complete enum reference tables

### **⚠️ Exception Reference** → [Error Handling Guide](exceptions.md)
- Exception hierarchy and inheritance
- Specific error types and when they occur
- Production-ready error handling patterns
- Debugging and troubleshooting tools

### **📋 Version History** → [Changelog](changelog.md)
- Release notes for all versions
- Breaking changes and migration guides
- Feature additions and improvements
- Bug fixes and security updates

---

## 🛠️ Developer Tools

### **Type Checking**
Use these imports for static type checking:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rezen import RezenClient
    from rezen.enums import TeamStatus
```

### **Runtime Validation**
Validate data at runtime:

```python
from rezen.enums import TeamStatus

def validate_status(status: str) -> bool:
    try:
        TeamStatus(status)
        return True
    except ValueError:
        return False
```

### **IDE Configuration**
Enable full IDE support by installing type stubs:

```bash
pip install types-requests
```

---

## 🔗 Related Documentation

- **[API Methods](../api/index.md)** - Complete API method reference
- **[Getting Started](../getting-started/index.md)** - Setup and authentication
- **[Guides & Examples](../guides/index.md)** - Practical usage examples
- **[Development](../development/index.md)** - Contributing and development setup

---

## 💡 Quick Tips

!!! tip "Development Best Practices"

    - Always use enums instead of string literals for API parameters
    - Implement comprehensive error handling for production applications
    - Keep up with the changelog for breaking changes
    - Use type hints for better IDE support and code quality
