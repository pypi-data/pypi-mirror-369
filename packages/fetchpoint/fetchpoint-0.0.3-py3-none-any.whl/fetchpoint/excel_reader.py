"""
Generic Excel data reader for SharePoint files.

This module provides functionality for reading Excel files directly from SharePoint
without downloading them to disk. It supports reading generic tabular data from Excel
files (.xlsx, .xls, .xlsm, .xlsb) and converting it to JSON-compatible data structures.

Features:
    - Read Excel files from bytes (in-memory)
    - Support for specific sheet selection
    - Column name mapping (rename columns)
    - Generic implementation (no hardcoded field names)
    - Proper null/NaN handling
    - Memory-efficient processing

Usage:
    from fetchpoint.excel_reader import ExcelReader

    reader = ExcelReader()
    data = reader.read_from_bytes(excel_bytes)  # Returns list[dict]

    # With column mapping
    mapping = {"Old Name": "new_name", "Another": "mapped_name"}
    data = reader.read_from_bytes(excel_bytes, column_mapping=mapping)

Requirements:
    - pandas (with openpyxl engine) for Excel file reading
    - Python 3.10+ for type hints support
"""

import logging
from io import BytesIO
from typing import Any, Optional

import pandas as pd

# Configure logger for this module
logger = logging.getLogger(__name__)


class ExcelReader:
    """
    Generic Excel data reader for processing Excel files from SharePoint.

    This class provides methods to read Excel files directly from bytes without
    requiring local file storage. It supports sheet selection, column mapping,
    and returns data as JSON-compatible structures.

    The reader is completely generic and doesn't contain any domain-specific
    logic or hardcoded field names.
    """

    def __init__(self) -> None:
        """
        Initialize the Excel reader.

        The reader is stateless and ready to use immediately.
        No configuration is required for basic functionality.
        """
        pass

    def read_from_bytes(
        self,
        content: bytes,
        sheet_name: Optional[str] = None,
        column_mapping: Optional[dict[str, str]] = None,
        skip_empty_rows: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Read Excel data from bytes and return as list of dictionaries.

        This method processes Excel content directly from memory, converts it to
        a DataFrame, and returns it as a list of dictionaries suitable for JSON
        serialization or further processing.

        Args:
            content: Raw Excel file bytes
            sheet_name: Name of the sheet to read. If None, reads the first sheet.
            column_mapping: Optional dictionary to rename columns
                          {"original_name": "new_name"}
            skip_empty_rows: Whether to skip rows where all values are empty/null

        Returns:
            List of dictionaries, where each dict represents a row with
            column names as keys and cell values as values.

        Raises:
            ValueError: If content is empty, invalid, or sheet not found
            Exception: If Excel reading fails

        Example:
            >>> reader = ExcelReader()
            >>> data = reader.read_from_bytes(excel_bytes)
            >>> print(data[0])  # First row as dict
            {'Name': 'John', 'Age': 30, 'City': 'New York'}
        """
        if not content:
            raise ValueError("Excel content cannot be empty")

        logger.debug("Reading Excel data from %d bytes", len(content))

        try:
            # Create BytesIO stream from content
            excel_stream = BytesIO(content)

            # Read Excel file using pandas with openpyxl engine
            df = pd.read_excel(excel_stream, sheet_name=sheet_name, engine="openpyxl")  # type: ignore[misc]

            # Handle case where sheet_name=None returns dict of all sheets
            if isinstance(df, dict):
                if sheet_name is None:
                    # Get first sheet
                    first_sheet_name = list(df.keys())[0]
                    df = df[first_sheet_name]
                    logger.debug("Using first sheet: %s", first_sheet_name)
                else:
                    raise ValueError(f"Unexpected dict result for sheet_name='{sheet_name}'")

            # Check if DataFrame is empty
            if df.empty:
                logger.warning("Excel sheet is empty")
                return []

            logger.debug("Read Excel with %d rows and %d columns", len(df), len(df.columns))

            # Apply column mapping if provided
            if column_mapping:
                df = self._apply_column_mapping(df, column_mapping)

            # Convert DataFrame to list of dictionaries
            data = self._dataframe_to_dict_list(df, skip_empty_rows=skip_empty_rows)

            logger.info("Successfully processed %d rows from Excel", len(data))
            return data

        except Exception as e:
            logger.error("Failed to read Excel data: %s", e)
            raise ValueError(f"Error reading Excel content: {str(e)}") from e

    def get_sheet_names_from_bytes(self, content: bytes) -> list[str]:
        """
        Get list of all sheet names from Excel bytes.

        This method extracts all sheet names from Excel content without
        loading the actual data, which can be useful for sheet selection.

        Args:
            content: Raw Excel file bytes

        Returns:
            List of sheet names in the Excel file

        Raises:
            ValueError: If content is empty or invalid
            Exception: If Excel reading fails

        Example:
            >>> reader = ExcelReader()
            >>> sheets = reader.get_sheet_names_from_bytes(excel_bytes)
            >>> print(sheets)
            ['Sheet1', 'Summary', 'Details']
        """
        if not content:
            raise ValueError("Excel content cannot be empty")

        try:
            # Create BytesIO stream from content
            excel_stream = BytesIO(content)

            # Use ExcelFile to get sheet names without loading data
            with pd.ExcelFile(excel_stream, engine="openpyxl") as excel_file:
                sheet_names = [str(name) for name in excel_file.sheet_names]
                logger.debug("Found %d sheets: %s", len(sheet_names), sheet_names)
                return sheet_names

        except Exception as e:
            logger.error("Failed to get sheet names: %s", e)
            raise ValueError(f"Error reading Excel sheets: {str(e)}") from e

    def _apply_column_mapping(self, df: pd.DataFrame, column_mapping: dict[str, str]) -> pd.DataFrame:
        """
        Apply column name mapping to DataFrame.

        Renames columns according to the provided mapping dictionary.
        Columns not in the mapping are left unchanged.

        Args:
            df: Input DataFrame
            column_mapping: Dictionary mapping old column names to new names

        Returns:
            DataFrame with renamed columns
        """
        # Only rename columns that exist in the DataFrame
        valid_mapping = {old_name: new_name for old_name, new_name in column_mapping.items() if old_name in df.columns}

        if valid_mapping:
            df = df.rename(columns=valid_mapping)
            logger.debug("Applied column mapping for %d columns", len(valid_mapping))
        else:
            logger.debug("No valid column mappings found")

        return df

    def _dataframe_to_dict_list(self, df: pd.DataFrame, skip_empty_rows: bool = True) -> list[dict[str, Any]]:
        """
        Convert pandas DataFrame to list of dictionaries with proper null handling.

        Args:
            df: Input DataFrame
            skip_empty_rows: Whether to skip rows where all values are null/empty

        Returns:
            List of dictionaries representing the DataFrame rows
        """
        data_list: list[dict[str, Any]] = []

        for index, row in df.iterrows():
            # Convert row to dictionary
            row_dict: dict[str, Any] = {}

            for column in df.columns:
                value = row[column]

                # Handle pandas NaN values - convert to None for JSON compatibility
                if pd.isna(value):
                    row_dict[column] = None
                else:
                    # Keep native Python types (int, float, str, datetime, etc.)
                    row_dict[column] = value

            # Skip empty rows if requested
            if skip_empty_rows and self._is_row_empty(row_dict):
                logger.debug("Skipping empty row at index %d", index)
                continue

            data_list.append(row_dict)  # type: ignore[misc]

        return data_list

    def _is_row_empty(self, row_dict: dict[str, Any]) -> bool:
        """
        Check if a row dictionary contains only null/empty values.

        Args:
            row_dict: Dictionary representing a row

        Returns:
            True if all values are None, empty strings, or whitespace-only strings
        """
        for value in row_dict.values():
            if value is not None:
                # Check if it's a non-empty string
                if isinstance(value, str):
                    if value.strip():  # Non-empty after stripping whitespace
                        return False
                else:
                    # Non-string, non-None value
                    return False

        # All values were None or empty strings
        return True
