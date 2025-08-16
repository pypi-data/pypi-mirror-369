"""
Unit tests for SharePointClient Excel functionality.

This module tests the Excel reading methods in SharePointClient,
including get_file_content, read_excel_content, and get_excel_sheet_names
using mocked SharePoint operations.
"""

import io
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from fetchpoint.client import SharePointClient
from fetchpoint.exceptions import ConnectionError, FileDownloadError, FileNotFoundError, FileSizeLimitError
from fetchpoint.models import SharePointAuthConfig


class TestSharePointClientExcel:
    """Test cases for SharePointClient Excel functionality."""

    @pytest.fixture
    def mock_config(self) -> SharePointAuthConfig:
        """Create mock SharePointAuthConfig for testing."""
        from pydantic import SecretStr

        return SharePointAuthConfig(
            username="test@example.com",
            password=SecretStr("password123"),
            sharepoint_url="https://test.sharepoint.com",
            max_file_size_mb=50,
        )

    @pytest.fixture
    def sample_excel_bytes(self) -> bytes:
        """Create sample Excel file bytes for testing."""
        test_data = {"Name": ["Alice", "Bob", "Charlie"], "Age": [25, 30, 35], "Department": ["IT", "HR", "Finance"]}
        df = pd.DataFrame(test_data)

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Employees", index=False)  # type: ignore[misc]

        return excel_buffer.getvalue()

    @pytest.fixture
    def multi_sheet_excel_bytes(self) -> bytes:
        """Create Excel file bytes with multiple sheets."""
        sheet1_data = {"Product": ["A", "B"], "Price": [100, 200]}
        sheet2_data = {"Employee": ["John", "Jane"], "Salary": [50000, 60000]}

        df1 = pd.DataFrame(sheet1_data)
        df2 = pd.DataFrame(sheet2_data)

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="Products", index=False)  # type: ignore[misc]
            df2.to_excel(writer, sheet_name="Employees", index=False)  # type: ignore[misc]

        return excel_buffer.getvalue()

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_content_success(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig, sample_excel_bytes: bytes
    ) -> None:
        """Test successful file content retrieval."""
        # Setup mocks
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        mock_file_item = MagicMock()
        mock_file_item.Length = len(sample_excel_bytes)

        # Mock get_content() result
        mock_content_result = MagicMock()
        mock_content_result.value = sample_excel_bytes
        mock_file_item.get_content.return_value = mock_content_result

        client = SharePointClient(mock_config)

        # Mock the connection state and _get_file_item method
        client._is_connected = True  # type: ignore[misc]  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]  # type: ignore[misc]

        with patch.object(client, "_get_file_item", return_value=mock_file_item):
            result = client.get_file_content(library="Documents", path=["folder", "test.xlsx"])

        assert result == sample_excel_bytes
        mock_file_item.get_content.assert_called_once()

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_content_not_connected(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error when client is not connected."""
        client = SharePointClient(mock_config)
        client._is_connected = False  # type: ignore[misc]

        with pytest.raises(ConnectionError, match="Not connected to SharePoint"):
            client.get_file_content(library="Documents", path=["folder", "test.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_content_file_not_found(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error when file is not found."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        with patch.object(client, "_get_file_item", return_value=None):
            with pytest.raises(FileNotFoundError, match="File not found: folder/test.xlsx"):
                client.get_file_content(library="Documents", path=["folder", "test.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_content_size_limit_exceeded(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig
    ) -> None:
        """Test error when file exceeds size limit."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        mock_file_item = MagicMock()
        # Set file size larger than limit (50MB)
        mock_file_item.Length = 60 * 1024 * 1024  # 60MB

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        with patch.object(client, "_get_file_item", return_value=mock_file_item):
            with pytest.raises(FileSizeLimitError, match="File size 60.0MB exceeds limit of 50MB"):
                client.get_file_content(library="Documents", path=["folder", "large_file.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_file_content_empty_content(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error when file content is empty."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        mock_file_item = MagicMock()
        mock_file_item.Length = 100

        # Mock empty content
        mock_content_result = MagicMock()
        mock_content_result.value = b""  # Empty bytes
        mock_file_item.get_content.return_value = mock_content_result

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        with patch.object(client, "_get_file_item", return_value=mock_file_item):
            with pytest.raises(FileDownloadError, match="File content is empty"):
                client.get_file_content(library="Documents", path=["folder", "empty.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_read_excel_content_success(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig, sample_excel_bytes: bytes
    ) -> None:
        """Test successful Excel content reading."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        # Mock get_file_content to return sample Excel bytes
        with patch.object(client, "get_file_content", return_value=sample_excel_bytes):
            result = client.read_excel_content(library="Documents", path=["data", "employees.xlsx"])

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["Name"] == "Alice"
        assert result[0]["Age"] == 25
        assert result[0]["Department"] == "IT"

    @patch("fetchpoint.client.create_authenticated_context")
    def test_read_excel_content_with_column_mapping(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig, sample_excel_bytes: bytes
    ) -> None:
        """Test Excel content reading with column mapping."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        column_mapping = {"Name": "employee_name", "Age": "employee_age"}

        with patch.object(client, "get_file_content", return_value=sample_excel_bytes):
            result = client.read_excel_content(
                library="Documents", path=["data", "employees.xlsx"], column_mapping=column_mapping
            )

        assert len(result) == 3
        assert "employee_name" in result[0]
        assert "employee_age" in result[0]
        assert "Department" in result[0]  # Unmapped column should remain
        assert result[0]["employee_name"] == "Alice"

    @patch("fetchpoint.client.create_authenticated_context")
    def test_read_excel_content_specific_sheet(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig, multi_sheet_excel_bytes: bytes
    ) -> None:
        """Test Excel content reading from specific sheet."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        with patch.object(client, "get_file_content", return_value=multi_sheet_excel_bytes):
            result = client.read_excel_content(
                library="Documents", path=["data", "multi_sheet.xlsx"], sheet_name="Employees"
            )

        assert len(result) == 2
        assert "Employee" in result[0]
        assert "Salary" in result[0]
        assert result[0]["Employee"] == "John"
        assert result[0]["Salary"] == 50000

    @patch("fetchpoint.client.create_authenticated_context")
    def test_read_excel_content_invalid_excel(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error handling for invalid Excel content."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        # Return invalid Excel bytes
        invalid_bytes = b"not excel content"

        with patch.object(client, "get_file_content", return_value=invalid_bytes):
            with pytest.raises(ValueError, match="Error processing Excel file"):
                client.read_excel_content(library="Documents", path=["data", "invalid.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_excel_sheet_names_success(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig, multi_sheet_excel_bytes: bytes
    ) -> None:
        """Test successful sheet name retrieval."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        with patch.object(client, "get_file_content", return_value=multi_sheet_excel_bytes):
            result = client.get_excel_sheet_names(library="Documents", path=["data", "workbook.xlsx"])

        assert isinstance(result, list)
        assert len(result) == 2
        assert "Products" in result
        assert "Employees" in result

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_excel_sheet_names_invalid_excel(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error handling for invalid Excel when getting sheet names."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        invalid_bytes = b"not excel content"

        with patch.object(client, "get_file_content", return_value=invalid_bytes):
            with pytest.raises(ValueError, match="Error reading Excel file sheets"):
                client.get_excel_sheet_names(library="Documents", path=["data", "invalid.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_read_excel_content_not_connected(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error when client is not connected during Excel reading."""
        client = SharePointClient(mock_config)
        client._is_connected = False  # type: ignore[misc]

        with pytest.raises(ConnectionError, match="Not connected to SharePoint"):
            client.read_excel_content(library="Documents", path=["data", "test.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_get_excel_sheet_names_not_connected(self, mock_auth: MagicMock, mock_config: SharePointAuthConfig) -> None:
        """Test error when client is not connected during sheet name retrieval."""
        client = SharePointClient(mock_config)
        client._is_connected = False  # type: ignore[misc]

        with pytest.raises(ConnectionError, match="Not connected to SharePoint"):
            client.get_excel_sheet_names(library="Documents", path=["data", "test.xlsx"])

    @patch("fetchpoint.client.create_authenticated_context")
    def test_read_excel_content_with_all_options(
        self, mock_auth: MagicMock, mock_config: SharePointAuthConfig, sample_excel_bytes: bytes
    ) -> None:
        """Test Excel content reading with all optional parameters."""
        mock_context = MagicMock()
        mock_auth.return_value = mock_context

        client = SharePointClient(mock_config)
        client._is_connected = True  # type: ignore[misc]
        client._context = mock_context  # type: ignore[misc]

        column_mapping = {"Name": "full_name"}

        with patch.object(client, "get_file_content", return_value=sample_excel_bytes):
            result = client.read_excel_content(
                library="Documents",
                path=["data", "employees.xlsx"],
                sheet_name="Employees",  # Specific sheet
                column_mapping=column_mapping,
                skip_empty_rows=False,  # Don't skip empty rows
            )

        assert len(result) == 3
        assert "full_name" in result[0]
        assert result[0]["full_name"] == "Alice"
