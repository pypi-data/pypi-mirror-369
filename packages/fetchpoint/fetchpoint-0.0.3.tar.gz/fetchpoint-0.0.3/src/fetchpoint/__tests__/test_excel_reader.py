"""
Unit tests for the ExcelReader module.

This module tests the generic Excel reading functionality, including
reading Excel files from bytes, sheet selection, column mapping,
and error handling scenarios.
"""

import io

import pandas as pd
import pytest

from fetchpoint.excel_reader import ExcelReader


class TestExcelReader:
    """Test cases for the ExcelReader class."""

    @pytest.fixture
    def sample_excel_bytes(self) -> bytes:
        """
        Create sample Excel file bytes for testing.

        Returns:
            Bytes representing a simple Excel file with test data
        """
        # Create a simple DataFrame with test data
        import numpy as np

        test_data = {
            "Name": ["Alice", "Bob", "Charlie", None],
            "Age": [25, 30, 35, np.nan],  # Use np.nan instead of None for numeric columns
            "City": ["New York", "London", "Tokyo", ""],
            "Salary": [50000.0, 60000.0, 70000.0, np.nan],  # Use np.nan for numeric columns
        }
        df = pd.DataFrame(test_data)

        # Convert to Excel bytes
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TestSheet", index=False)  # type: ignore[misc]

        return excel_buffer.getvalue()

    @pytest.fixture
    def multi_sheet_excel_bytes(self) -> bytes:
        """
        Create Excel file bytes with multiple sheets for testing.

        Returns:
            Bytes representing an Excel file with multiple sheets
        """
        # Create test data for multiple sheets
        sheet1_data = {"Column1": ["A1", "A2"], "Column2": [1, 2]}
        sheet2_data = {"ColumnX": ["X1", "X2"], "ColumnY": [10, 20]}

        df1 = pd.DataFrame(sheet1_data)
        df2 = pd.DataFrame(sheet2_data)

        # Convert to Excel bytes with multiple sheets
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df1.to_excel(writer, sheet_name="Sheet1", index=False)  # type: ignore[misc]
            df2.to_excel(writer, sheet_name="Sheet2", index=False)  # type: ignore[misc]

        return excel_buffer.getvalue()

    @pytest.fixture
    def excel_reader(self) -> ExcelReader:
        """Create ExcelReader instance for testing."""
        return ExcelReader()

    def test_reader_initialization(self, excel_reader: ExcelReader) -> None:
        """Test that ExcelReader initializes correctly."""
        assert excel_reader is not None
        assert isinstance(excel_reader, ExcelReader)

    def test_read_from_bytes_basic(self, excel_reader: ExcelReader, sample_excel_bytes: bytes) -> None:
        """Test basic Excel reading from bytes."""
        result = excel_reader.read_from_bytes(sample_excel_bytes)

        assert isinstance(result, list)
        assert len(result) == 3  # Should skip the row with all None/empty values

        # Check first row
        first_row = result[0]
        assert first_row["Name"] == "Alice"
        assert first_row["Age"] == 25
        assert first_row["City"] == "New York"
        assert first_row["Salary"] == 50000.0

    def test_read_from_bytes_with_nulls(self, excel_reader: ExcelReader) -> None:
        """Test that null values are handled correctly."""
        # Create Excel with explicit null values that won't be dropped by pandas
        import numpy as np

        test_data = {
            "Name": ["Alice", "Bob", None],  # Mix of values and None
            "Age": [25, np.nan, 35],  # Mix with NaN
            "City": ["New York", "", "Tokyo"],  # Mix with empty string
            "Salary": [50000.0, 60000.0, np.nan],  # Mix with NaN
        }
        df = pd.DataFrame(test_data)

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TestSheet", index=False)  # type: ignore[misc]

        result = excel_reader.read_from_bytes(excel_buffer.getvalue(), skip_empty_rows=False)

        # Should have 3 rows (none are completely empty)
        assert len(result) == 3

        # Check that null values are converted to None
        first_row = result[0]
        assert first_row["Name"] == "Alice"
        assert first_row["Age"] == 25

        second_row = result[1]
        assert second_row["Name"] == "Bob"
        assert second_row["Age"] is None  # NaN becomes None
        assert second_row["City"] is None  # Empty string becomes NaN in Excel, then None

        third_row = result[2]
        assert third_row["Name"] is None  # None remains None
        assert third_row["Salary"] is None  # NaN becomes None

    def test_read_from_bytes_with_column_mapping(self, excel_reader: ExcelReader, sample_excel_bytes: bytes) -> None:
        """Test column name mapping functionality."""
        column_mapping = {"Name": "employee_name", "Age": "employee_age", "Salary": "annual_salary"}

        result = excel_reader.read_from_bytes(sample_excel_bytes, column_mapping=column_mapping)

        assert len(result) == 3

        # Check that column names were mapped correctly
        first_row = result[0]
        assert "employee_name" in first_row
        assert "employee_age" in first_row
        assert "annual_salary" in first_row
        assert "City" in first_row  # Unmapped column should remain unchanged

        assert first_row["employee_name"] == "Alice"
        assert first_row["employee_age"] == 25
        assert first_row["annual_salary"] == 50000.0

    def test_read_from_bytes_skip_empty_rows(self, excel_reader: ExcelReader) -> None:
        """Test skipping of empty rows."""
        # Create Excel with empty rows
        test_data = {"Col1": ["A", None, "C"], "Col2": [1, None, 3], "Col3": ["X", None, "Z"]}
        df = pd.DataFrame(test_data)

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="TestSheet", index=False)  # type: ignore[misc]

        # Test with skip_empty_rows=True (default)
        result_skip = excel_reader.read_from_bytes(excel_buffer.getvalue(), skip_empty_rows=True)
        assert len(result_skip) == 2  # Should skip the middle empty row

        # Test with skip_empty_rows=False
        result_no_skip = excel_reader.read_from_bytes(excel_buffer.getvalue(), skip_empty_rows=False)
        assert len(result_no_skip) == 3  # Should include the empty row

    def test_read_specific_sheet(self, excel_reader: ExcelReader, multi_sheet_excel_bytes: bytes) -> None:
        """Test reading a specific sheet by name."""
        result = excel_reader.read_from_bytes(multi_sheet_excel_bytes, sheet_name="Sheet2")

        assert len(result) == 2
        assert "ColumnX" in result[0]
        assert "ColumnY" in result[0]
        assert result[0]["ColumnX"] == "X1"
        assert result[0]["ColumnY"] == 10

    def test_get_sheet_names_from_bytes(self, excel_reader: ExcelReader, multi_sheet_excel_bytes: bytes) -> None:
        """Test getting sheet names from Excel bytes."""
        sheet_names = excel_reader.get_sheet_names_from_bytes(multi_sheet_excel_bytes)

        assert isinstance(sheet_names, list)
        assert len(sheet_names) == 2
        assert "Sheet1" in sheet_names
        assert "Sheet2" in sheet_names

    def test_read_from_bytes_empty_content(self, excel_reader: ExcelReader) -> None:
        """Test error handling for empty content."""
        with pytest.raises(ValueError, match="Excel content cannot be empty"):
            excel_reader.read_from_bytes(b"")

    def test_read_from_bytes_invalid_content(self, excel_reader: ExcelReader) -> None:
        """Test error handling for invalid Excel content."""
        with pytest.raises(ValueError, match="Error reading Excel content"):
            excel_reader.read_from_bytes(b"not excel content")

    def test_get_sheet_names_empty_content(self, excel_reader: ExcelReader) -> None:
        """Test error handling for empty content when getting sheet names."""
        with pytest.raises(ValueError, match="Excel content cannot be empty"):
            excel_reader.get_sheet_names_from_bytes(b"")

    def test_get_sheet_names_invalid_content(self, excel_reader: ExcelReader) -> None:
        """Test error handling for invalid Excel content when getting sheet names."""
        with pytest.raises(ValueError, match="Error reading Excel sheets"):
            excel_reader.get_sheet_names_from_bytes(b"not excel content")

    def test_read_nonexistent_sheet(self, excel_reader: ExcelReader, sample_excel_bytes: bytes) -> None:
        """Test error handling for non-existent sheet name."""
        with pytest.raises(ValueError, match="Error reading Excel content"):
            excel_reader.read_from_bytes(sample_excel_bytes, sheet_name="NonExistentSheet")

    def test_empty_excel_file(self, excel_reader: ExcelReader) -> None:
        """Test handling of Excel file with no data."""
        # Create Excel with no data rows (just headers)
        df = pd.DataFrame(columns=["Header1", "Header2"])

        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="EmptySheet", index=False)  # type: ignore[misc]

        result = excel_reader.read_from_bytes(excel_buffer.getvalue())
        assert result == []  # Should return empty list for empty Excel

    def test_column_mapping_with_missing_columns(self, excel_reader: ExcelReader, sample_excel_bytes: bytes) -> None:
        """Test column mapping with non-existent columns."""
        column_mapping = {
            "Name": "employee_name",
            "NonExistentColumn": "mapped_name",  # This column doesn't exist
            "Age": "employee_age",
        }

        # Should work fine and ignore non-existent columns
        result = excel_reader.read_from_bytes(sample_excel_bytes, column_mapping=column_mapping)

        assert len(result) == 3
        assert "employee_name" in result[0]
        assert "employee_age" in result[0]
        assert "mapped_name" not in result[0]  # Non-existent mapping ignored

    def test_apply_column_mapping_method(self, excel_reader: ExcelReader) -> None:
        """Test the _apply_column_mapping method directly."""
        # Create a DataFrame with test data
        df = pd.DataFrame({"OriginalCol1": [1, 2, 3], "OriginalCol2": ["A", "B", "C"], "KeepSame": [10, 20, 30]})

        column_mapping = {"OriginalCol1": "MappedCol1", "OriginalCol2": "MappedCol2"}

        result_df = excel_reader._apply_column_mapping(df, column_mapping)  # type: ignore[misc]

        # Check that columns were renamed correctly
        assert "MappedCol1" in result_df.columns
        assert "MappedCol2" in result_df.columns
        assert "KeepSame" in result_df.columns
        assert "OriginalCol1" not in result_df.columns
        assert "OriginalCol2" not in result_df.columns

    def test_is_row_empty_method(self, excel_reader: ExcelReader) -> None:
        """Test the _is_row_empty method directly."""
        # Test completely empty row
        empty_row = {"col1": None, "col2": None, "col3": ""}
        assert excel_reader._is_row_empty(empty_row) is True  # type: ignore[misc]

        # Test row with whitespace only
        whitespace_row = {"col1": None, "col2": "  ", "col3": "\t"}
        assert excel_reader._is_row_empty(whitespace_row) is True  # type: ignore[misc]

        # Test row with actual data
        data_row = {"col1": None, "col2": "", "col3": "actual_data"}
        assert excel_reader._is_row_empty(data_row) is False  # type: ignore[misc]

        # Test row with numeric data
        numeric_row = {"col1": None, "col2": "", "col3": 0}
        assert excel_reader._is_row_empty(numeric_row) is False  # type: ignore[misc]

    def test_dataframe_to_dict_list_method(self, excel_reader: ExcelReader) -> None:
        """Test the _dataframe_to_dict_list method directly."""
        import numpy as np

        # Create test DataFrame with various data types
        df = pd.DataFrame(
            {"StringCol": ["text", None, ""], "NumCol": [42, np.nan, 0], "FloatCol": [3.14, np.nan, 2.71]}
        )

        result = excel_reader._dataframe_to_dict_list(df, skip_empty_rows=True)  # type: ignore[misc]

        # Should skip the row where all values are None/empty/NaN
        assert len(result) == 2  # First and third rows

        # Check data types are preserved
        assert result[0]["StringCol"] == "text"
        assert result[0]["NumCol"] == 42
        assert result[0]["FloatCol"] == 3.14

        # Check None conversion
        assert result[1]["StringCol"] == ""  # Empty string remains empty
        assert result[1]["NumCol"] == 0  # Zero remains zero
        assert result[1]["FloatCol"] == 2.71  # Third row, not second
