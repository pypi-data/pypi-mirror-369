"""
Unit tests for Excel-related Pydantic models.

This module tests the ExcelData and ColumnMapping models,
including validation, properties, and methods.
"""

from typing import Any

import pytest

from fetchpoint.models import ColumnMapping, ExcelData


class TestExcelData:
    """Test cases for the ExcelData model."""

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample Excel data for testing."""
        return [
            {"name": "Alice", "age": 25, "city": "New York"},
            {"name": "Bob", "age": 30, "city": "London"},
            {"name": "Charlie", "age": 35, "city": "Tokyo"},
        ]

    @pytest.fixture
    def excel_data(self, sample_data: list[dict[str, Any]]) -> ExcelData:
        """Create ExcelData instance for testing."""
        return ExcelData(
            filename="test.xlsx",
            sheet_name="Sheet1",
            data=sample_data,
            row_count=len(sample_data),
            column_names=["name", "age", "city"],
        )

    def test_excel_data_creation(self, sample_data: list[dict[str, Any]]) -> None:
        """Test basic ExcelData creation."""
        excel_data = ExcelData(
            filename="test.xlsx",
            sheet_name="TestSheet",
            data=sample_data,
            row_count=3,
            column_names=["name", "age", "city"],
        )

        assert excel_data.filename == "test.xlsx"
        assert excel_data.sheet_name == "TestSheet"
        assert len(excel_data.data) == 3
        assert excel_data.row_count == 3
        assert excel_data.column_names == ["name", "age", "city"]
        assert excel_data.empty_rows_skipped == 0  # Default value

    def test_excel_data_with_optional_fields(self, sample_data: list[dict[str, Any]]) -> None:
        """Test ExcelData creation with optional fields."""
        column_mapping = {"Name": "name", "Age": "age"}

        excel_data = ExcelData(
            filename="test.xlsx",
            sheet_name="Sheet1",
            data=sample_data,
            row_count=3,
            column_names=["name", "age", "city"],
            column_mapping_applied=column_mapping,
            empty_rows_skipped=2,
        )

        assert excel_data.column_mapping_applied == column_mapping
        assert excel_data.empty_rows_skipped == 2

    def test_row_count_validation_mismatch(self, sample_data: list[dict[str, Any]]) -> None:
        """Test validation failure when row_count doesn't match data length."""
        with pytest.raises(ValueError, match="Row count 5 doesn't match data length 3"):
            ExcelData(
                filename="test.xlsx",
                sheet_name="Sheet1",
                data=sample_data,
                row_count=5,  # Mismatch with actual data length
                column_names=["name", "age", "city"],
            )

    def test_data_structure_validation(self) -> None:
        """Test validation of data structure."""
        # Test invalid data type
        with pytest.raises(ValueError, match="Data must be a list"):
            ExcelData(
                filename="test.xlsx",
                sheet_name="Sheet1",
                data="not a list",  # type: ignore
                row_count=0,
                column_names=[],
            )

        # Test invalid row type
        with pytest.raises(ValueError, match="Row 1 must be a dictionary"):
            ExcelData(
                filename="test.xlsx",
                sheet_name="Sheet1",
                data=[{"valid": "row"}, "invalid row"],  # type: ignore
                row_count=2,
                column_names=["valid"],
            )

    def test_is_empty_property(self) -> None:
        """Test the is_empty property."""
        # Empty data
        empty_excel = ExcelData(
            filename="empty.xlsx", sheet_name="Sheet1", data=[], row_count=0, column_names=["col1", "col2"]
        )
        assert empty_excel.is_empty is True

        # Non-empty data
        non_empty_excel = ExcelData(
            filename="data.xlsx", sheet_name="Sheet1", data=[{"col1": "value"}], row_count=1, column_names=["col1"]
        )
        assert non_empty_excel.is_empty is False

    def test_column_count_property(self, excel_data: ExcelData) -> None:
        """Test the column_count property."""
        assert excel_data.column_count == 3

    def test_get_column_data(self, excel_data: ExcelData) -> None:
        """Test getting data for a specific column."""
        names = excel_data.get_column_data("name")
        assert names == ["Alice", "Bob", "Charlie"]

        ages = excel_data.get_column_data("age")
        assert ages == [25, 30, 35]

    def test_get_column_data_invalid_column(self, excel_data: ExcelData) -> None:
        """Test error handling for invalid column name."""
        with pytest.raises(ValueError, match="Column 'invalid_col' not found in data"):
            excel_data.get_column_data("invalid_col")

    def test_filter_rows(self, excel_data: ExcelData) -> None:
        """Test filtering rows with a condition."""
        # Filter for age >= 30
        filtered = excel_data.filter_rows(lambda row: row.get("age", 0) >= 30)

        assert isinstance(filtered, ExcelData)
        assert filtered.row_count == 2
        assert len(filtered.data) == 2
        assert filtered.data[0]["name"] == "Bob"
        assert filtered.data[1]["name"] == "Charlie"
        assert filtered.filename == excel_data.filename
        assert filtered.sheet_name == excel_data.sheet_name
        assert filtered.column_names == excel_data.column_names

    def test_filter_rows_empty_result(self, excel_data: ExcelData) -> None:
        """Test filtering that results in empty data."""
        # Filter for impossible condition
        filtered = excel_data.filter_rows(lambda row: row.get("age", 0) > 100)

        assert filtered.row_count == 0
        assert filtered.is_empty is True
        assert len(filtered.data) == 0


class TestColumnMapping:
    """Test cases for the ColumnMapping model."""

    def test_column_mapping_creation(self) -> None:
        """Test basic ColumnMapping creation."""
        mappings = {"Original Name": "mapped_name", "Another Col": "another_col"}

        column_mapping = ColumnMapping(mappings=mappings)

        assert column_mapping.mappings == mappings
        assert column_mapping.case_sensitive is True  # Default value
        assert column_mapping.ignore_missing is True  # Default value

    def test_column_mapping_with_options(self) -> None:
        """Test ColumnMapping creation with optional parameters."""
        mappings = {"Name": "name"}

        column_mapping = ColumnMapping(mappings=mappings, case_sensitive=False, ignore_missing=False)

        assert column_mapping.case_sensitive is False
        assert column_mapping.ignore_missing is False

    def test_mappings_validation_invalid_type(self) -> None:
        """Test validation failure for invalid mappings type."""
        with pytest.raises(ValueError, match="Mappings must be a dictionary"):
            ColumnMapping(mappings="not a dict")  # type: ignore

    def test_mappings_validation_invalid_keys_values(self) -> None:
        """Test validation failure for invalid key/value types."""
        with pytest.raises(ValueError, match="Both original and mapped column names must be strings"):
            ColumnMapping(mappings={123: "mapped"})  # type: ignore

        with pytest.raises(ValueError, match="Both original and mapped column names must be strings"):
            ColumnMapping(mappings={"original": 456})  # type: ignore

    def test_mappings_validation_empty_strings(self) -> None:
        """Test validation failure for empty or whitespace-only strings."""
        with pytest.raises(ValueError, match="Column names cannot be empty or whitespace-only"):
            ColumnMapping(mappings={"": "mapped"})

        with pytest.raises(ValueError, match="Column names cannot be empty or whitespace-only"):
            ColumnMapping(mappings={"original": "  "})

    def test_apply_to_columns_case_sensitive(self) -> None:
        """Test applying mapping with case-sensitive matching."""
        column_mapping = ColumnMapping(
            mappings={"Name": "name", "Age": "age", "NotFound": "not_found"}, case_sensitive=True, ignore_missing=True
        )

        available_columns = ["Name", "Age", "City"]
        result = column_mapping.apply_to_columns(available_columns)

        expected = {"Name": "name", "Age": "age"}
        assert result == expected

    def test_apply_to_columns_case_insensitive(self) -> None:
        """Test applying mapping with case-insensitive matching."""
        column_mapping = ColumnMapping(
            mappings={"name": "mapped_name", "AGE": "mapped_age"}, case_sensitive=False, ignore_missing=True
        )

        available_columns = ["Name", "Age", "City"]
        result = column_mapping.apply_to_columns(available_columns)

        expected = {"Name": "mapped_name", "Age": "mapped_age"}
        assert result == expected

    def test_apply_to_columns_ignore_missing_false(self) -> None:
        """Test error when ignore_missing=False and columns are missing."""
        column_mapping = ColumnMapping(mappings={"Name": "name", "NotFound": "not_found"}, ignore_missing=False)

        available_columns = ["Name", "Age"]

        with pytest.raises(ValueError, match="Mapping columns not found: NotFound"):
            column_mapping.apply_to_columns(available_columns)

    def test_apply_to_columns_ignore_missing_true(self) -> None:
        """Test successful application when ignore_missing=True."""
        column_mapping = ColumnMapping(mappings={"Name": "name", "NotFound": "not_found"}, ignore_missing=True)

        available_columns = ["Name", "Age"]
        result = column_mapping.apply_to_columns(available_columns)

        # Should only include mappings for existing columns
        expected = {"Name": "name"}
        assert result == expected

    def test_mapping_count_property(self) -> None:
        """Test the mapping_count property."""
        mappings = {"Col1": "col1", "Col2": "col2", "Col3": "col3"}
        column_mapping = ColumnMapping(mappings=mappings)

        assert column_mapping.mapping_count == 3

    def test_empty_mappings(self) -> None:
        """Test ColumnMapping with empty mappings dictionary."""
        column_mapping = ColumnMapping(mappings={})

        assert column_mapping.mapping_count == 0

        # Should return empty dict for any columns
        result = column_mapping.apply_to_columns(["Col1", "Col2"])
        assert result == {}

    def test_partial_mapping_application(self) -> None:
        """Test applying mapping where only some columns match."""
        column_mapping = ColumnMapping(
            mappings={"Found1": "mapped1", "NotFound": "mapped_not_found", "Found2": "mapped2"}, ignore_missing=True
        )

        available_columns = ["Found1", "Found2", "OtherCol"]
        result = column_mapping.apply_to_columns(available_columns)

        expected = {"Found1": "mapped1", "Found2": "mapped2"}
        assert result == expected

    def test_duplicate_mappings_edge_case(self) -> None:
        """Test edge case with duplicate target names."""
        # This should be allowed at model level, but users should be careful
        mappings = {"Col1": "same_name", "Col2": "same_name"}
        column_mapping = ColumnMapping(mappings=mappings)

        # Should create the mapping without error
        assert column_mapping.mapping_count == 2

        available_columns = ["Col1", "Col2"]
        result = column_mapping.apply_to_columns(available_columns)

        # Both mappings should be returned
        expected = {"Col1": "same_name", "Col2": "same_name"}
        assert result == expected
