"""
Custom exception classes for FetchPoint SharePoint operations.

This module provides a comprehensive exception hierarchy for SharePoint operations
with clear error messages and helpful context information for debugging.
"""

from typing import Any, Optional


class SharePointError(Exception):
    """
    Base exception class for all FetchPoint SharePoint operations.

    This is the root exception that all other SharePoint-related exceptions inherit from.
    It provides common functionality for error context and string representation.
    """

    def __init__(self, message: str, operation: Optional[str] = None, context: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize SharePoint error with message and optional context.

        Args:
            message: Human-readable error description
            operation: The operation that failed (e.g., 'authenticate', 'download_file')
            context: Additional context information (file_path, library_name, etc.)
        """
        super().__init__(message)
        self.message = message
        self.operation = operation
        self.context = context or {}

    def __str__(self) -> str:
        """Return user-friendly error message."""
        if self.operation:
            return f"SharePoint {self.operation} failed: {self.message}"
        return f"SharePoint error: {self.message}"

    def __repr__(self) -> str:
        """Return detailed error representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"operation={self.operation!r}, "
            f"context={self.context!r})"
        )


class AuthenticationError(SharePointError):
    """
    Exception raised when SharePoint authentication fails.

    This covers general authentication failures but not federated auth specific issues.
    """

    def __init__(self, message: str, username: Optional[str] = None, site_url: Optional[str] = None) -> None:
        """
        Initialize authentication error.

        Args:
            message: Error description
            username: Masked username (first 3 chars + ***)
            site_url: SharePoint site URL
        """
        context: dict[str, Any] = {}
        if username:
            # Mask username for security - show only first 3 chars
            masked_username = username[:3] + "***" if len(username) > 3 else "***"
            context["username"] = masked_username
        if site_url:
            context["site_url"] = site_url

        super().__init__(message, operation="authenticate", context=context)


class FederatedAuthError(AuthenticationError):
    """
    Exception raised when federated authentication fails.

    This is specific to federated authentication issues with enterprise SharePoint environments.
    """

    def __init__(
        self,
        message: str,
        username: Optional[str] = None,
        site_url: Optional[str] = None,
        auth_provider: Optional[str] = None,
    ) -> None:
        """
        Initialize federated authentication error.

        Args:
            message: Error description
            username: Masked username
            site_url: SharePoint site URL
            auth_provider: Identity provider name (e.g., 'Azure AD')
        """
        super().__init__(message, username, site_url)
        if auth_provider:
            self.context["auth_provider"] = auth_provider


class FileNotFoundError(SharePointError):
    """
    Exception raised when a requested file cannot be found in SharePoint.
    """

    def __init__(self, file_path: str, library_name: Optional[str] = None, site_url: Optional[str] = None) -> None:
        """
        Initialize file not found error.

        Args:
            file_path: Path to the file that was not found
            library_name: SharePoint document library name
            site_url: SharePoint site URL
        """
        message = f"File not found: {file_path}"
        context: dict[str, Any] = {"file_path": file_path}

        if library_name:
            context["library_name"] = library_name
            message += f" in library '{library_name}'"
        if site_url:
            context["site_url"] = site_url

        super().__init__(message, operation="find_file", context=context)


class FileDownloadError(SharePointError):
    """
    Exception raised when file download fails.
    """

    def __init__(
        self, file_path: str, reason: str, library_name: Optional[str] = None, file_size: Optional[int] = None
    ) -> None:
        """
        Initialize file download error.

        Args:
            file_path: Path to the file that failed to download
            reason: Specific reason for download failure
            library_name: SharePoint document library name
            file_size: File size in bytes if known
        """
        message = f"Failed to download file '{file_path}': {reason}"
        context: dict[str, Any] = {"file_path": file_path, "reason": reason}

        if library_name:
            context["library_name"] = library_name
        if file_size is not None:
            context["file_size"] = file_size

        super().__init__(message, operation="download_file", context=context)


class FileSizeLimitError(SharePointError):
    """
    Exception raised when file exceeds the 100MB size limit.
    """

    def __init__(
        self,
        file_path: str,
        file_size: int,
        size_limit: int = 100 * 1024 * 1024,  # 100MB in bytes
    ) -> None:
        """
        Initialize file size limit error.

        Args:
            file_path: Path to the oversized file
            file_size: Actual file size in bytes
            size_limit: Maximum allowed size in bytes
        """
        size_mb = file_size / (1024 * 1024)
        limit_mb = size_limit / (1024 * 1024)

        message = f"File '{file_path}' is too large ({size_mb:.1f}MB). Maximum size allowed is {limit_mb:.0f}MB"

        context: dict[str, Any] = {"file_path": file_path, "file_size": file_size, "size_limit": size_limit}

        super().__init__(message, operation="validate_file_size", context=context)


class ConfigurationError(SharePointError):
    """
    Exception raised when SharePoint configuration is invalid or missing.
    """

    def __init__(self, message: str, config_field: Optional[str] = None, config_value: Optional[str] = None) -> None:
        """
        Initialize configuration error.

        Args:
            message: Error description
            config_field: Name of the configuration field that's invalid
            config_value: Invalid configuration value (masked if sensitive)
        """
        context: dict[str, Any] = {}
        if config_field:
            context["config_field"] = config_field
        if config_value:
            # Mask potentially sensitive config values
            if any(sensitive in config_field.lower() for sensitive in ["password", "secret", "token"] if config_field):
                context["config_value"] = "***masked***"
            else:
                context["config_value"] = config_value

        super().__init__(message, operation="validate_config", context=context)


class ConnectionError(SharePointError):
    """
    Exception raised when connection to SharePoint fails.
    """

    def __init__(self, message: str, site_url: Optional[str] = None, timeout: Optional[int] = None) -> None:
        """
        Initialize connection error.

        Args:
            message: Error description
            site_url: SharePoint site URL
            timeout: Connection timeout in seconds if applicable
        """
        context: dict[str, Any] = {}
        if site_url:
            context["site_url"] = site_url
        if timeout is not None:
            context["timeout"] = timeout

        super().__init__(message, operation="connect", context=context)


class PermissionError(SharePointError):
    """
    Exception raised when user lacks permission for SharePoint operation.
    """

    def __init__(
        self, message: str, operation: str, resource: Optional[str] = None, username: Optional[str] = None
    ) -> None:
        """
        Initialize permission error.

        Args:
            message: Error description
            operation: The operation that was denied
            resource: Resource that access was denied to
            username: Masked username
        """
        context: dict[str, Any] = {"denied_operation": operation}
        if resource:
            context["resource"] = resource
        if username:
            # Mask username for security
            masked_username = username[:3] + "***" if len(username) > 3 else "***"
            context["username"] = masked_username

        super().__init__(message, operation="check_permissions", context=context)


class LibraryNotFoundError(SharePointError):
    """
    Exception raised when SharePoint document library cannot be found.
    """

    def __init__(
        self, library_name: str, site_url: Optional[str] = None, available_libraries: Optional[list[str]] = None
    ) -> None:
        """
        Initialize library not found error.

        Args:
            library_name: Name of the library that was not found
            site_url: SharePoint site URL
            available_libraries: List of available library names
        """
        message = f"Document library '{library_name}' not found"
        context: dict[str, Any] = {"library_name": library_name}

        if site_url:
            context["site_url"] = site_url
        if available_libraries:
            context["available_libraries"] = available_libraries
            message += f". Available libraries: {', '.join(available_libraries)}"

        super().__init__(message, operation="find_library", context=context)


class InvalidFileTypeError(SharePointError):
    """
    Exception raised when file type is not supported.
    """

    def __init__(self, file_path: str, file_extension: str, supported_extensions: Optional[list[str]] = None) -> None:
        """
        Initialize invalid file type error.

        Args:
            file_path: Path to the invalid file
            file_extension: The unsupported file extension
            supported_extensions: List of supported file extensions
        """
        message = f"File '{file_path}' has unsupported extension '{file_extension}'"
        context: dict[str, Any] = {"file_path": file_path, "file_extension": file_extension}

        if supported_extensions:
            context["supported_extensions"] = supported_extensions
            message += f". Supported extensions: {', '.join(supported_extensions)}"

        super().__init__(message, operation="validate_file_type", context=context)
