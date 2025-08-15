# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Code Quality & Testing

```bash
# Format code
just prettify
# or: uv run ruff format src

# Lint with auto-fix
just lintify-fix
# or: uv run ruff check --fix src

# Type checking
just type-check
# or: uv run pyright src

# Run tests
just test
# or: uv run pytest src -vv

# Run tests with coverage
just test-cov
# or: uv run pytest src --cov=src --cov-report=term-missing

# Complete validation workflow
just validate
# or: uv run ruff check --fix src && uv run ruff format src && uv run pyright src && uv run pytest src -vv
```

### Package Management

```bash
# Install dependencies
uv sync

# For library development
uv sync --all-groups

# Build wheel package
uv build --wheel

# Publish to PyPI
uv publish --token $PYPI_TOKEN

# Clean cache files
just clean
```

### Version Management

**Single Source of Truth**: `src/fetchpoint/__init__.py` contains the authoritative version via `__version__ = "x.y.z"`

- `pyproject.toml` uses dynamic versioning to read from `__init__.py` automatically
- No hardcoded versions elsewhere (README.md does not include version)
- Hatchling build backend handles version extraction during build

**To Update Version:**

1. Edit `__version__` in `src/fetchpoint/__init__.py`
2. Follow semantic versioning: MAJOR.MINOR.PATCH
3. Build and publish: `uv build --wheel && uv publish --token $PYPI_TOKEN`

**Configuration:**

```toml
[project]
dynamic = ["version"]

[tool.hatch.version]
path = "src/fetchpoint/__init__.py"
```

## Architecture Overview

**FetchPoint** is a SharePoint Online integration library focused on read-only operations with federated authentication support.

### Core Module Structure (`src/fetchpoint/`)

- **`client.py`** - Main `SharePointClient` class with context manager support and `PathResolver` for hierarchical path validation
  - **Main Class**: `SharePointClient` - Context manager for SharePoint connections
  - **Helper Class**: `PathResolver` - Validates and resolves SharePoint paths
  - **Key Features**: Stateless design, path validation with hierarchical error reporting, file listing and download capabilities, library structure discovery
- **`authenticator.py`** - Federated authentication handler for Azure AD and enterprise identity providers
  - Key function: `create_authenticated_context(config: SharePointAuthConfig) -> ClientContext`
  - Maps authentication errors to specific exception types
  - **Features**: Handles Azure AD and enterprise federated authentication flows, provides secure username masking for logging, validates connection by loading web properties
- **`config.py`** - Configuration management with explicit parameter support (no environment dependencies by default)
  - `create_sharepoint_config()` - Creates auth config with explicit parameters
  - `create_config_from_dict()` - Creates config from dictionary
  - `load_sharepoint_config()` - Deprecated environment-based config
- **`models.py`** - Pydantic v2 models: `SharePointAuthConfig`, `FileInfo`, `FileType` enum
- **`file_handler.py`** - File listing and metadata extraction functions
  - `list_files_in_library()` - Lists files with metadata
  - `list_folders_in_library()` - Lists folders in a library
  - `list_excel_files_by_path_segments()` - Folder-by-folder navigation
  - `create_file_info()` - Creates FileInfo from SharePoint file object
- **`exceptions.py`** - Custom exception hierarchy inheriting from `SharePointError`
  - **Base Exception**: `SharePointError`
  - **Specific Exceptions**: `AuthenticationError` (general auth failures), `FederatedAuthError` (federated auth specific issues), `FileNotFoundError` (file not found in SharePoint), `FileDownloadError` (download failures), `FileSizeLimitError` (file exceeds size limit), `ConfigurationError` (invalid configuration), `ConnectionError` (connection failures), `PermissionError` (access denied), `LibraryNotFoundError` (library not found), `InvalidFileTypeError` (unsupported file type)
- **`url_utils.py`** - URL parsing and validation utilities

### Key Dependencies

- `office365-rest-python-client>=2.6.2` - SharePoint API client
- `pydantic>=2.11.7` - Data validation
- `click>=8.2.1` - CLI framework
- `python-dotenv>=1.1.1` - Environment variable loading (optional)
- `openpyxl>=3.1.5` - Excel file processing

### Design Principles

1. **Stateless Design** - Client uses context managers for clean resource management
2. **Explicit Configuration** - No environment variable dependencies by default
3. **Hierarchical Error Reporting** - Path validation shows exactly which folder is missing
4. **Excel Focus** - Optimized for `.xlsx`, `.xls`, `.xlsm`, `.xlsb` files
5. **Security First** - Passwords as `SecretStr`, username masking, read-only operations

### Configuration Usage

```python
from fetchpoint import SharePointClient, create_sharepoint_config

# Method 1: Using configuration factory
config = create_sharepoint_config(
    username="user@company.com",
    password="your_password",
    sharepoint_url="https://company.sharepoint.com/sites/yoursite",
    timeout_seconds=30,  # optional, default: 30
    max_file_size_mb=100  # optional, default: 100
)

# Method 2: Using dictionary configuration
client = SharePointClient.from_dict({
    "username": "user@company.com",
    "password": "your_password",
    "sharepoint_url": "https://company.sharepoint.com/sites/yoursite"
})

# Context manager usage (recommended)
with SharePointClient(config) as client:
    files = client.list_excel_files("Documents", "General/Reports")
    results = client.download_files("Documents", "General/Reports", files, "./downloads")
```

### Advanced Usage Examples

```python
# Path validation
with SharePointClient(config) as client:
    # Validate configured paths
    validation_results = client.validate_paths("Documents")

    # Discover library structure
    structure = client.discover_structure("Documents", max_depth=3)

    # Get detailed file information
    file_info = client.get_file_details(
        library_name="Documents",
        folder_path="General/Reports",
        filename="important_report.xlsx"
    )

# List files with complete metadata
with SharePointClient(config) as client:
    files = client.list_files(
        library="Documents",
        path=["General", "Reports"]
    )

    # Download files with per-file error handling
    results = client.download_files(
        library_name="Documents",
        folder_path="General/Reports",
        filenames=["report1.xlsx", "report2.xlsx"],
        download_dir="./downloads"
    )
```

### Test Structure

- Tests located in `__tests__/` directories co-located with source code
- Uses pytest with extensions: pytest-asyncio, pytest-mock, pytest-cov
- Integration tests for authentication flows
- Mock-based tests for SharePoint API interactions

### Configuration

Uses `uv` for dependency management with:

- **Ruff** for linting/formatting (120 char line length, strict import organization)
- **Pyright** for type checking (strict mode, Python 3.13 target)
- **Pytest** for testing with coverage reporting
- **Just** for task automation

## Key Features

### 1. **Federated Authentication**

- Supports enterprise users with Azure AD authentication
- Handles federated authentication flow transparently
- Provides detailed error messages for auth failures

### 2. **Path Validation**

- Hierarchical path validation with detailed error reporting
- Shows exactly which folder is missing and available alternatives
- Supports both coupled and decoupled path configurations

### 3. **File Operations**

- Lists Excel files with complete metadata
- Downloads files with size validation
- Supports batch downloads with per-file error handling

### 4. **Library Discovery**

- Explores SharePoint library structure up to specified depth
- Helps with debugging path configurations
- Outputs in both human-readable and JSON formats

## Error Handling

The library provides comprehensive error handling with:

- Custom exception hierarchy for different failure types
- Context-aware error messages with helpful debugging information
- Secure masking of sensitive information in logs
- Detailed error reporting for path validation failures

## Security Considerations

1. **Credential Protection**:

   - Passwords stored as `SecretStr` in Pydantic models
   - Usernames masked in logs (shows only first 3 characters)
   - Sensitive configuration values masked in error messages

2. **File Size Limits**:

   - Default 100MB limit (configurable)
   - Prevents downloading excessively large files

3. **Read-Only Access**:
   - Library designed for read-only operations
   - No write/modify/delete operations on SharePoint

## Installation and Deployment

### As a Package

```bash
# Install dependencies
pip install office365-rest-python-client>=2.6.2 pydantic>=2.11.7

# Install the library
pip install fetchpoint  # When published to PyPI
```

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd fetchpoint

# Install in development mode
pip install -e .

# Run tests
python -m pytest
```

## Development lifecycle

**IMPORTANT**: after every code change, run (in order):

- uv run ruff format src
- uv run ruff check --fix src
- uv run pyright src
- uv run pytest src -vv
