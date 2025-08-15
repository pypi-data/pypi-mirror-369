"""
Pydantic v2 data models for SharePoint Reader component.

This module contains all data models used for configuration validation,
file metadata, and data transfer objects in the SharePoint Reader.
"""

import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel, Field, SecretStr, field_validator


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
