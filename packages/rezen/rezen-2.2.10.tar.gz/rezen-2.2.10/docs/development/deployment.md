# Deployment Guide

This guide covers all deployment processes for the ReZEN Python client, consolidated into GitHub Actions workflows.

## 🚀 Quick Overview

All deployments are handled automatically through GitHub Actions:

- **Code Quality**: Automatic on every push/PR
- **Testing**: Automatic on every push/PR  
- **Documentation**: Automatic on docs changes
- **Releases**: Manual trigger or tag-based

## 📋 Prerequisites

### GitHub Secrets

Ensure these secrets are configured in your repository:

```bash
# Required for all deployments
REZEN_API_KEY                 # For running tests
GITHUB_TOKEN                  # Auto-provided

# Required for PyPI publishing
PYPI_API_TOKEN               # PyPI API token
```

## 🔄 Automated Workflows

### 1. Continuous Integration (`ci.yml`)

**Triggers**: Every push/PR to `main` or `develop`

**What it does**:
- ✅ Code quality checks (Black, isort, flake8, mypy)
- 🔒 Security scanning (Bandit, Safety)
- 📝 Config validation (YAML, TOML)
- 🧪 Test suite across Python 3.8-3.12
- 📦 Package build verification

### 2. Documentation (`docs.yml`)

**Triggers**: Changes to `docs/`, `mkdocs.yml`, or code

**What it does**:
- 🔄 Auto-sync API coverage
- 📚 Build documentation with MkDocs
- 🚀 Deploy to GitHub Pages
- 💬 PR comments with build status

### 3. Release (`release.yml`)

**Triggers**: 
- Tag push (`v*`)
- Manual workflow dispatch

**What it does**:
- 🏷️ Version bumping (manual releases)
- ✅ Full test suite
- 📦 Package building  
- 🚀 PyPI publishing
- 📋 GitHub release creation
- 📝 Automatic changelog generation

## 🛠️ Manual Operations

### Creating a Release

#### Option 1: Manual Release (Recommended)

1. Go to **Actions** → **Release** → **Run workflow**
2. Enter version (e.g., `1.2.3`)
3. Optionally mark as prerelease
4. Click **Run workflow**

The workflow will:
- Validate version format
- Update `pyproject.toml` and `rezen/__init__.py`
- Create and push the git tag
- Run tests and build
- Publish to PyPI
- Create GitHub release

#### Option 2: Tag-based Release

```bash
# Update versions manually
vim pyproject.toml      # Update version = "1.2.3"
vim rezen/__init__.py   # Update __version__ = "1.2.3"

# Commit and tag
git add pyproject.toml rezen/__init__.py
git commit -m "Bump version to 1.2.3"
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin main --tags
```

### Local Development

#### Documentation

```bash
# Install dependencies
pip install -r docs/requirements.txt

# Serve locally  
mkdocs serve

# Build for testing
mkdocs build
```

#### Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest --cov=rezen

# Run quality checks
black --check .
isort --check .
flake8 .
mypy rezen/
```

## 🔧 Configuration Files

### Minimal Configuration

The following files are **no longer needed** and have been consolidated into GitHub Actions:

- ❌ `.pre-commit-config.yaml` → Integrated into CI workflow
- ❌ `scripts/bump_version.py` → Integrated into release workflow
- ❌ `scripts/sync_docs.py` → Integrated into docs workflow
- ⚠️ `.readthedocs.yml` → Optional (if using RTD alongside GitHub Pages)

### Required Files

- ✅ `.github/workflows/` → All automation
- ✅ `mkdocs.yml` → Documentation config
- ✅ `pyproject.toml` → Package config
- ✅ `requirements.txt` & `requirements-dev.txt` → Dependencies

## 🚨 Troubleshooting

### Release Issues

**Version mismatch errors**:
```bash
# Check current versions
grep version pyproject.toml
grep __version__ rezen/__init__.py

# Ensure they match your intended version
```

**PyPI publishing fails**:
- Verify `PYPI_API_TOKEN` secret is set
- Check if version already exists on PyPI
- Ensure package builds successfully

### Documentation Issues

**Build failures**:
- Check MkDocs configuration in `mkdocs.yml`
- Verify all referenced files exist
- Check for syntax errors in markdown

### CI Issues

**Code quality failures**:
```bash
# Fix formatting
black .
isort .

# Check for issues
flake8 .
mypy rezen/
```

**Test failures**:
- Ensure `REZEN_API_KEY` is set in secrets
- Check for environment-specific issues
- Verify all dependencies are installed

## 📊 Monitoring

### Workflow Status

Monitor deployments at:
- **GitHub Actions**: Repository → Actions tab
- **PyPI**: https://pypi.org/project/rezen/
- **GitHub Pages**: https://theperrygroup.github.io/rezen/

### Coverage Reports

- **Codecov**: Automatic uploads from CI
- **Security**: Bandit reports in CI artifacts
- **Dependencies**: Dependabot PRs for updates

## 🎯 Best Practices

1. **Always test locally** before pushing
2. **Use manual releases** for better control
3. **Write descriptive commit messages** for better changelogs
4. **Keep dependencies updated** via Dependabot
5. **Monitor workflow runs** for issues
6. **Use semantic versioning** (e.g., 1.2.3)

## 📞 Support

If workflows fail or you need help:

1. Check workflow logs in GitHub Actions
2. Review this guide for common issues
3. Check repository Issues for known problems
4. Create a new issue with workflow logs attached
