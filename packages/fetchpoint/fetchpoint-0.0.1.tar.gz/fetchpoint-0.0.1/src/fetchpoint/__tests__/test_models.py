"""
Unit tests for FetchPoint Pydantic models.

Tests cover all validation scenarios, field validators, and model functionality
for SharePoint authentication and file metadata models.
"""

from datetime import datetime

import pytest
from pydantic import BaseModel, SecretStr, ValidationError

from fetchpoint.models import FileInfo, FileType, SharePointAuthConfig


class TestFileType:
    """Test cases for FileType enum."""

    def test_file_type_values(self) -> None:
        """Test that FileType enum has correct Excel extensions."""
        assert FileType.XLSX == ".xlsx"
        assert FileType.XLS == ".xls"
        assert FileType.XLSM == ".xlsm"
        assert FileType.XLSB == ".xlsb"

    def test_file_type_string_inheritance(self) -> None:
        """Test that FileType inherits from str."""
        assert isinstance(FileType.XLSX, str)
        assert str(FileType.XLSX) == ".xlsx"


class TestSharePointAuthConfig:
    """Test cases for SharePointAuthConfig model."""

    def test_valid_config_creation(self) -> None:
        """Test creating valid SharePointAuthConfig."""
        config = SharePointAuthConfig(
            username="test.user@company.com",
            password="secret123",  # type: ignore[arg-type]
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        assert config.username == "test.user@company.com"
        assert config.password.get_secret_value() == "secret123"
        assert config.sharepoint_url == "https://company.sharepoint.com/sites/test"
        assert config.timeout_seconds == 30  # Default value
        assert config.max_file_size_mb == 100  # Default value

    def test_custom_optional_fields(self) -> None:
        """Test config with custom optional field values."""
        config = SharePointAuthConfig(
            username="admin@company.com",
            password="admin123",  # type: ignore[arg-type]
            sharepoint_url="https://company.sharepoint.com",
            timeout_seconds=60,
            max_file_size_mb=200,
        )

        assert config.timeout_seconds == 60
        assert config.max_file_size_mb == 200

    def test_username_validation_valid_company_email(self) -> None:
        """Test username validation with valid company email."""
        config = SharePointAuthConfig(
            username="Test.User@COMPANY.COM",  # Mixed case
            password="secret",  # type: ignore[arg-type]
            sharepoint_url="https://test.sharepoint.com",
        )

        # Should be converted to lowercase
        assert config.username == "test.user@company.com"

    def test_username_validation_valid_email_formats(self) -> None:
        """Test username validation accepts various valid email formats."""
        valid_emails = [
            "user@gmail.com",
            "admin@company.org",
            "test.user@company.com",
            "User.Name@Domain.COM",  # Mixed case
            "user123@test-domain.co.uk",
            "name+tag@example.io",
        ]

        for email in valid_emails:
            config = SharePointAuthConfig(
                username=email,
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://test.sharepoint.com",
            )
            # Should be converted to lowercase and trimmed
            assert config.username == email.lower().strip()

    def test_username_validation_invalid_email_formats(self) -> None:
        """Test username validation rejects invalid email formats."""
        invalid_emails = [
            "not-an-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user.domain.com",
            "user@domain.",
            "user name@domain.com",  # Space in email
            "user@@domain.com",  # Double @
        ]

        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                SharePointAuthConfig(
                    username=invalid_email,
                    password="secret",  # type: ignore[arg-type]
                    sharepoint_url="https://test.sharepoint.com",
                )

            error = exc_info.value.errors()[0]
            assert "Username must be a valid email address" in str(error["msg"])

    def test_username_validation_empty(self) -> None:
        """Test username validation rejects empty values."""
        with pytest.raises(ValidationError) as exc_info:
            SharePointAuthConfig(
                username="",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://test.sharepoint.com",
            )

        # Should fail with our custom validation message
        error = exc_info.value.errors()[0]
        assert "Username cannot be empty" in str(error["msg"])

    def test_sharepoint_url_validation_valid_urls(self) -> None:
        """Test SharePoint URL validation with valid URLs."""
        valid_urls = [
            "https://company.sharepoint.com",
            "https://company.sharepoint.com/sites/test",
            "http://internal-sharepoint.company.com",
        ]

        for url in valid_urls:
            config = SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url=url,
            )
            assert config.sharepoint_url == url.rstrip("/")

    def test_sharepoint_url_validation_removes_trailing_slash(self) -> None:
        """Test that trailing slashes are removed from URLs."""
        config = SharePointAuthConfig(
            username="user@company.com",
            password="secret",  # type: ignore[arg-type]
            sharepoint_url="https://company.sharepoint.com/",
        )

        assert config.sharepoint_url == "https://company.sharepoint.com"

    def test_sharepoint_url_validation_invalid_protocol(self) -> None:
        """Test SharePoint URL validation rejects invalid protocols."""
        with pytest.raises(ValidationError) as exc_info:
            SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="ftp://company.sharepoint.com",
            )

        error = exc_info.value.errors()[0]
        assert "SharePoint URL must start with https:// or http://" in str(error["msg"])

    def test_sharepoint_url_validation_invalid_domain(self) -> None:
        """Test SharePoint URL validation rejects non-SharePoint domains."""
        with pytest.raises(ValidationError) as exc_info:
            SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://google.com",
            )

        error = exc_info.value.errors()[0]
        assert "URL must be a valid SharePoint URL" in str(error["msg"])

    def test_timeout_validation_bounds(self) -> None:
        """Test timeout validation enforces bounds."""
        # Test minimum bound
        with pytest.raises(ValidationError):
            SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://test.sharepoint.com",
                timeout_seconds=4,  # Below minimum of 5
            )

        # Test maximum bound
        with pytest.raises(ValidationError):
            SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://test.sharepoint.com",
                timeout_seconds=301,  # Above maximum of 300
            )

    def test_max_file_size_validation_bounds(self) -> None:
        """Test max file size validation enforces bounds."""
        # Test minimum bound
        with pytest.raises(ValidationError):
            SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://test.sharepoint.com",
                max_file_size_mb=0,  # Below minimum of 1
            )

        # Test maximum bound
        with pytest.raises(ValidationError):
            SharePointAuthConfig(
                username="user@company.com",
                password="secret",  # type: ignore[arg-type]
                sharepoint_url="https://test.sharepoint.com",
                max_file_size_mb=501,  # Above maximum of 500
            )

    def test_password_secret_str(self) -> None:
        """Test that password field uses SecretStr."""
        config = SharePointAuthConfig(
            username="user@company.com",
            password="secret123",  # type: ignore[arg-type]
            sharepoint_url="https://test.sharepoint.com",
        )

        # Password should be SecretStr type
        from pydantic import SecretStr

        assert isinstance(config.password, SecretStr)

        # Should not be visible in string representation
        config_str = str(config)
        assert "secret123" not in config_str
        assert "**********" in config_str or "SecretStr" in config_str


class TestFileInfo:
    """Test cases for FileInfo model."""

    def test_valid_file_info_creation(self) -> None:
        """Test creating valid FileInfo."""
        file_info = FileInfo(
            name="report.xlsx",
            library="Documents",
            relative_path="documents/reports/report.xlsx",
            size_bytes=1024000,
            modified_date=datetime(2024, 1, 15, 10, 30),
            file_type=FileType.XLSX,
        )

        assert file_info.name == "report.xlsx"
        assert file_info.library == "Documents"
        assert file_info.relative_path == "documents/reports/report.xlsx"
        assert file_info.size_bytes == 1024000
        assert file_info.file_type == FileType.XLSX

    def test_file_info_with_optional_fields(self) -> None:
        """Test FileInfo with optional fields set."""
        file_info = FileInfo(
            name="data.xlsx",
            library="Shared Documents",
            relative_path="shared/data.xlsx",
            size_bytes=2048000,
            modified_date=datetime(2024, 2, 1, 14, 45),
            file_type=FileType.XLSX,
            created_date=datetime(2024, 1, 15, 9, 0),
            created_by="John Doe",
            modified_by="Jane Smith",
        )

        assert file_info.created_date == datetime(2024, 1, 15, 9, 0)
        assert file_info.created_by == "John Doe"
        assert file_info.modified_by == "Jane Smith"

    def test_file_name_validation_valid_extensions(self) -> None:
        """Test file name validation accepts valid Excel extensions."""
        valid_files = ["report.xlsx", "data.xls", "macro.xlsm", "binary.xlsb"]

        for filename in valid_files:
            file_info = FileInfo(
                name=filename,
                library="Documents",
                relative_path=f"files/{filename}",
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,  # Will be validated separately
            )
            assert file_info.name == filename

    def test_file_name_validation_invalid_extension(self) -> None:
        """Test file name validation rejects invalid extensions."""
        invalid_files = ["document.pdf", "image.png", "text.txt", "data.csv"]

        for filename in invalid_files:
            with pytest.raises(ValidationError) as exc_info:
                FileInfo(
                    name=filename,
                    library="Documents",
                    relative_path=f"files/{filename}",
                    size_bytes=1000,
                    modified_date=datetime.now(),
                    file_type=FileType.XLSX,
                )

            error = exc_info.value.errors()[0]
            assert "File must have Excel extension" in str(error["msg"])

    def test_file_name_validation_empty(self) -> None:
        """Test file name validation rejects empty names."""
        with pytest.raises(ValidationError) as exc_info:
            FileInfo(
                name="",
                library="Documents",
                relative_path="files/empty",
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
            )

        error = exc_info.value.errors()[0]
        assert "File name cannot be empty" in str(error["msg"])

    def test_relative_path_validation_normalization(self) -> None:
        """Test relative path validation and normalization."""
        test_cases = [
            ("documents\\reports\\file.xlsx", "documents/reports/file.xlsx"),
            ("/documents/reports/file.xlsx", "documents/reports/file.xlsx"),
            ("documents/reports/file.xlsx/", "documents/reports/file.xlsx"),
            ("//documents//reports//file.xlsx//", "documents/reports/file.xlsx"),
        ]

        for input_path, expected_path in test_cases:
            file_info = FileInfo(
                name="file.xlsx",
                library="Documents",
                relative_path=input_path,
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
            )
            assert file_info.relative_path == expected_path

    def test_relative_path_validation_empty(self) -> None:
        """Test relative path validation rejects empty paths."""
        with pytest.raises(ValidationError) as exc_info:
            FileInfo(
                name="file.xlsx",
                library="Documents",
                relative_path="",
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
            )

        error = exc_info.value.errors()[0]
        assert "Relative path cannot be empty" in str(error["msg"])

    def test_size_validation_bounds(self) -> None:
        """Test file size validation enforces bounds."""
        # Test negative size
        with pytest.raises(ValidationError) as exc_info:
            FileInfo(
                name="file.xlsx",
                library="Documents",
                relative_path="files/file.xlsx",
                size_bytes=-1,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
            )

        error = exc_info.value.errors()[0]
        assert "File size cannot be negative" in str(error["msg"])

        # File size validation no longer has hardcoded limits
        # Large files should be accepted by the model itself
        large_size = 101 * 1024 * 1024  # 101MB
        file_info = FileInfo(
            name="file.xlsx",
            library="Documents",
            relative_path="files/file.xlsx",
            size_bytes=large_size,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )
        # Should not raise ValidationError at model level
        assert file_info.size_bytes == large_size

    def test_size_mb_property(self) -> None:
        """Test size_mb property calculation."""
        file_info = FileInfo(
            name="file.xlsx",
            library="Documents",
            relative_path="files/file.xlsx",
            size_bytes=1048576,  # 1MB exactly
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )

        assert file_info.size_mb == 1.0

        # Test rounding
        file_info.size_bytes = 1572864  # 1.5MB
        assert file_info.size_mb == 1.5

    def test_extension_property(self) -> None:
        """Test extension property extraction."""
        file_info = FileInfo(
            name="Report.XLSX",  # Mixed case
            library="Documents",
            relative_path="files/Report.XLSX",
            size_bytes=1000,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )

        assert file_info.extension == ".xlsx"  # Should be lowercase

    def test_library_field(self) -> None:
        """Test library field validation and access."""
        file_info = FileInfo(
            name="test.xlsx",
            library="Shared Documents",
            relative_path="folder/test.xlsx",
            size_bytes=1000,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )

        assert file_info.library == "Shared Documents"

        # Test library validation - empty library
        with pytest.raises(ValidationError) as exc_info:
            FileInfo(
                name="test.xlsx",
                library="",
                relative_path="folder/test.xlsx",
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
            )

        error = exc_info.value.errors()[0]
        assert "Library name cannot be empty" in str(error["msg"])

    def test_full_path_property(self) -> None:
        """Test full_path property combines library and relative path."""
        file_info = FileInfo(
            name="report.xlsx",
            library="Documents",
            relative_path="General/Reports/report.xlsx",
            size_bytes=1000,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )

        assert file_info.full_path == "Documents/General/Reports/report.xlsx"

        # Test with file in library root
        file_info_root = FileInfo(
            name="root.xlsx",
            library="Documents",
            relative_path="root.xlsx",
            size_bytes=1000,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )

        assert file_info_root.full_path == "Documents/root.xlsx"

    def test_str_representation(self) -> None:
        """Test string representation of FileInfo."""
        file_info = FileInfo(
            name="report.xlsx",
            library="Documents",
            relative_path="files/report.xlsx",
            size_bytes=1048576,  # 1MB
            modified_date=datetime(2024, 1, 15, 10, 30),
            file_type=FileType.XLSX,
        )

        str_repr = str(file_info)
        assert "report.xlsx" in str_repr
        assert "1.0MB" in str_repr
        assert "2024-01-15 10:30" in str_repr

    def test_user_fields_max_length(self) -> None:
        """Test created_by and modified_by fields max length validation."""
        # Test valid length for created_by
        file_info = FileInfo(
            name="file.xlsx",
            library="Documents",
            relative_path="files/file.xlsx",
            size_bytes=1000,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
            created_by="A" * 255,  # Maximum allowed length
        )
        # Fixed: Add None check before calling len()
        assert file_info.created_by is not None and len(file_info.created_by) == 255

        # Test valid length for modified_by
        file_info = FileInfo(
            name="file.xlsx",
            library="Documents",
            relative_path="files/file.xlsx",
            size_bytes=1000,
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
            modified_by="B" * 255,  # Maximum allowed length
        )
        assert file_info.modified_by is not None and len(file_info.modified_by) == 255

        # Test exceeding max length for created_by
        with pytest.raises(ValidationError):
            FileInfo(
                name="file.xlsx",
                library="Documents",
                relative_path="files/file.xlsx",
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
                created_by="A" * 256,  # Exceeds maximum
            )

        # Test exceeding max length for modified_by
        with pytest.raises(ValidationError):
            FileInfo(
                name="file.xlsx",
                library="Documents",
                relative_path="files/file.xlsx",
                size_bytes=1000,
                modified_date=datetime.now(),
                file_type=FileType.XLSX,
                modified_by="B" * 256,  # Exceeds maximum
            )

    def test_validate_against_config(self) -> None:
        """Test validate_against_config method."""
        config = SharePointAuthConfig(
            username="test@example.com",
            password=SecretStr("password123"),
            sharepoint_url="https://example.sharepoint.com",
            max_file_size_mb=10,
        )

        # Test file within size limit
        small_file = FileInfo(
            name="small.xlsx",
            library="Documents",
            relative_path="files/small.xlsx",
            size_bytes=5 * 1024 * 1024,  # 5MB
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )
        # Should not raise exception
        small_file.validate_against_config(config)

        # Test file exceeding size limit
        large_file = FileInfo(
            name="large.xlsx",
            library="Documents",
            relative_path="files/large.xlsx",
            size_bytes=15 * 1024 * 1024,  # 15MB
            modified_date=datetime.now(),
            file_type=FileType.XLSX,
        )
        with pytest.raises(ValueError) as exc_info:
            large_file.validate_against_config(config)

        assert "exceeds maximum limit" in str(exc_info.value)


def test_models_are_exportable() -> None:
    """Test that all models can be imported from the models module."""
    from fetchpoint.models import FileInfo, FileType, SharePointAuthConfig

    # Test that classes are properly defined
    assert FileInfo is not None
    assert FileType is not None
    assert SharePointAuthConfig is not None

    # Test that they are the correct types
    assert isinstance(FileType.XLSX, str)
    assert issubclass(FileInfo, BaseModel)
    assert issubclass(SharePointAuthConfig, BaseModel)


def test_models_exportable_from_package() -> None:
    """Test that models can be imported from the main package."""
    from fetchpoint import FileInfo, FileType, SharePointAuthConfig

    # Test basic instantiation works
    config = SharePointAuthConfig(
        username="test@company.com",
        password="secret",  # type: ignore[arg-type]
        sharepoint_url="https://test.sharepoint.com",
    )
    assert config.username == "test@company.com"

    file_info = FileInfo(
        name="test.xlsx",
        library="Documents",
        relative_path="files/test.xlsx",
        size_bytes=1000,
        modified_date=datetime.now(),
        file_type=FileType.XLSX,
    )
    assert file_info.name == "test.xlsx"
