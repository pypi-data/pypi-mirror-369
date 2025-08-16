# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.6] - 2025-01-29

### 🎯 Critical Fix
- **RESOLVED: June 2024 Listing Posting Issue** - Fixed location update validation that was causing "Bad request: Invalid request" errors when posting listings
- **Location Updates Now Work Correctly** - Added comprehensive validation and documentation for the 3 required additional fields:
  - `county` (string) - REQUIRED beyond basic address fields
  - `yearBuilt` (integer) - REQUIRED beyond basic address fields  
  - `mlsNumber` (string) - REQUIRED beyond basic address fields

### ✨ Enhanced
- **Comprehensive Field Validation** - Added helpful error messages for common field naming mistakes:
  - Use `street` not `address`
  - Use `zip` not `zipCode` or `zip_code`
  - State codes must be ALL CAPS (e.g., `UTAH`, `CALIFORNIA`)
  - Use camelCase: `yearBuilt`, `mlsNumber`, `escrowNumber`
- **Improved Documentation** - Updated all location-related examples and documentation to include required fields
- **Better Error Messages** - Validation errors now provide clear guidance on fixing field name and format issues
- **End-to-End Testing** - Added comprehensive tests covering location validation scenarios and complete listing workflows

### 🔧 Technical Details
- **Breaking Change Context**: This resolves the breaking change introduced when migrating from Tapioca-based API client to official rezen library in June 2024
- **Backward Compatibility**: All existing method names (`put_location_to_draft`, etc.) continue to work as aliases
- **API Requirements**: The ReZEN API began enforcing stricter validation requirements that were not well-documented in version 1.7.1
- **Current Support**: All validation and requirements are fully supported in version 2.2.6+

### 📋 Migration Guide
For users affected by the June 2024 listing posting issue:

**Before (Failing):**
```python
location_data = {
    "address": "123 Main Street",  # Wrong field name
    "city": "Salt Lake City",
    "state": "utah",               # Wrong case
    "zipCode": "84101"            # Wrong field name
}
```

**After (Working):**
```python
location_data = {
    "street": "123 Main Street",   # Correct field name
    "city": "Salt Lake City", 
    "state": "UTAH",              # ALL CAPS required
    "zip": "84101",               # Correct field name
    "county": "Salt Lake",        # REQUIRED - was missing
    "yearBuilt": 2020,           # REQUIRED - was missing
    "mlsNumber": "MLS123456"     # REQUIRED - was missing
}
```

## [2.2.5] - 2024-01-XX

### Fixed
- Fix dealType field value issue

## [2.2.4] - 2024-01-XX

### Fixed
- Commission payer documentation and tests

## [2.2.3] - 2024-01-XX

### Fixed
- Fix add_participant multipart/form-data bug

## [2.2.2] - 2024-01-XX

### Fixed
- Improve emoji rendering in documentation

## [2.2.1] - 2024-01-XX

### Fixed
- Simplify mkdocs emoji configuration to prevent YAML parsing errors

## [2.1.0] - 2024-01-XX

### Added
- Consolidate workflows into unified deployment
- Merge release and docs workflows

## [2.0.1] - 2024-01-XX

### Fixed
- Code formatting, linting, and version bump
- Applied Black formatting to all Python files
- Applied isort to sort imports
- Passed mypy type checking
- Rebuilt documentation with mkdocs

## [2.0.0] - 2024-01-XX

### Added
- Major version release
- Significant API improvements and stabilization

## [1.7.1] - 2024-06-XX

### Note
- This version introduced stricter location validation requirements that caused listing posting failures
- Issues resolved in version 2.2.6+

---

**Legend:**
- 🎯 Critical fixes and major improvements
- ✨ New features and enhancements  
- 🔧 Technical changes and improvements
- 📋 Migration guides and breaking changes
- 🐛 Bug fixes
