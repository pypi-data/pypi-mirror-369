# Development Guide

This guide covers setting up the development environment, code quality standards, and contribution workflow for the ReZEN Python client.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (recommended: Python 3.12)
- pip or poetry for dependency management
- Git

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/theperrygroup/rezen.git
   cd rezen
   ```

2. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks** (recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

5. **Set up environment variables**:
   ```bash
   echo "REZEN_API_KEY=your_api_key_here" > .env
   ```

## 🔧 Code Quality Standards

### Formatting and Linting

This project enforces strict code quality standards:

- **Black**: Code formatting (line length: 88)
- **isort**: Import sorting (compatible with Black)
- **flake8**: Linting and style checking
- **mypy**: Static type checking
- **pytest**: Testing framework

### Running Quality Checks

```bash
# Format code
black rezen tests
isort rezen tests

# Lint code
flake8 rezen tests

# Type checking
mypy rezen

# Run tests with coverage
pytest --cov=rezen --cov-report=html
```

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually on all files
pre-commit run --all-files
```

## 📝 Documentation Standards

### Docstring Requirements

All public functions, methods, and classes must have Google-style docstrings:

```python
def search_active_agents(
    self,
    page_number: int = 0,
    page_size: int = 50,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for active agents with filtering options.

    Args:
        page_number: Zero-based page number for pagination
        page_size: Number of results per page (max 100)
        name: Filter by agent name (partial match)

    Returns:
        Dictionary containing search results and pagination info

    Raises:
        ValidationError: If parameters are invalid
        AuthenticationError: If API key is invalid

    Example:
        >>> client = AgentsClient(api_key="your_key")
        >>> results = client.search_active_agents(
        ...     page_size=10,
        ...     name="Smith"
        ... )
        >>> print(f"Found {results['totalCount']} agents")
    """
```

### Type Hints

- All function parameters must have type hints
- All return values must have type hints
- Use `Optional[T]` for nullable parameters
- Use `Union[T, U]` sparingly; prefer overloads
- Import types from `typing` module as needed

### Documentation Updates

When making code changes, always update:

1. **Function docstrings** - Keep examples current
2. **API reference** - Update `docs/api/index.md`
3. **Examples** - Update `docs/guides/examples.md`
4. **Changelog** - Add entry to `docs/changelog.md`

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── test_agents.py          # Agent API tests
├── test_client.py          # Main client tests
├── test_directory.py       # Directory API tests
├── test_exceptions.py      # Exception handling tests
├── test_teams.py          # Teams API tests
└── test_transactions.py   # Transaction API tests
```

### Test Requirements

- **100% test coverage** for all new code
- **Descriptive test names** explaining what is tested
- **Mock external API calls** using `responses` library
- **Test error conditions** not just happy paths

### Writing Tests

```python
@responses.activate
def test_search_agents_with_filters(self, client: AgentsClient) -> None:
    """Test agent search with multiple filter parameters."""
    # Arrange
    mock_response = {
        "agents": [{"id": "agent-123", "name": "John Smith"}],
        "totalCount": 1
    }
    responses.add(
        responses.GET,
        "https://yenta.therealbrokerage.com/api/v1/agents/search/active",
        json=mock_response,
        status=200,
    )

    # Act
    result = client.search_active_agents(
        name="Smith",
        page_size=10
    )

    # Assert
    assert result == mock_response
    assert len(responses.calls) == 1

    # Verify request parameters
    request_url = responses.calls[0].request.url
    assert "name=Smith" in request_url
    assert "pageSize=10" in request_url
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=rezen --cov-report=html

# Run tests in parallel
pytest -n auto

# Run tests with verbose output
pytest -v
```

## 🔄 Development Workflow

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/feature-name` - Individual features
- `bugfix/issue-description` - Bug fixes
- `hotfix/critical-fix` - Emergency fixes

### Contribution Process

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-endpoint
   ```

2. **Make changes** following code quality standards

3. **Run quality checks**:
   ```bash
   pre-commit run --all-files
   pytest --cov=rezen
   ```

4. **Update documentation** as needed

5. **Commit with descriptive message**:
   ```bash
   git commit -m "feat: add search_transactions endpoint

   - Add new endpoint for transaction search
   - Include pagination and filtering options
   - Add comprehensive tests with 100% coverage
   - Update API reference documentation"
   ```

6. **Push and create pull request**:
   ```bash
   git push origin feature/new-endpoint
   ```

### Commit Message Format

Follow conventional commits:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation updates
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/updates
- `chore:` - Maintenance tasks

## 🐛 Debugging

### Common Issues

1. **Import errors**: Ensure you're in the virtual environment
2. **API errors**: Check your API key in `.env`
3. **Test failures**: Run `pytest -v` for detailed output
4. **Type errors**: Run `mypy rezen` to identify issues

### Debugging Tools

```bash
# Debug specific test
pytest tests/test_agents.py::TestAgentsClient::test_search_agents -v -s

# Debug with pdb
pytest --pdb tests/test_agents.py

# Generate coverage report
pytest --cov=rezen --cov-report=html
open htmlcov/index.html
```

## 📦 Release Process

### Version Management

1. Update version in `rezen/__init__.py`
2. Update version in `pyproject.toml`
3. Update `docs/changelog.md`
4. Create git tag: `git tag v1.2.0`

### Publishing

```bash
# Build package
python -m build

# Upload to PyPI (maintainers only)
twine upload dist/*
```

## 🔗 Resources

- [ReZEN API Documentation](https://api-docs.rezen.com)
- [Python Type Hints Guide](https://docs.python.org/3/library/typing.html)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [pytest Documentation](https://docs.pytest.org/)

## 🆘 Getting Help

- **Documentation**: Check the full documentation site
- **Issues**: Open a GitHub issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general questions
- **Email**: Contact the maintainers at dev@theperrygroup.com
