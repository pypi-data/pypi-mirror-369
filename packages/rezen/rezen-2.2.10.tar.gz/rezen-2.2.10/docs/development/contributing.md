# Contributing Guide

Thank you for your interest in contributing to the ReZEN Python API client! This guide will help you get started with contributing code, documentation, and improvements.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Release Process](#release-process)

---

## Getting Started

### Prerequisites

- **Python**: 3.7 or higher
- **Git**: For version control
- **GitHub account**: For submitting contributions
- **ReZEN API key**: For testing (contact support if needed)

### Ways to Contribute

- 🐛 **Bug fixes** - Fix issues found in the codebase
- 🚀 **New features** - Add new API endpoints or functionality
- 📖 **Documentation** - Improve docs, examples, or guides
- 🧪 **Tests** - Add test coverage or improve existing tests
- 🔧 **Performance** - Optimize code for better performance
- 💡 **Examples** - Create real-world usage examples

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/rezen-python-client.git
cd rezen-python-client

# Add upstream remote
git remote add upstream https://github.com/original-org/rezen-python-client.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .
```

### 3. Verify Setup

```bash
# Run tests to ensure everything works
pytest

# Check code formatting
black --check rezen tests
isort --check-only rezen tests

# Run type checking
mypy rezen

# Check test coverage
pytest --cov=rezen --cov-report=html
```

### 4. Set Up Pre-commit Hooks (Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## Code Standards

### Python Style

We follow [PEP 8](https://pep8.org/) with some specific guidelines:

```python
# ✅ Good: Clear function names with type hints
def get_agent_by_email(email_address: str) -> Dict[str, Any]:
    """Get agent information by email address.

    Args:
        email_address: The agent's email address

    Returns:
        Agent data dictionary

    Raises:
        NotFoundError: If agent is not found
        ValidationError: If email format is invalid
    """
    if '@' not in email_address:
        raise ValidationError(f"Invalid email format: {email_address}")

    return self.get("agents", params={"email": email_address})

# ❌ Bad: No type hints, unclear naming
def get_agent(email):
    return self.get("agents", params={"email": email})
```

### Code Formatting

We use automated tools for consistent formatting:

```bash
# Format code with Black
black rezen tests

# Sort imports with isort
isort rezen tests

# Check with flake8
flake8 rezen tests
```

### Type Hints

All public methods must have complete type hints:

```python
from typing import Dict, List, Optional, Any, Union

# ✅ Complete type hints
def search_teams(
    self,
    status: Optional[Union[TeamStatus, str]] = None,
    page_size: Optional[int] = None
) -> Dict[str, Any]:
    pass

# ❌ Missing type hints
def search_teams(self, status=None, page_size=None):
    pass
```

### Docstrings

Use Google-style docstrings for all public methods:

```python
def create_transaction_builder(self, builder_type: str = "TRANSACTION") -> Dict[str, Any]:
    """Create a new transaction builder.

    Creates a new transaction builder instance that can be used to construct
    real estate transactions with participants, property details, and financial information.

    Args:
        builder_type: Type of builder to create. Must be "TRANSACTION" or "LISTING".
                     Defaults to "TRANSACTION".

    Returns:
        Dictionary containing the created transaction builder data with at least:
        - id: Unique identifier for the transaction builder
        - type: The builder type that was created
        - status: Current status of the builder

    Raises:
        ValidationError: If builder_type is not valid
        AuthenticationError: If API key is invalid
        ServerError: If the API server encounters an error

    Example:
        Create a basic transaction builder:

        >>> client = RezenClient()
        >>> response = client.transaction_builder.create_transaction_builder()
        >>> transaction_id = response['id']

        Create a listing builder:

        >>> response = client.transaction_builder.create_transaction_builder("LISTING")
    """
```

### Error Handling

Use specific exceptions and provide helpful error messages:

```python
from .exceptions import ValidationError, NotFoundError

def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
    """Get transaction details."""
    if not transaction_id:
        raise ValidationError("Transaction ID cannot be empty")

    if not isinstance(transaction_id, str):
        raise ValidationError(f"Transaction ID must be string, got {type(transaction_id)}")

    try:
        return self.get(f"transactions/{transaction_id}")
    except NotFoundError:
        raise NotFoundError(
            f"Transaction '{transaction_id}' not found. "
            f"Verify the ID is correct and the transaction exists."
        )
```

---

## Testing Guidelines

### Test Structure

We use pytest with a specific structure:

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_client.py             # Main client tests
├── test_transaction_builder.py # Transaction builder tests
├── test_transactions.py       # Transactions API tests
├── test_teams.py              # Teams API tests
├── test_agents.py             # Agents API tests
├── test_exceptions.py         # Exception handling tests
└── test_integration.py        # Integration tests
```

### Writing Tests

#### Unit Tests

```python
import pytest
from unittest.mock import Mock, patch
from rezen import RezenClient
from rezen.exceptions import ValidationError, NotFoundError

class TestTransactionBuilder:

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.client = RezenClient(api_key="test_key")

    @patch('rezen.transaction_builder.TransactionBuilderClient._request')
    def test_create_transaction_builder_success(self, mock_request):
        """Test successful transaction builder creation."""
        # Arrange
        expected_response = {"id": "tx-12345", "type": "TRANSACTION"}
        mock_request.return_value = expected_response

        # Act
        result = self.client.transaction_builder.create_transaction_builder()

        # Assert
        assert result == expected_response
        mock_request.assert_called_once_with(
            "POST", "transaction-builder",
            params={"type": "TRANSACTION"}
        )

    def test_create_transaction_builder_invalid_type(self):
        """Test transaction builder creation with invalid type."""
        with pytest.raises(ValidationError, match="Invalid builder type"):
            self.client.transaction_builder.create_transaction_builder("INVALID")

    @pytest.mark.parametrize("builder_type,expected_params", [
        ("TRANSACTION", {"type": "TRANSACTION"}),
        ("LISTING", {"type": "LISTING"}),
    ])
    def test_create_transaction_builder_types(self, builder_type, expected_params):
        """Test transaction builder creation with different types."""
        with patch.object(self.client.transaction_builder, '_request') as mock_request:
            mock_request.return_value = {"id": "test"}

            self.client.transaction_builder.create_transaction_builder(builder_type)

            mock_request.assert_called_once_with(
                "POST", "transaction-builder", params=expected_params
            )
```

#### Integration Tests

```python
import pytest
from rezen import RezenClient

class TestIntegration:
    """Integration tests that hit real API endpoints."""

    @pytest.mark.integration
    def test_teams_search_integration(self):
        """Test actual teams search API call."""
        client = RezenClient()  # Uses real API key from environment

        teams = client.teams.search_teams(status="ACTIVE", page_size=5)

        assert isinstance(teams, list)
        assert len(teams) <= 5

        if teams:
            team = teams[0]
            assert 'id' in team
            assert 'name' in team
            assert team.get('status') == 'ACTIVE'
```

### Test Configuration

Add to `conftest.py`:

```python
import pytest
import os

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )

@pytest.fixture
def mock_api_key():
    """Provide a test API key."""
    return "test_api_key_12345"

@pytest.fixture
def sample_transaction_data():
    """Provide sample transaction data for tests."""
    return {
        "type": "PURCHASE",
        "property": {
            "address": "123 Test St",
            "city": "Test City",
            "state": "CA",
            "zipCode": "90210"
        },
        "purchase_price": 500000
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_teams.py

# Run tests with coverage
pytest --cov=rezen --cov-report=html

# Run only unit tests (skip integration)
pytest -m "not integration"

# Run only integration tests
pytest -m integration

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

### Test Coverage Requirements

- **Minimum coverage**: 95% overall
- **New code**: 100% coverage required
- **Critical paths**: Authentication, API calls, error handling must have 100% coverage

Check coverage:

```bash
# Generate coverage report
pytest --cov=rezen --cov-report=html
open htmlcov/index.html  # View in browser

# Check coverage for specific module
pytest --cov=rezen.teams --cov-report=term-missing
```

---

## Documentation

### Code Documentation

All public methods require docstrings:

```python
def search_active_agents(
    self,
    page_number: Optional[int] = None,
    page_size: Optional[int] = None,
    name: Optional[str] = None
) -> Dict[str, Any]:
    """Search for active agents with filtering options.

    Searches the agent database for active agents matching the specified
    criteria. Results are paginated and can be filtered by various attributes.

    Args:
        page_number: Page number for pagination (0-based). Defaults to 0.
        page_size: Number of results per page (1-200). Defaults to 20.
        name: Filter agents by name (partial match, case-insensitive).
              Searches both first and last names.

    Returns:
        Dictionary containing:
        - content: List of agent dictionaries
        - page: Current page information
        - total: Total number of matching agents

    Raises:
        ValidationError: If page_size is outside valid range (1-200)
        AuthenticationError: If API key is invalid or missing
        RateLimitError: If too many requests made in short time

    Example:
        Search for agents named "John":

        >>> client = RezenClient()
        >>> agents = client.agents.search_active_agents(name="John", page_size=10)
        >>> print(f"Found {len(agents['content'])} agents")

        Paginate through all agents:

        >>> page = 0
        >>> all_agents = []
        >>> while True:
        ...     result = client.agents.search_active_agents(page_number=page)
        ...     if not result['content']:
        ...         break
        ...     all_agents.extend(result['content'])
        ...     page += 1
    """
```

### User Documentation

When adding new features, update relevant documentation:

1. **API Reference** (`docs/api/index.md`)
2. **Examples** (`docs/guides/examples.md`)
3. **README** (if major feature)
4. **Changelog** (`docs/changelog.md`)

### Documentation Style

- Use clear, concise language
- Include working code examples
- Add parameter descriptions and return value info
- Note any breaking changes
- Use emoji for visual organization (sparingly)

---

## Pull Request Process

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/add-agent-search
# or
git checkout -b fix/transaction-validation-error
```

### 2. Make Changes

- Write code following our standards
- Add/update tests for all changes
- Update documentation if needed
- Ensure all tests pass locally

### 3. Commit Changes

Use conventional commit messages:

```bash
# Feature additions
git commit -m "feat: add agent search by location endpoint"

# Bug fixes
git commit -m "fix: handle empty response in transaction search"

# Documentation
git commit -m "docs: add examples for team management"

# Tests
git commit -m "test: add coverage for error handling paths"

# Refactoring
git commit -m "refactor: simplify exception handling logic"
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/add-agent-search

# Create pull request on GitHub
# Use the PR template provided
```

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing performed
- [ ] Integration tests updated if needed

## Documentation
- [ ] Code documentation updated (docstrings)
- [ ] User documentation updated
- [ ] Examples updated/added
- [ ] Changelog updated

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Breaking changes documented
- [ ] Tests provide adequate coverage
```

### Review Process

1. **Automated checks**: CI/CD runs tests, linting, type checking
2. **Code review**: Maintainers review code for quality and standards
3. **Testing**: Verify functionality works as expected
4. **Documentation**: Ensure docs are complete and accurate
5. **Approval**: At least one maintainer approval required
6. **Merge**: Squash and merge to main branch

---

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Create client with '...'
2. Call method '....'
3. Pass parameters '....'
4. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.9.0]
- ReZEN client version: [e.g. 1.0.7]

**Code Sample**
```python
# Minimal code sample that reproduces the issue
client = RezenClient()
# ... rest of code
```

**Error Output**
```
Full error traceback here
```

**Additional Context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear description of the feature you'd like to see.

**Use Case**
Explain why this feature would be useful.

**Proposed Solution**
How you think this should work.

**Alternative Solutions**
Any alternative approaches you've considered.

**Additional Context**
Any other context or screenshots about the feature request.
```

---

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0 → 2.0.0): Breaking changes
- **MINOR** (1.0.0 → 1.1.0): New features, backwards compatible
- **PATCH** (1.0.0 → 1.0.1): Bug fixes, backwards compatible

### Release Checklist

1. **Update version numbers**:
   ```bash
   # Update version in pyproject.toml and __init__.py
   python scripts/bump_version.py 1.2.0
   ```

2. **Update changelog**:
   ```markdown
   ## [1.2.0] - 2024-01-15

   ### Added
   - New agent search by location endpoint
   - Support for team member management

   ### Fixed
   - Transaction validation error handling
   - Memory leak in batch operations

   ### Changed
   - Improved error messages for authentication failures
   ```

3. **Run full test suite**:
   ```bash
   pytest --cov=rezen --cov-report=html
   mypy rezen
   black --check rezen tests
   ```

4. **Build and test package**:
   ```bash
   python -m build
   pip install dist/rezen-1.2.0.tar.gz
   # Test installation works
   ```

5. **Create release PR**:
   - Include version bump and changelog
   - Get approval from maintainers

6. **Tag and release**:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   # GitHub Actions handles PyPI publishing
   ```

---

## Getting Help

### Development Questions

- **GitHub Discussions**: For general questions about contributing
- **Discord/Slack**: For real-time development chat (if available)
- **Email**: support@rezen.com for private questions

### Resources

- **Style Guide**: Follow PEP 8 and project conventions above
- **API Documentation**: [docs/api/index.md](../api/index.md)
- **Examples**: [docs/guides/examples.md](../guides/examples.md)
- **Python Docs**: [docs.python.org](https://docs.python.org/)

---

## Recognition

Contributors will be:

- Listed in the project contributors
- Mentioned in release notes for significant contributions
- Invited to the contributors' Discord/Slack channel (if available)

---

**Thank you for contributing to the ReZEN Python client!** 🎉

Your contributions help make real estate technology more accessible to developers worldwide.
