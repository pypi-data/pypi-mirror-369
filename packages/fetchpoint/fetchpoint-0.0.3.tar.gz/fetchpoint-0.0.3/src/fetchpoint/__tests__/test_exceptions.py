"""
Unit tests for FetchPoint custom exceptions.

This module tests all custom exception classes for proper initialization,
string representations, context handling, and inheritance hierarchy.
"""

from fetchpoint.exceptions import (
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


class TestSharePointError:
    """Test cases for the base SharePointError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic exception initialization with message only."""
        error = SharePointError("Test error message")

        assert error.message == "Test error message"
        assert error.operation is None
        assert error.context == {}

    def test_initialization_with_operation(self) -> None:
        """Test exception initialization with operation."""
        error = SharePointError("Test error", operation="test_operation")

        assert error.message == "Test error"
        assert error.operation == "test_operation"
        assert error.context == {}

    def test_initialization_with_context(self) -> None:
        """Test exception initialization with context."""
        context = {"file_path": "/test/path", "library": "TestLib"}
        error = SharePointError("Test error", context=context)

        assert error.message == "Test error"
        assert error.operation is None
        assert error.context == context

    def test_str_without_operation(self) -> None:
        """Test string representation without operation."""
        error = SharePointError("Test error message")
        expected = "SharePoint error: Test error message"

        assert str(error) == expected

    def test_str_with_operation(self) -> None:
        """Test string representation with operation."""
        error = SharePointError("Test error", operation="authenticate")
        expected = "SharePoint authenticate failed: Test error"

        assert str(error) == expected

    def test_repr(self) -> None:
        """Test detailed representation for debugging."""
        context = {"key": "value"}
        error = SharePointError("Test error", "test_op", context)
        expected = "SharePointError(message='Test error', operation='test_op', context={'key': 'value'})"

        assert repr(error) == expected

    def test_inheritance_from_exception(self) -> None:
        """Test that SharePointError inherits from Exception."""
        error = SharePointError("Test error")

        assert isinstance(error, Exception)
        assert isinstance(error, SharePointError)


class TestAuthenticationError:
    """Test cases for AuthenticationError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic authentication error initialization."""
        error = AuthenticationError("Auth failed")

        assert error.message == "Auth failed"
        assert error.operation == "authenticate"
        assert error.context == {}

    def test_initialization_with_username(self) -> None:
        """Test authentication error with username masking."""
        error = AuthenticationError("Auth failed", username="testuser@company.com")

        assert error.message == "Auth failed"
        assert error.operation == "authenticate"
        assert error.context["username"] == "tes***"

    def test_initialization_with_short_username(self) -> None:
        """Test authentication error with short username masking."""
        error = AuthenticationError("Auth failed", username="ab")

        assert error.context["username"] == "***"

    def test_initialization_with_site_url(self) -> None:
        """Test authentication error with site URL."""
        site_url = "https://company.sharepoint.com/sites/test"
        error = AuthenticationError("Auth failed", site_url=site_url)

        assert error.context["site_url"] == site_url

    def test_inheritance(self) -> None:
        """Test AuthenticationError inheritance hierarchy."""
        error = AuthenticationError("Test error")

        assert isinstance(error, SharePointError)
        assert isinstance(error, AuthenticationError)


class TestFederatedAuthError:
    """Test cases for FederatedAuthError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic federated auth error initialization."""
        error = FederatedAuthError("Federated auth failed")

        assert error.message == "Federated auth failed"
        assert error.operation == "authenticate"

    def test_initialization_with_auth_provider(self) -> None:
        """Test federated auth error with auth provider."""
        error = FederatedAuthError("Federated auth failed", username="testuser@company.com", auth_provider="Azure AD")

        assert error.context["username"] == "tes***"
        assert error.context["auth_provider"] == "Azure AD"

    def test_inheritance(self) -> None:
        """Test FederatedAuthError inheritance hierarchy."""
        error = FederatedAuthError("Test error")

        assert isinstance(error, SharePointError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, FederatedAuthError)


class TestFileNotFoundError:
    """Test cases for FileNotFoundError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic file not found error initialization."""
        error = FileNotFoundError("/path/to/file.xlsx")

        assert error.message == "File not found: /path/to/file.xlsx"
        assert error.operation == "find_file"
        assert error.context["file_path"] == "/path/to/file.xlsx"

    def test_initialization_with_library(self) -> None:
        """Test file not found error with library name."""
        error = FileNotFoundError("/path/to/file.xlsx", library_name="Documents")

        expected_message = "File not found: /path/to/file.xlsx in library 'Documents'"
        assert error.message == expected_message
        assert error.context["library_name"] == "Documents"

    def test_inheritance(self) -> None:
        """Test FileNotFoundError inheritance hierarchy."""
        error = FileNotFoundError("/test/path")

        assert isinstance(error, SharePointError)
        assert isinstance(error, FileNotFoundError)


class TestFileDownloadError:
    """Test cases for FileDownloadError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic file download error initialization."""
        error = FileDownloadError("/path/to/file.xlsx", "Network timeout")

        expected_message = "Failed to download file '/path/to/file.xlsx': Network timeout"
        assert error.message == expected_message
        assert error.operation == "download_file"
        assert error.context["file_path"] == "/path/to/file.xlsx"
        assert error.context["reason"] == "Network timeout"

    def test_inheritance(self) -> None:
        """Test FileDownloadError inheritance hierarchy."""
        error = FileDownloadError("/test/path", "test reason")

        assert isinstance(error, SharePointError)
        assert isinstance(error, FileDownloadError)


class TestFileSizeLimitError:
    """Test cases for FileSizeLimitError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic file size limit error initialization."""
        file_size = 150 * 1024 * 1024  # 150MB
        error = FileSizeLimitError("/path/to/large_file.xlsx", file_size)

        expected_message = "File '/path/to/large_file.xlsx' is too large (150.0MB). Maximum size allowed is 100MB"
        assert error.message == expected_message
        assert error.operation == "validate_file_size"
        assert error.context["file_path"] == "/path/to/large_file.xlsx"
        assert error.context["file_size"] == file_size
        assert error.context["size_limit"] == 100 * 1024 * 1024

    def test_inheritance(self) -> None:
        """Test FileSizeLimitError inheritance hierarchy."""
        error = FileSizeLimitError("/test/path", 1024)

        assert isinstance(error, SharePointError)
        assert isinstance(error, FileSizeLimitError)


class TestConfigurationError:
    """Test cases for ConfigurationError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic configuration error initialization."""
        error = ConfigurationError("Invalid configuration")

        assert error.message == "Invalid configuration"
        assert error.operation == "validate_config"
        assert error.context == {}

    def test_sensitive_value_masking(self) -> None:
        """Test that sensitive configuration values are masked."""
        error = ConfigurationError("Invalid password", config_field="password", config_value="secret123")

        assert error.context["config_field"] == "password"
        assert error.context["config_value"] == "***masked***"

    def test_non_sensitive_value_not_masked(self) -> None:
        """Test that non-sensitive values are not masked."""
        error = ConfigurationError("Invalid site URL", config_field="site_url", config_value="invalid-url")

        assert error.context["config_value"] == "invalid-url"

    def test_inheritance(self) -> None:
        """Test ConfigurationError inheritance hierarchy."""
        error = ConfigurationError("Test error")

        assert isinstance(error, SharePointError)
        assert isinstance(error, ConfigurationError)


class TestConnectionError:
    """Test cases for ConnectionError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic connection error initialization."""
        error = ConnectionError("Connection failed")

        assert error.message == "Connection failed"
        assert error.operation == "connect"
        assert error.context == {}

    def test_inheritance(self) -> None:
        """Test ConnectionError inheritance hierarchy."""
        error = ConnectionError("Test error")

        assert isinstance(error, SharePointError)
        assert isinstance(error, ConnectionError)


class TestPermissionError:
    """Test cases for PermissionError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic permission error initialization."""
        error = PermissionError("Access denied", "read_file")

        assert error.message == "Access denied"
        assert error.operation == "check_permissions"
        assert error.context["denied_operation"] == "read_file"

    def test_username_masking(self) -> None:
        """Test permission error with username masking."""
        error = PermissionError("Access denied", "read_file", username="testuser@company.com")

        assert error.context["username"] == "tes***"

    def test_inheritance(self) -> None:
        """Test PermissionError inheritance hierarchy."""
        error = PermissionError("Test error", "test_op")

        assert isinstance(error, SharePointError)
        assert isinstance(error, PermissionError)


class TestLibraryNotFoundError:
    """Test cases for LibraryNotFoundError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic library not found error initialization."""
        error = LibraryNotFoundError("Documents")

        expected_message = "Document library 'Documents' not found"
        assert error.message == expected_message
        assert error.operation == "find_library"
        assert error.context["library_name"] == "Documents"

    def test_with_available_libraries(self) -> None:
        """Test library not found error with available libraries."""
        available = ["Shared Documents", "Forms", "Site Assets"]
        error = LibraryNotFoundError("Documents", available_libraries=available)

        expected_message = (
            "Document library 'Documents' not found. Available libraries: Shared Documents, Forms, Site Assets"
        )
        assert error.message == expected_message
        assert error.context["available_libraries"] == available

    def test_inheritance(self) -> None:
        """Test LibraryNotFoundError inheritance hierarchy."""
        error = LibraryNotFoundError("TestLib")

        assert isinstance(error, SharePointError)
        assert isinstance(error, LibraryNotFoundError)


class TestInvalidFileTypeError:
    """Test cases for InvalidFileTypeError exception class."""

    def test_basic_initialization(self) -> None:
        """Test basic invalid file type error initialization."""
        error = InvalidFileTypeError("/path/to/file.txt", ".txt")

        expected_message = "File '/path/to/file.txt' has unsupported extension '.txt'"
        assert error.message == expected_message
        assert error.operation == "validate_file_type"
        assert error.context["file_path"] == "/path/to/file.txt"
        assert error.context["file_extension"] == ".txt"

    def test_with_supported_extensions(self) -> None:
        """Test invalid file type error with supported extensions."""
        supported = [".xlsx", ".xls", ".xlsm", ".xlsb"]
        error = InvalidFileTypeError("/path/to/file.txt", ".txt", supported_extensions=supported)

        expected_message = (
            "File '/path/to/file.txt' has unsupported extension '.txt'. Supported extensions: .xlsx, .xls, .xlsm, .xlsb"
        )
        assert error.message == expected_message
        assert error.context["supported_extensions"] == supported

    def test_inheritance(self) -> None:
        """Test InvalidFileTypeError inheritance hierarchy."""
        error = InvalidFileTypeError("/test/path", ".txt")

        assert isinstance(error, SharePointError)
        assert isinstance(error, InvalidFileTypeError)


class TestExceptionHierarchy:
    """Test cases for the overall exception hierarchy."""

    def test_all_exceptions_inherit_from_sharepoint_error(self) -> None:
        """Test that all custom exceptions inherit from SharePointError."""
        # Test key exceptions with proper parameters
        auth_error = AuthenticationError("test")
        file_error = FileNotFoundError("test_path")
        config_error = ConfigurationError("test")
        download_error = FileDownloadError("test_path", "test_reason")
        size_error = FileSizeLimitError("test_path", 1024)
        permission_error = PermissionError("test", "test_op")
        library_error = LibraryNotFoundError("test_lib")
        filetype_error = InvalidFileTypeError("test_path", ".txt")

        all_errors = [
            auth_error,
            file_error,
            config_error,
            download_error,
            size_error,
            permission_error,
            library_error,
            filetype_error,
        ]

        for error in all_errors:
            assert isinstance(error, SharePointError)
            assert isinstance(error, Exception)

    def test_federated_auth_error_inheritance_chain(self) -> None:
        """Test specific inheritance chain for FederatedAuthError."""
        error = FederatedAuthError("test")

        assert isinstance(error, Exception)
        assert isinstance(error, SharePointError)
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, FederatedAuthError)

    def test_exception_context_isolation(self) -> None:
        """Test that exception contexts don't interfere with each other."""
        error1 = SharePointError("Error 1", context={"key": "value1"})
        error2 = SharePointError("Error 2", context={"key": "value2"})

        assert error1.context["key"] == "value1"
        assert error2.context["key"] == "value2"

        # Modify one context and ensure the other is unaffected
        error1.context["new_key"] = "new_value"
        assert "new_key" not in error2.context
