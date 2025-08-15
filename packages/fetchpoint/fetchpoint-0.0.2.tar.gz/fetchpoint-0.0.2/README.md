# FetchPoint

A Python library for SharePoint Online integration with federated authentication support.

## Overview

FetchPoint is a clean, enterprise-ready library for SharePoint Online integration with federated authentication support. Provides secure, read-only access to files stored in SharePoint document libraries with comprehensive error handling, metadata extraction, and Excel file focus. Designed for enterprise environments with Azure AD and federated authentication.

## Key Features

- **Federated Authentication**: Azure AD and enterprise identity provider support
- **Read-Only Operations**: Secure file listing and downloading
- **Excel Focus**: Optimized for .xlsx, .xls, .xlsm, .xlsb files
- **Path Validation**: Hierarchical folder navigation with detailed error reporting
- **Context Manager**: Clean resource management
- **Comprehensive Error Handling**: Detailed diagnostics for troubleshooting
- **No Environment Dependencies**: Explicit configuration required (environment variables optional)

## Installation

```bash
uv add fetchpoint
```

## Quick Start

```python
from fetchpoint import SharePointClient, create_sharepoint_config

# Create configuration
config = create_sharepoint_config(
    username="user@company.com",
    password="your_password",
    sharepoint_url="https://company.sharepoint.com/sites/project"
)

# Use context manager (recommended)
with SharePointClient(config) as client:
    # List Excel files
    files = client.list_excel_files(
        library_name="Documents",
        folder_path="General/Reports"
    )

    # Download files
    results = client.download_files(
        library_name="Documents",
        folder_path="General/Reports",
        filenames=files,
        download_dir="./downloads"
    )
```

## Configuration

### Method 1: Explicit Configuration

```python
from fetchpoint import create_sharepoint_config

config = create_sharepoint_config(
    username="user@company.com",           # Required: SharePoint username (email)
    password="your_password",              # Required: User password
    sharepoint_url="https://company.sharepoint.com/sites/yoursite",  # Required: SharePoint site URL
    timeout_seconds=30,                    # Optional: Connection timeout (default: 30)
    max_file_size_mb=100                   # Optional: File size limit (default: 100)
)
```

### Method 2: Dictionary Configuration

```python
from fetchpoint import SharePointClient

client = SharePointClient.from_dict({
    "username": "user@company.com",
    "password": "your_password",
    "sharepoint_url": "https://company.sharepoint.com/sites/yoursite"
})
```

### Method 3: Environment Variables (Legacy)

```bash
# Required
SHAREPOINT_URL=https://company.sharepoint.com/sites/yoursite
SHAREPOINT_USERNAME=user@company.com
SHAREPOINT_PASSWORD=your_password

# Optional
SHAREPOINT_TIMEOUT_SECONDS=30
SHAREPOINT_MAX_FILE_SIZE_MB=100
SHAREPOINT_AUTH_TYPE=federated
SHAREPOINT_SESSION_TIMEOUT=3600
SHAREPOINT_LOG_LEVEL=INFO
```

**Important**: `SHAREPOINT_URL` is optional when using explicit configuration methods. When using environment variables, it's required and specifies the complete SharePoint site URL.

## API Reference

### SharePointClient

Main client class for SharePoint operations.

#### Methods

**`connect() -> bool`**

- Establish connection to SharePoint
- Returns: `True` if successful

**`test_connection() -> bool`**

- Validate current connection
- Returns: `True` if connection is valid

**`disconnect() -> None`**

- Clean up connection and resources

**`list_excel_files(library_name: str, folder_path: str) -> list[str]`**

- List Excel file names in specified location
- Args: `library_name` (default: "Documents"), `folder_path` (e.g., "General/Reports")
- Returns: List of Excel filenames

**`list_files(library: str, path: list[str]) -> list[FileInfo]`**

- List files with complete metadata
- Args: `library` name, `path` segments
- Returns: List of FileInfo objects with metadata

**`list_folders(library_name: str, folder_path: str) -> list[str]`**

- List folder names in specified location
- Returns: List of folder names

**`download_file(library: str, path: list[str], local_path: str) -> None`**

- Download single file
- Args: `library` name, `path` segments including filename, `local_path`

**`download_files(library_name: str, folder_path: str, filenames: list[str], download_dir: str) -> dict`**

- Download multiple files with per-file error handling
- Returns: Dictionary with success/failure status for each file

**`get_file_details(library_name: str, folder_path: str, filename: str) -> FileInfo`**

- Get comprehensive file metadata
- Returns: FileInfo object with complete metadata

**`validate_paths(library_name: str) -> dict`**

- Validate configured SharePoint paths
- Returns: Validation results with error details and available folders

**`discover_structure(library_name: str, max_depth: int) -> dict`**

- Explore SharePoint library structure
- Returns: Hierarchical representation of folders and files

### Configuration Functions

**`create_sharepoint_config(...) -> SharePointAuthConfig`**

- Create configuration with explicit parameters

**`create_config_from_dict(config_dict: dict) -> SharePointAuthConfig`**

- Create configuration from dictionary

**`create_authenticated_context(config: SharePointAuthConfig) -> ClientContext`**

- Create authenticated SharePoint context

### Models

**`SharePointAuthConfig`**

- Configuration model with validation
- Fields: `username`, `password`, `sharepoint_url`, `timeout_seconds`, `max_file_size_mb`

**`FileInfo`**

- File metadata model
- Fields: `name`, `size_bytes`, `size_mb`, `created_date`, `modified_date`, `file_type`, `library_name`, `folder_path`, `created_by`, `modified_by`

**`FileType`**

- Enum for supported Excel extensions
- Values: `XLSX`, `XLS`, `XLSM`, `XLSB`

### Exceptions

All exceptions inherit from `SharePointError`:

- **`AuthenticationError`**: Authentication failures
- **`FederatedAuthError`**: Federated authentication issues (Azure AD specific)
- **`ConnectionError`**: Connection problems
- **`FileNotFoundError`**: File not found in SharePoint
- **`FileDownloadError`**: Download failures
- **`FileSizeLimitError`**: File exceeds size limit
- **`ConfigurationError`**: Invalid configuration
- **`PermissionError`**: Access denied
- **`LibraryNotFoundError`**: Document library not found
- **`InvalidFileTypeError`**: Unsupported file type

## Security

- Passwords stored as `SecretStr` (Pydantic)
- Usernames masked in logs (first 3 characters only)
- Read-only operations only
- Configurable file size limits (default: 100MB)
- No environment dependencies by default

## Error Handling

FetchPoint provides detailed error messages with context:

```python
try:
    with SharePointClient(config) as client:
        files = client.list_excel_files("Documents", "NonExistent/Path")
except LibraryNotFoundError as e:
    print(f"Library error: {e}")
    print(f"Available folders: {e.available_folders}")
```

## Development

For project developers working on the fetchpoint library:

### Setup

```bash
# Install dependencies
uv sync --all-groups

# Build wheel package
uv build --wheel
```

### Development Commands

**Code Quality (run after every change):**

```bash
# Format code
uv run ruff format src

# Lint with auto-fix
uv run ruff check --fix src

# Type checking
uv run pyright src

# Run tests
uv run pytest src -vv

# Run tests with coverage
uv run pytest src --cov=src --cov-report=term-missing
```

**Complete validation workflow:**

```bash
uv run ruff format src && uv run ruff check --fix src && uv run pyright src && uv run pytest src -vv
```

### Testing

- Tests located in `__tests__/` directories co-located with source code
- Use pytest with extensions (pytest-asyncio, pytest-mock, pytest-cov)
- Minimum 90% coverage for critical components

### Version Management

FetchPoint uses a single source of truth for version management:

- **Version Source**: `src/fetchpoint/__init__.py` contains `__version__ = "x.y.z"`
- **Dynamic Configuration**: `pyproject.toml` reads version automatically from `__init__.py`
- **Publishing Workflow**:
  1. Update version in `src/fetchpoint/__init__.py`
  2. Build: `uv build --wheel`
  3. Publish: `uv publish --token $PYPI_TOKEN`

Update `uv.lock` via:

```sh
uv lock --refresh
```

**Version Access:**

```python
import fetchpoint
print(fetchpoint.__version__)  # e.g., "0.2.0"
```

### Publishing Quick Reference

```bash
just validate
rm -rf dist/
uv build --wheel && uv build --sdist
uv publish --token $PYPI_TOKEN
```

## Roadmap

- Download a single file by path
- Handle filetypes

## License

Open source library for SharePoint Online integration.
