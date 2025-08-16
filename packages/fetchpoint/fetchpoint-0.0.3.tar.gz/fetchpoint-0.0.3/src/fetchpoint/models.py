"""
Pydantic v2 data models for SharePoint Reader component.

This module contains all data models used for configuration validation,
file metadata, and data transfer objects in the SharePoint Reader.
"""

import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional, Union

from pydantic import BaseModel, Field, SecretStr, field_validator, model_validator


class FileType(str, Enum):
    """Supported Excel file extensions for SharePoint operations."""

    XLSX = ".xlsx"  # Excel 2007+ format
    XLS = ".xls"  # Legacy Excel format
    XLSM = ".xlsm"  # Excel with macros
    XLSB = ".xlsb"  # Excel binary format

    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value


class SharePointAuthConfig(BaseModel):
    """
    Configuration model for SharePoint authentication.

    Validates user credentials and SharePoint connection parameters.
    Supports any valid email domain for flexible authentication.
    """

    # Required authentication fields
    username: str = Field(..., description="Valid email address for SharePoint authentication")

    password: SecretStr = Field(..., description="User password (stored securely)")

    sharepoint_url: str = Field(..., description="SharePoint site URL")

    # Optional connection parameters with defaults
    timeout_seconds: int = Field(default=30, description="Connection timeout in seconds", ge=5, le=300)

    max_file_size_mb: int = Field(default=100, description="Maximum file size limit in MB", ge=1, le=500)

    @field_validator("password", mode="before")
    @classmethod
    def convert_password_to_secret_str(cls, v: Union[str, SecretStr]) -> SecretStr:
        """
        Convert string passwords to SecretStr for security.

        Accepts both plain strings and SecretStr instances, ensuring all passwords
        are stored securely regardless of input type.

        Args:
            v: Password as string or SecretStr

        Returns:
            SecretStr instance for secure storage
        """
        if isinstance(v, str):
            return SecretStr(v)
        return v

    @field_validator("username")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """
        Validate that username is a properly formatted email address.

        Args:
            v: Username to validate

        Returns:
            Validated username in lowercase

        Raises:
            ValueError: If username is not a valid email format
        """
        if not v or not v.strip():
            raise ValueError("Username cannot be empty")

        # Basic email format validation using regex
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, v.strip()):
            raise ValueError("Username must be a valid email address")

        return v.lower().strip()

    @field_validator("sharepoint_url")
    @classmethod
    def validate_sharepoint_url(cls, v: str) -> str:
        """
        Validate SharePoint URL format.

        Args:
            v: URL to validate

        Returns:
            Validated URL

        Raises:
            ValueError: If URL is not a valid SharePoint URL
        """
        if not v or not v.strip():
            raise ValueError("SharePoint URL cannot be empty")
        if not v.startswith(("https://", "http://")):
            raise ValueError("SharePoint URL must start with https:// or http://")
        if not v.lower().endswith(".sharepoint.com") and "sharepoint" not in v.lower():
            raise ValueError("URL must be a valid SharePoint URL")
        return v.rstrip("/")

    @classmethod
    def from_dict(cls, config_dict: dict[str, Union[str, int]]) -> "SharePointAuthConfig":
        """
        Create configuration from a dictionary.

        Args:
            config_dict: Dictionary with configuration parameters
                Required keys: username, password, sharepoint_url
                Optional keys: timeout_seconds, max_file_size_mb

        Returns:
            SharePointAuthConfig instance

        Raises:
            ValueError: If required parameters are missing

        Example:
            config = SharePointAuthConfig.from_dict({
                "username": "user@example.com",
                "password": "password",
                "sharepoint_url": "https://example.sharepoint.com",
                "timeout_seconds": 60,
                "max_file_size_mb": 200
            })
        """
        # Validate required keys
        required_keys = {"username", "password", "sharepoint_url"}
        missing_keys = required_keys - set(config_dict.keys())
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

        # Create instance with all parameters
        return cls(
            username=str(config_dict["username"]),
            password=SecretStr(str(config_dict["password"])),
            sharepoint_url=str(config_dict["sharepoint_url"]),
            timeout_seconds=int(config_dict.get("timeout_seconds", 30)),
            max_file_size_mb=int(config_dict.get("max_file_size_mb", 100)),
        )


class FileInfo(BaseModel):
    """
    Metadata model for SharePoint files.

    Contains all relevant information about Excel files stored in SharePoint,
    including path, size, modification dates, and file type classification.
    """

    # Core file identification - removed min_length to allow custom validation
    name: str = Field(..., description="File name with extension")

    library: str = Field(..., description="SharePoint library name containing the file")

    relative_path: str = Field(..., description="Relative path from SharePoint library root")

    # File metadata - removed ge=0 to allow custom validation
    size_bytes: int = Field(..., description="File size in bytes")

    modified_date: datetime = Field(..., description="Last modification timestamp")

    file_type: FileType = Field(..., description="Excel file type based on extension")

    # Optional metadata
    created_date: Optional[datetime] = Field(default=None, description="File creation timestamp")

    created_by: Optional[str] = Field(default=None, description="User who created the file", max_length=255)

    modified_by: Optional[str] = Field(default=None, description="User who last modified the file", max_length=255)

    @field_validator("name")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        """
        Validate file name format and extension.

        Args:
            v: File name to validate

        Returns:
            Validated file name

        Raises:
            ValueError: If file name is invalid or has unsupported extension
        """
        if not v or not v.strip():
            raise ValueError("File name cannot be empty")

        # Check for valid Excel extension
        file_path = Path(v)
        extension = file_path.suffix.lower()

        valid_extensions = [ft.value for ft in FileType]
        if extension not in valid_extensions:
            raise ValueError(f"File must have Excel extension: {', '.join(valid_extensions)}")

        return v

    @field_validator("library")
    @classmethod
    def validate_library_name(cls, v: str) -> str:
        """
        Validate SharePoint library name.

        Args:
            v: Library name to validate

        Returns:
            Validated library name

        Raises:
            ValueError: If library name is invalid
        """
        if not v or not v.strip():
            raise ValueError("Library name cannot be empty")

        return v.strip()

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, v: str) -> str:
        """
        Validate and normalize relative path.

        Args:
            v: Relative path to validate

        Returns:
            Normalized relative path

        Raises:
            ValueError: If path is invalid
        """
        if not v or not v.strip():
            raise ValueError("Relative path cannot be empty")

        # Normalize path separators and remove leading/trailing slashes
        # First replace backslashes with forward slashes
        normalized = v.replace("\\", "/")

        # Remove leading and trailing slashes
        normalized = normalized.strip("/")

        # Clean up multiple consecutive slashes
        normalized = re.sub(r"/+", "/", normalized)

        if not normalized:
            raise ValueError("Relative path cannot be empty after normalization")

        return normalized

    @field_validator("size_bytes")
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """
        Validate file size is within reasonable limits.

        Args:
            v: File size in bytes

        Returns:
            Validated file size

        Raises:
            ValueError: If file size is invalid
        """
        if v < 0:
            raise ValueError("File size cannot be negative")

        # Note: Maximum file size limit is configured in SharePointAuthConfig
        # and should be validated at the application level, not in the model
        return v

    @property
    def size_mb(self) -> float:
        """
        Get file size in megabytes.

        Returns:
            File size in MB rounded to 2 decimal places
        """
        return round(self.size_bytes / (1024 * 1024), 2)

    @property
    def extension(self) -> str:
        """
        Get file extension in lowercase.

        Returns:
            File extension (e.g., '.xlsx')
        """
        return Path(self.name).suffix.lower()

    @property
    def full_path(self) -> str:
        """
        Get full path including library name.

        Returns:
            Full path from SharePoint site root (e.g., 'Documenti/General/folder/file.xlsx')
        """
        return f"{self.library}/{self.relative_path}"

    def __str__(self) -> str:
        """
        String representation of file info.

        Returns:
            Human-readable file description
        """
        return f"{self.name} ({self.size_mb}MB, modified: {self.modified_date.strftime('%Y-%m-%d %H:%M')})"

    def validate_against_config(self, config: "SharePointAuthConfig") -> None:
        """
        Validate file info against SharePoint configuration limits.

        Args:
            config: SharePoint configuration with size limits

        Raises:
            ValueError: If file exceeds configured limits
        """
        max_size_bytes = config.max_file_size_mb * 1024 * 1024
        if self.size_bytes > max_size_bytes:
            raise ValueError(f"File size {self.size_mb}MB exceeds maximum limit of {config.max_file_size_mb}MB")


class ExcelData(BaseModel):
    """
    Model for Excel file data extracted from SharePoint.

    This model represents the structured data extracted from an Excel file,
    including metadata about the extraction process and the actual data rows.
    """

    # File metadata
    filename: str = Field(..., description="Original Excel file name")

    sheet_name: str = Field(..., description="Name of the sheet that was read")

    # Data content
    data: list[dict[str, Any]] = Field(..., description="List of dictionaries representing Excel rows")

    # Processing metadata
    row_count: int = Field(..., description="Number of data rows extracted", ge=0)

    column_names: list[str] = Field(..., description="List of column names after any mapping is applied")

    # Optional processing information
    column_mapping_applied: Optional[dict[str, str]] = Field(
        default=None, description="Column mapping that was applied during extraction"
    )

    empty_rows_skipped: int = Field(default=0, description="Number of empty rows that were skipped", ge=0)

    @model_validator(mode="before")
    @classmethod
    def validate_data_structure(cls, values: Any) -> Any:
        """
        Validate that data is a list of dictionaries.

        Args:
            values: Raw input values before Pydantic processing

        Returns:
            Validated values

        Raises:
            ValueError: If data structure is invalid
        """
        if isinstance(values, dict) and "data" in values:
            data = values["data"]  # type: ignore[misc]
            if not isinstance(data, list):
                raise ValueError("Data must be a list")

            for i, row in enumerate(data):  # type: ignore[misc]
                if not isinstance(row, dict):
                    raise ValueError(f"Row {i} must be a dictionary")

        return values  # type: ignore[misc]

    @field_validator("row_count")
    @classmethod
    def validate_row_count_matches_data(cls, v: int, info: Any) -> int:
        """
        Validate that row_count matches the actual data length.

        Args:
            v: Row count value
            info: Validation info context

        Returns:
            Validated row count

        Raises:
            ValueError: If row count doesn't match data length
        """
        # In Pydantic v2, we can access other field values through info.data
        if hasattr(info, "data") and info.data and "data" in info.data:
            data_length = len(info.data["data"]) if info.data["data"] else 0
            if data_length != v:
                raise ValueError(f"Row count {v} doesn't match data length {data_length}")
        return v

    @property
    def is_empty(self) -> bool:
        """
        Check if the Excel data is empty.

        Returns:
            True if no data rows were extracted
        """
        return self.row_count == 0

    @property
    def column_count(self) -> int:
        """
        Get the number of columns in the data.

        Returns:
            Number of columns
        """
        return len(self.column_names)

    def get_column_data(self, column_name: str) -> list[Any]:
        """
        Extract all values for a specific column.

        Args:
            column_name: Name of the column to extract

        Returns:
            List of values from the specified column

        Raises:
            ValueError: If column name doesn't exist
        """
        if column_name not in self.column_names:
            raise ValueError(f"Column '{column_name}' not found in data")

        return [row.get(column_name) for row in self.data]

    def filter_rows(self, condition: Callable[[dict[str, Any]], bool]) -> "ExcelData":
        """
        Create a new ExcelData with rows filtered by a condition.

        Args:
            condition: Function that takes a row dict and returns bool

        Returns:
            New ExcelData instance with filtered data
        """
        filtered_data = [row for row in self.data if condition(row)]

        return ExcelData(
            filename=self.filename,
            sheet_name=self.sheet_name,
            data=filtered_data,
            row_count=len(filtered_data),
            column_names=self.column_names,
            column_mapping_applied=self.column_mapping_applied,
            empty_rows_skipped=self.empty_rows_skipped,
        )


class ColumnMapping(BaseModel):
    """
    Model for Excel column name mapping configuration.

    This model defines how Excel column names should be transformed during
    the data extraction process, allowing for standardization of field names
    across different Excel file formats.
    """

    # Core mapping configuration
    mappings: dict[str, str] = Field(..., description="Dictionary mapping original column names to new names")

    # Optional configuration
    case_sensitive: bool = Field(default=True, description="Whether column name matching should be case sensitive")

    ignore_missing: bool = Field(default=True, description="Whether to ignore mapping entries for non-existent columns")

    @model_validator(mode="before")
    @classmethod
    def validate_mappings(cls, values: Any) -> Any:
        """
        Validate mapping dictionary structure.

        Args:
            values: Raw input values before Pydantic processing

        Returns:
            Validated values

        Raises:
            ValueError: If mappings are invalid
        """
        if isinstance(values, dict) and "mappings" in values:
            mappings = values["mappings"]  # type: ignore[misc]
            if not isinstance(mappings, dict):
                raise ValueError("Mappings must be a dictionary")

            for original, mapped in mappings.items():  # type: ignore[misc]
                if not isinstance(original, str) or not isinstance(mapped, str):
                    raise ValueError("Both original and mapped column names must be strings")

                if not original.strip() or not mapped.strip():
                    raise ValueError("Column names cannot be empty or whitespace-only")

        return values  # type: ignore[misc]

    def apply_to_columns(self, column_names: list[str]) -> dict[str, str]:
        """
        Apply the mapping to a list of column names and return the applicable mappings.

        Args:
            column_names: List of original column names

        Returns:
            Dictionary of mappings that apply to the given columns

        Raises:
            ValueError: If ignore_missing is False and some mappings don't apply
        """
        applicable_mappings = {}
        missing_columns = []

        for original, mapped in self.mappings.items():
            # Check for column existence (case sensitive or not)
            if self.case_sensitive:
                if original in column_names:
                    applicable_mappings[original] = mapped
                else:
                    missing_columns.append(original)  # type: ignore[misc]
            else:
                # Case insensitive matching
                matching_column = None
                for col in column_names:
                    if col.lower() == original.lower():
                        matching_column = col
                        break

                if matching_column:
                    applicable_mappings[matching_column] = mapped
                else:
                    missing_columns.append(original)  # type: ignore[misc]

        # Handle missing columns based on configuration
        if missing_columns and not self.ignore_missing:
            raise ValueError(f"Mapping columns not found: {', '.join(missing_columns)}")  # type: ignore[misc]

        return applicable_mappings  # type: ignore[misc]

    @property
    def mapping_count(self) -> int:
        """
        Get the number of mappings defined.

        Returns:
            Number of column mappings
        """
        return len(self.mappings)
