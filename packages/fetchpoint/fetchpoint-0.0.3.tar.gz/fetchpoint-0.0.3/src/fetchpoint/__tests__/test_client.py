"""
Unit tests for SharePoint client implementation.

Tests cover client initialization, connection management, context manager support,
and test connection functionality as specified in Issue #6.
"""

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from fetchpoint.client import SharePointClient
from fetchpoint.config import SharePointAuthConfig
from fetchpoint.exceptions import AuthenticationError, ConnectionError, PermissionError

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestSharePointClient:
    """Test cases for SharePoint client base implementation."""

    def test_init_with_config(self) -> None:
        """Test client initialization with provided configuration."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        client = SharePointClient(config)

        assert client.config == config
        assert not client.is_connected
        assert client.context is None

    def test_init_without_config_raises_error(self) -> None:
        """Test client initialization raises error when no config provided."""
        with pytest.raises(ValueError, match="Configuration is required"):
            SharePointClient(None)  # type: ignore[arg-type]

    @patch("fetchpoint.client.create_authenticated_context")
    def test_connect_success(self, mock_create_context: "MagicMock") -> None:
        """Test successful connection to SharePoint."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        result = client.connect()

        assert result is True
        assert client.is_connected
        assert client.context == mock_context
        mock_create_context.assert_called_once_with(config)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_connect_failure(self, mock_create_context: "MagicMock") -> None:
        """Test connection failure handling."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_create_context.side_effect = AuthenticationError("Auth failed")

        client = SharePointClient(config)

        with pytest.raises(AuthenticationError):
            client.connect()

        assert not client.is_connected
        assert client.context is None

    def test_test_connection_not_connected(self) -> None:
        """Test test_connection when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.test_connection()

        assert "Not connected to SharePoint" in str(exc_info.value)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_test_connection_success(self, mock_create_context: "MagicMock") -> None:
        """Test successful connection test."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        # Mock the context and web properties
        mock_web = Mock()
        mock_context = Mock()
        mock_context.web = mock_web
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        result = client.test_connection()

        assert result is True
        mock_context.load.assert_called_once_with(mock_web)
        mock_context.execute_query.assert_called_once()

    @patch("fetchpoint.client.create_authenticated_context")
    def test_test_connection_failure(self, mock_create_context: "MagicMock") -> None:
        """Test connection test failure."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )

        # Mock context that fails on execute_query
        mock_context = Mock()
        mock_context.execute_query.side_effect = Exception("Network error")
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        with pytest.raises(ConnectionError) as exc_info:
            client.test_connection()

        assert "Connection test failed" in str(exc_info.value)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_disconnect(self, mock_create_context: "MagicMock") -> None:
        """Test disconnection from SharePoint."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        # Verify connected state
        assert client.is_connected
        assert client.context is not None

        # Disconnect
        client.disconnect()

        # Verify disconnected state
        assert not client.is_connected
        assert client.context is None

    def test_disconnect_when_not_connected(self) -> None:
        """Test disconnect is safe when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        # Should not raise any errors
        client.disconnect()

        assert not client.is_connected
        assert client.context is None

    @patch("fetchpoint.client.create_authenticated_context")
    def test_context_manager_success(self, mock_create_context: "MagicMock") -> None:
        """Test context manager with successful connection."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)

        with client as ctx:
            assert ctx is client
            assert client.is_connected
            assert client.context == mock_context

        # Should be disconnected after context exit
        assert not client.is_connected
        assert client.context is None

    @patch("fetchpoint.client.create_authenticated_context")
    def test_context_manager_with_exception(self, mock_create_context: "MagicMock") -> None:
        """Test context manager properly cleans up on exception."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)

        with pytest.raises(ValueError):
            with client:
                raise ValueError("Test exception")

        # Should be disconnected after exception
        assert not client.is_connected
        assert client.context is None

    @patch("fetchpoint.client.create_authenticated_context")
    def test_context_manager_connection_failure(self, mock_create_context: "MagicMock") -> None:
        """Test context manager with connection failure."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_create_context.side_effect = AuthenticationError("Connection failed")

        client = SharePointClient(config)

        with pytest.raises(AuthenticationError):
            with client:
                pass  # Should fail on __enter__

    def test_string_representations(self) -> None:
        """Test string representation of client."""
        config = SharePointAuthConfig(
            username="test.user@example.com",
            password=SecretStr("password"),
            sharepoint_url="https://example.sharepoint.com/sites/test",
        )
        client = SharePointClient(config)

        str_repr = str(client)
        assert "SharePointClient" in str_repr
        assert "tes***" in str_repr  # Masked username
        assert "example.sharepoint.com" in str_repr
        assert "connected=disconnected" in str_repr

        repr_str = repr(client)
        assert "SharePointClient" in repr_str
        assert "tes***" in repr_str

    def test_string_representations_short_username(self) -> None:
        """Test string representation with short username."""
        config = SharePointAuthConfig(
            username="ab@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        str_repr = str(client)
        assert "ab@***" in str_repr  # Short username with masking (first 3 chars)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_properties(self, mock_create_context: "MagicMock") -> None:
        """Test client properties."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)

        # Test initial state
        assert client.config == config
        assert client.config.sharepoint_url == config.sharepoint_url
        assert client.config.username == config.username
        assert not client.is_connected
        assert client.context is None

        # Test connected state
        client.connect()
        assert client.is_connected
        assert client.context is mock_context

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_excel_files_by_path_segments")
    def test_list_excel_files_not_connected(
        self, mock_list_files: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test list_excel_files when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.list_excel_files()

        assert "Not connected to SharePoint" in str(exc_info.value)
        mock_list_files.assert_not_called()

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_excel_files_by_path_segments")
    def test_list_excel_files_success(self, mock_list_files: "MagicMock", mock_create_context: "MagicMock") -> None:
        """Test successful Excel files listing."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_list_files.return_value = ["file1.xlsx", "file2.xlsx"]

        client = SharePointClient(config)
        client.connect()

        # Test with default parameters
        result = client.list_excel_files()

        assert result == ["file1.xlsx", "file2.xlsx"]
        mock_list_files.assert_called_once_with(mock_context, "Documents", [])

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_excel_files_by_path_segments")
    def test_list_excel_files_with_folder_path(
        self, mock_list_files: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test Excel files listing with folder path."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_list_files.return_value = ["report.xlsx"]

        client = SharePointClient(config)
        client.connect()

        # Test with folder path
        result = client.list_excel_files("MyLibrary", "General/Reports")

        assert result == ["report.xlsx"]
        mock_list_files.assert_called_once_with(mock_context, "MyLibrary", ["General", "Reports"])

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_folders_in_library")
    def test_list_folders_not_connected(self, mock_list_folders: "MagicMock", mock_create_context: "MagicMock") -> None:
        """Test list_folders when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.list_folders()

        assert "Not connected to SharePoint" in str(exc_info.value)
        mock_list_folders.assert_not_called()

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_folders_in_library")
    def test_list_folders_success(self, mock_list_folders: "MagicMock", mock_create_context: "MagicMock") -> None:
        """Test successful folders listing."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_list_folders.return_value = ["Folder1", "Folder2"]

        client = SharePointClient(config)
        client.connect()

        result = client.list_folders("TestLibrary", "some/path")

        assert result == ["Folder1", "Folder2"]
        mock_list_folders.assert_called_once_with(mock_context, "TestLibrary", "some/path")

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.load_sharepoint_paths")
    @patch("fetchpoint.client.PathResolver")
    def test_validate_paths_not_connected(
        self, mock_path_resolver: "MagicMock", mock_load_paths: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test validate_paths when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.validate_paths()

        assert "Not connected to SharePoint" in str(exc_info.value)
        mock_load_paths.assert_not_called()

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.load_sharepoint_paths")
    @patch("fetchpoint.client.PathResolver")
    def test_validate_paths_success(
        self, mock_path_resolver_class: "MagicMock", mock_load_paths: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test successful path validation."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        # Mock paths configuration
        mock_load_paths.return_value = {"test_path": ["Documents", "General", "Reports"]}

        # Mock PathResolver instance
        mock_resolver = Mock()
        mock_path_resolver_class.return_value = mock_resolver
        mock_resolver.validate_path.return_value = (True, "", [])

        client = SharePointClient(config)
        client.connect()

        result = client.validate_paths("Documents")

        assert result == {
            "test_path": {
                "valid": True,
                "path": ["Documents", "General", "Reports"],
                "error": "",
                "available_folders": [],
            }
        }
        mock_path_resolver_class.assert_called_once_with(mock_context, "Documents")
        mock_resolver.validate_path.assert_called_once_with(["General", "Reports"])

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.load_sharepoint_paths")
    @patch("fetchpoint.client.PathResolver")
    def test_validate_paths_failure(
        self, mock_path_resolver_class: "MagicMock", mock_load_paths: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test path validation with failures."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        # Mock paths configuration
        mock_load_paths.return_value = {"invalid_path": ["Documents", "NonExistent"]}

        # Mock PathResolver instance
        mock_resolver = Mock()
        mock_path_resolver_class.return_value = mock_resolver
        mock_resolver.validate_path.return_value = (False, "Folder not found", ["Folder1", "Folder2"])

        client = SharePointClient(config)
        client.connect()

        result = client.validate_paths("Documents")

        assert result == {
            "invalid_path": {
                "valid": False,
                "path": ["Documents", "NonExistent"],
                "error": "Folder not found",
                "available_folders": ["Folder1", "Folder2"],
            }
        }

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.load_sharepoint_paths")
    @patch("fetchpoint.client.PathResolver")
    def test_validate_decoupled_paths_not_connected(
        self, mock_path_resolver: "MagicMock", mock_load_paths: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test validate_decoupled_paths when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.validate_decoupled_paths()

        assert "Not connected to SharePoint" in str(exc_info.value)
        mock_load_paths.assert_not_called()

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.load_sharepoint_paths")
    @patch("fetchpoint.client.PathResolver")
    def test_validate_decoupled_paths_success(
        self, mock_path_resolver_class: "MagicMock", mock_load_paths: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test successful decoupled path validation."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        # Mock paths configuration with different libraries
        mock_load_paths.return_value = {"lib1_path": ["Library1", "Folder1"], "lib2_path": ["Library2", "Folder2"]}

        # Mock PathResolver instance
        mock_resolver = Mock()
        mock_path_resolver_class.return_value = mock_resolver
        mock_resolver.validate_path.return_value = (True, "", [])

        client = SharePointClient(config)
        client.connect()

        result = client.validate_decoupled_paths()

        # Should have results for both paths
        assert len(result) == 2
        assert result["lib1_path"]["valid"] is True
        assert result["lib1_path"]["library"] == "Library1"
        assert result["lib2_path"]["valid"] is True
        assert result["lib2_path"]["library"] == "Library2"

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_folders_in_library")
    @patch("fetchpoint.client.list_files_in_library")
    def test_discover_structure_not_connected(
        self, mock_list_files: "MagicMock", mock_list_folders: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test discover_structure when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.discover_structure()

        assert "Not connected to SharePoint" in str(exc_info.value)
        mock_list_files.assert_not_called()
        mock_list_folders.assert_not_called()

    @patch("fetchpoint.client.create_authenticated_context")
    @patch("fetchpoint.client.list_folders_in_library")
    @patch("fetchpoint.client.list_files_in_library")
    def test_discover_structure_success(
        self, mock_list_files: "MagicMock", mock_list_folders: "MagicMock", mock_create_context: "MagicMock"
    ) -> None:
        """Test successful structure discovery."""
        from fetchpoint.models import FileInfo, FileType

        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        # Mock root level files and folders
        from datetime import datetime

        mock_file = FileInfo(
            name="test.xlsx",
            library="TestLibrary",
            relative_path="test.xlsx",
            size_bytes=1024,
            modified_date=datetime(2024, 1, 1),
            file_type=FileType.XLSX,
        )
        mock_list_files.return_value = [mock_file]
        mock_list_folders.return_value = ["Folder1"]

        client = SharePointClient(config)
        client.connect()

        result = client.discover_structure("TestLibrary", max_depth=1)

        assert result["library"] == "TestLibrary"
        assert result["files"] == ["test.xlsx"]
        assert result["file_count"] == 1
        assert "Folder1" in result["folders"]

        # Should have called list functions for root level
        mock_list_files.assert_called_with(mock_context, "TestLibrary", None)
        mock_list_folders.assert_called_with(mock_context, "TestLibrary", None)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_download_files_not_connected(self, mock_create_context: "MagicMock") -> None:
        """Test download_files when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            client.download_files("Documents", None, ["test.xlsx"], "/tmp")

        assert "Not connected to SharePoint" in str(exc_info.value)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_download_files_no_download_dir(self, mock_create_context: "MagicMock") -> None:
        """Test download_files when download_dir is not provided."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        with pytest.raises(ValueError) as exc_info:
            client.download_files("Documents", None, ["test.xlsx"], "")

        assert "download_dir parameter is required" in str(exc_info.value)

    @patch("fetchpoint.client.create_authenticated_context")
    @patch.dict(os.environ, {"DOWNLOAD_PATH": ""})
    def test_download_files_successful_download(self, mock_create_context: "MagicMock") -> None:
        """Test successful file download."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        # Mock file item
        mock_file_item = Mock()
        mock_file_item.length = 1024  # 1KB file
        mock_file_item.name = "test.xlsx"

        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variable to temp directory
            with patch.dict(os.environ, {"DOWNLOAD_PATH": temp_dir}):
                # Mock _get_file_item to return our mock file
                with patch.object(client, "_get_file_item", return_value=mock_file_item):
                    # Mock the file download
                    def mock_download(file_handle: Any) -> Mock:
                        file_handle.write(b"x" * 1024)  # Write 1KB of data
                        return Mock()

                    mock_file_item.download = Mock(side_effect=mock_download)

                    result = client.download_files("Documents", "General/Reports", ["test.xlsx"], temp_dir)

                    # Verify successful download
                    assert len(result) == 1
                    assert "test.xlsx" in result
                    assert result["test.xlsx"]["success"] is True
                    assert result["test.xlsx"]["size_bytes"] == 1024
                    assert "local_path" in result["test.xlsx"]

                    # Verify file was actually written
                    downloaded_file = Path(result["test.xlsx"]["local_path"])
                    assert downloaded_file.exists()
                    assert downloaded_file.stat().st_size == 1024

    @patch("fetchpoint.client.create_authenticated_context")
    @patch.dict(os.environ, {"DOWNLOAD_PATH": ""})
    def test_download_files_file_not_found(self, mock_create_context: "MagicMock") -> None:
        """Test download when file is not found."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"DOWNLOAD_PATH": temp_dir}):
                # Mock _get_file_item to return None (file not found)
                with patch.object(client, "_get_file_item", return_value=None):
                    result = client.download_files("Documents", None, ["nonexistent.xlsx"], temp_dir)

                    # Verify file not found result
                    assert len(result) == 1
                    assert "nonexistent.xlsx" in result
                    assert result["nonexistent.xlsx"]["success"] is False
                    assert "not found" in result["nonexistent.xlsx"]["error"]

    @patch("fetchpoint.client.create_authenticated_context")
    @patch.dict(os.environ, {"DOWNLOAD_PATH": ""})
    def test_download_files_size_limit_exceeded(self, mock_create_context: "MagicMock") -> None:
        """Test download when file exceeds size limit."""
        config = SharePointAuthConfig(
            username="test@example.com",
            password=SecretStr("password"),
            sharepoint_url="https://example.sharepoint.com",
            max_file_size_mb=1,  # Set 1MB limit
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        # Mock file item with size exceeding limit
        mock_file_item = Mock()
        mock_file_item.length = 2 * 1024 * 1024  # 2MB file
        mock_file_item.name = "large_file.xlsx"

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"DOWNLOAD_PATH": temp_dir}):
                with patch.object(client, "_get_file_item", return_value=mock_file_item):
                    result = client.download_files("Documents", None, ["large_file.xlsx"], temp_dir)

                    # Verify size limit error
                    assert len(result) == 1
                    assert "large_file.xlsx" in result
                    assert result["large_file.xlsx"]["success"] is False
                    assert "exceeds size limit" in result["large_file.xlsx"]["error"]

    @patch("fetchpoint.client.create_authenticated_context")
    @patch.dict(os.environ, {"DOWNLOAD_PATH": ""})
    def test_download_files_multiple_files_mixed_results(self, mock_create_context: "MagicMock") -> None:
        """Test download of multiple files with mixed success/failure results."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        def mock_get_file_item(library_name: str, path_segments: list[str], filename: str):
            if filename == "success.xlsx":
                mock_file = Mock()
                mock_file.length = 1024
                mock_file.name = filename
                return mock_file
            elif filename == "notfound.xlsx":
                return None  # File not found
            elif filename == "error.xlsx":
                # This will cause an exception in the download process
                mock_file = Mock()
                mock_file.length = 1024
                mock_file.name = filename
                return mock_file
            return None

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"DOWNLOAD_PATH": temp_dir}):
                with patch.object(client, "_get_file_item", side_effect=mock_get_file_item):
                    # Mock successful download for success.xlsx
                    def mock_download_success(file_handle: Any) -> Mock:
                        file_handle.write(b"x" * 1024)
                        return Mock()

                    # Mock failed download for error.xlsx
                    def mock_download_error(file_handle: Any) -> None:
                        raise Exception("Network error")

                    # We need to patch the download method differently for each file
                    original_get_file_item = getattr(client, "_get_file_item")  # Access protected method for testing

                    def patched_get_file_item(library_name: str, path_segments: list[str], filename: str) -> Any:
                        file_item = original_get_file_item(library_name, path_segments, filename)
                        if file_item and filename == "success.xlsx":
                            file_item.download = Mock(side_effect=mock_download_success)
                        elif file_item and filename == "error.xlsx":
                            file_item.download = Mock(side_effect=mock_download_error)
                        return file_item

                    with patch.object(client, "_get_file_item", side_effect=patched_get_file_item):
                        result = client.download_files(
                            "Documents", None, ["success.xlsx", "notfound.xlsx", "error.xlsx"], temp_dir
                        )

                        # Verify mixed results
                        assert len(result) == 3

                        # Success case
                        assert result["success.xlsx"]["success"] is True
                        assert result["success.xlsx"]["size_bytes"] == 1024

                        # Not found case
                        assert result["notfound.xlsx"]["success"] is False
                        assert "not found" in result["notfound.xlsx"]["error"]

                        # Error case
                        assert result["error.xlsx"]["success"] is False
                        assert "error" in result["error.xlsx"]["error"].lower()

    @patch("fetchpoint.client.create_authenticated_context")
    @patch.dict(os.environ, {"DOWNLOAD_PATH": ""})
    def test_download_files_permission_error(self, mock_create_context: "MagicMock") -> None:
        """Test download when permission error occurs."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"DOWNLOAD_PATH": temp_dir}):
                # Mock _get_file_item to raise PermissionError
                with patch.object(
                    client, "_get_file_item", side_effect=PermissionError("Access denied", "download_file")
                ):
                    result = client.download_files("Documents", None, ["restricted.xlsx"], temp_dir)

                    # Verify permission error result
                    assert len(result) == 1
                    assert "restricted.xlsx" in result
                    assert result["restricted.xlsx"]["success"] is False
                    assert "Permission denied" in result["restricted.xlsx"]["error"]

    @patch("fetchpoint.client.create_authenticated_context")
    @patch.dict(os.environ, {"DOWNLOAD_PATH": ""})
    def test_download_files_incomplete_download(self, mock_create_context: "MagicMock") -> None:
        """Test download when file is incompletely downloaded."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        client = SharePointClient(config)
        client.connect()

        # Mock file item
        mock_file_item = Mock()
        mock_file_item.length = 1024  # Expected 1KB
        mock_file_item.name = "incomplete.xlsx"

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"DOWNLOAD_PATH": temp_dir}):
                with patch.object(client, "_get_file_item", return_value=mock_file_item):
                    # Mock incomplete download (writes less data than expected)
                    def mock_incomplete_download(file_handle: Any) -> Mock:
                        file_handle.write(b"x" * 512)  # Write only 512 bytes instead of 1024
                        return Mock()

                    mock_file_item.download = Mock(side_effect=mock_incomplete_download)

                    result = client.download_files("Documents", None, ["incomplete.xlsx"], temp_dir)

                    # Verify incomplete download error
                    assert len(result) == 1
                    assert "incomplete.xlsx" in result
                    assert result["incomplete.xlsx"]["success"] is False
                    assert "download incomplete" in result["incomplete.xlsx"]["error"]

                    # Verify incomplete file was cleaned up
                    incomplete_file = Path(temp_dir) / "incomplete.xlsx"
                    assert not incomplete_file.exists()

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_item_not_connected(self, mock_create_context: "MagicMock") -> None:
        """Test _get_file_item when not connected."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        with pytest.raises(ConnectionError) as exc_info:
            getattr(client, "_get_file_item")("Documents", [], "test.xlsx")  # Access protected method for testing

        assert "SharePoint context is not authenticated" in str(exc_info.value)

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_item_successful(self, mock_create_context: "MagicMock") -> None:
        """Test successful _get_file_item operation."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        # Mock library and folder structure
        mock_library = Mock()
        mock_root_folder = Mock()
        mock_library.root_folder = mock_root_folder
        mock_context.web.lists.get_by_title.return_value = mock_library

        # Mock files collection
        mock_file_item = Mock()
        mock_file_item.name = "test.xlsx"
        mock_files_collection = [mock_file_item]
        mock_root_folder.files = mock_files_collection

        client = SharePointClient(config)
        client.connect()

        result = getattr(client, "_get_file_item")("Documents", [], "test.xlsx")  # Access protected method for testing

        assert result is mock_file_item
        mock_context.web.lists.get_by_title.assert_called_with("Documents")

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_item_file_not_found(self, mock_create_context: "MagicMock") -> None:
        """Test _get_file_item when file is not found."""
        config = SharePointAuthConfig(
            username="test@example.com", password=SecretStr("password"), sharepoint_url="https://example.sharepoint.com"
        )
        mock_context = Mock()
        mock_create_context.return_value = mock_context

        # Mock library and folder structure
        mock_library = Mock()
        mock_root_folder = Mock()
        mock_library.root_folder = mock_root_folder
        mock_context.web.lists.get_by_title.return_value = mock_library

        # Mock empty files collection
        mock_files_collection = []
        mock_root_folder.files = mock_files_collection

        client = SharePointClient(config)
        client.connect()

        result = getattr(client, "_get_file_item")(
            "Documents", [], "nonexistent.xlsx"
        )  # Access protected method for testing

        assert result is None
