"""
FetchPoint - A modern SharePoint client library for Python.

Provides secure, read-only access to SharePoint document libraries with federated
authentication support and comprehensive error handling.
"""

from .authenticator import create_authenticated_context
from .client import SharePointClient
from .config import (
    create_config_from_dict,
    create_sharepoint_config,
    # Deprecated - for backward compatibility only
    load_sharepoint_config,
)
from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    FederatedAuthError,
    FileDownloadError,
    FileNotFoundError,
    FileSizeLimitError,
    InvalidFileTypeError,
    LibraryNotFoundError,
    PermissionError,
    SharePointError,
)
from .models import ColumnMapping, ExcelData, FileInfo, FileType, SharePointAuthConfig

__all__ = [
    # Main API
    "SharePointClient",
    "SharePointAuthConfig",
    "create_sharepoint_config",
    "create_config_from_dict",
    # File operations
    "FileInfo",
    "FileType",
    # Excel operations
    "ExcelData",
    "ColumnMapping",
    # Authentication
    "create_authenticated_context",
    # Exceptions
    "SharePointError",
    "AuthenticationError",
    "FederatedAuthError",
    "FileNotFoundError",
    "FileDownloadError",
    "FileSizeLimitError",
    "ConfigurationError",
    "ConnectionError",
    "PermissionError",
    "LibraryNotFoundError",
    "InvalidFileTypeError",
    # Deprecated
    "load_sharepoint_config",
]

__version__ = "0.0.3"
