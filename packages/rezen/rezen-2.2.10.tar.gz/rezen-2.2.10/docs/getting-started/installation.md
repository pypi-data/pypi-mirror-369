# Installation Guide

This guide covers installation and setup of the ReZEN Python API client.

## 📋 Requirements

- **Python**: 3.7 or higher
- **Operating Systems**: Windows, macOS, Linux
- **Internet connection** for package installation and API access

## 🚀 Quick Installation

### From PyPI (Recommended)

```bash
pip install rezen
```

### From Source

```bash
git clone https://github.com/theperrygroup/rezen.git
cd rezen
pip install .
```

### Development Installation

```bash
git clone https://github.com/theperrygroup/rezen.git
cd rezen
pip install -e .
```

## 🔧 Environment Setup

### 1. API Key Configuration

You'll need a ReZEN API key. Get one from the ReZEN platform dashboard.

#### Option A: Environment Variable (Recommended)

**Linux/macOS:**
```bash
export REZEN_API_KEY="your_api_key_here"
```

**Windows Command Prompt:**
```cmd
set REZEN_API_KEY=your_api_key_here
```

**Windows PowerShell:**
```powershell
$env:REZEN_API_KEY="your_api_key_here"
```

#### Option B: `.env` File

Create a `.env` file in your project root:

```bash
REZEN_API_KEY=your_api_key_here
```

Then load it in your Python code:

```python
from dotenv import load_dotenv
load_dotenv()

from rezen import RezenClient
client = RezenClient()  # Will automatically use the API key from .env
```

#### Option C: Direct Initialization

```python
from rezen import RezenClient

client = RezenClient(api_key="your_api_key_here")
```

### 2. Virtual Environment Setup (Recommended)

Create an isolated environment for your project:

```bash
# Create virtual environment
python -m venv rezen-env

# Activate (Linux/macOS)
source rezen-env/bin/activate

# Activate (Windows)
rezen-env\Scripts\activate

# Install rezen
pip install rezen
```

## 📦 Dependencies

The ReZEN client automatically installs these dependencies:

- **requests** - HTTP client for API calls
- **typing-extensions** - Enhanced type hints (Python < 3.8)

### Optional Dependencies

For development and testing:

```bash
pip install rezen[dev]
```

This includes:
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **isort** - Import sorting
- **mypy** - Type checking
- **python-dotenv** - Environment variable loading

## ✅ Verify Installation

Test your installation with this simple script:

```python
from rezen import RezenClient

# Initialize client
client = RezenClient()

# Test connection (this will validate your API key)
try:
    # Simple API call to verify connection
    teams = client.teams.search_teams(limit=1)
    print("✅ Installation successful!")
    print(f"Connected to ReZEN API")
except Exception as e:
    print(f"❌ Installation issue: {e}")
    print("Check your API key and internet connection")
```

## 🐛 Troubleshooting

### Common Installation Issues

#### 1. Permission Errors
```bash
# Use --user flag
pip install --user rezen

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install rezen
```

#### 2. Python Version Issues
```bash
# Check Python version
python --version

# Use specific Python version
python3.8 -m pip install rezen
```

#### 3. Network/Proxy Issues
```bash
# Behind corporate firewall
pip install --trusted-host pypi.org --trusted-host pypi.python.org rezen

# Using proxy
pip install --proxy http://proxy.company.com:8080 rezen
```

#### 4. SSL Certificate Issues
```bash
# Disable SSL verification (not recommended for production)
pip install --trusted-host pypi.org rezen
```

### API Key Issues

#### Invalid API Key Error
```python
from rezen.exceptions import AuthenticationError

try:
    client = RezenClient(api_key="invalid_key")
    teams = client.teams.search_teams()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key")
```

#### Environment Variable Not Found
```python
import os

# Check if API key is set
api_key = os.getenv('REZEN_API_KEY')
if not api_key:
    print("❌ REZEN_API_KEY environment variable not set")
    print("Set it with: export REZEN_API_KEY='your_key_here'")
else:
    print(f"✅ API key found: {api_key[:10]}...")
```

## 🔧 Advanced Configuration

### Custom Base URLs

For enterprise or testing environments:

```python
from rezen import RezenClient

# Custom API base URL
client = RezenClient(
    api_key="your_key",
    base_url="https://api-staging.rezen.com"
)
```

### Timeout Configuration

Configure request timeouts for your environment:

```python
from rezen.base_client import BaseClient

# Configure global timeout (affects all clients)
BaseClient.DEFAULT_TIMEOUT = 30  # 30 seconds
```

### Request Debugging

Enable request/response logging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Your ReZEN client calls will now show detailed request/response info
from rezen import RezenClient
client = RezenClient()
```

## 🔄 Upgrading

### Check Current Version

```python
import rezen
print(f"Current version: {rezen.__version__}")
```

### Upgrade to Latest

```bash
pip install --upgrade rezen
```

### Specific Version

```bash
pip install rezen==1.0.7
```

## 📋 Next Steps

After successful installation:

1. **[Quick Start Guide](quickstart.md)** - Your first API calls
2. **[API Reference](../api/index.md)** - Complete endpoint documentation
3. **[Examples](../guides/examples.md)** - Real-world usage patterns
4. **[Error Handling](../guides/troubleshooting.md)** - Handle edge cases

## 💡 Tips

### Production Deployments

1. **Pin versions** in requirements.txt:
   ```
   rezen==1.0.7
   ```

2. **Use environment variables** for API keys (never commit keys to source control)

3. **Set up monitoring** for API rate limits and errors

4. **Consider caching** for frequently accessed data

### Development Best Practices

1. **Use virtual environments** to isolate dependencies
2. **Add `.env` to `.gitignore** to avoid committing secrets
3. **Use type hints** for better IDE support
4. **Write tests** for your integration code

---

**🎉 Ready to start building with ReZEN!** Continue to the [Quick Start Guide](quickstart.md) for your first API calls.
