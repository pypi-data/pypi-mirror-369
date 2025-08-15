"""
Unit tests for SharePoint configuration module.

Tests cover the new explicit configuration API.
"""

import os
from unittest.mock import patch

import pytest

from fetchpoint.config import create_config_from_dict, create_sharepoint_config, load_sharepoint_config


class TestCreateSharePointConfig:
    """Test cases for create_sharepoint_config function."""

    def test_create_config_explicit_params(self) -> None:
        """Test creating config with explicit parameters."""
        config = create_sharepoint_config(
            username="user@company.com",
            password="secret123",
            sharepoint_url="https://company.sharepoint.com",
            timeout_seconds=60,
            max_file_size_mb=200,
        )

        assert config.username == "user@company.com"
        assert config.password.get_secret_value() == "secret123"
        assert config.sharepoint_url == "https://company.sharepoint.com"
        assert config.timeout_seconds == 60
        assert config.max_file_size_mb == 200

    def test_create_config_defaults(self) -> None:
        """Test creating config with default values."""
        config = create_sharepoint_config(
            username="user@company.com", password="secret123", sharepoint_url="https://company.sharepoint.com"
        )

        assert config.username == "user@company.com"
        assert config.password.get_secret_value() == "secret123"
        assert config.sharepoint_url == "https://company.sharepoint.com"
        assert config.timeout_seconds == 30  # Default
        assert config.max_file_size_mb == 100  # Default

    def test_create_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        config_dict = {
            "username": "user@example.com",
            "password": "password123",
            "sharepoint_url": "https://example.sharepoint.com",
            "timeout_seconds": 45,
            "max_file_size_mb": 150,
        }

        config = create_config_from_dict(config_dict)

        assert config.username == "user@example.com"
        assert config.password.get_secret_value() == "password123"
        assert config.sharepoint_url == "https://example.sharepoint.com"
        assert config.timeout_seconds == 45
        assert config.max_file_size_mb == 150

    def test_create_config_from_dict_missing_required(self) -> None:
        """Test creating config from dictionary with missing required fields."""
        config_dict = {
            "username": "user@example.com"
            # Missing password and sharepoint_url
        }

        with pytest.raises(ValueError, match="Missing required parameter"):
            create_config_from_dict(config_dict)


class TestDeprecatedLoadConfig:
    """Test cases for deprecated load_sharepoint_config function."""

    @patch.dict(
        os.environ,
        {
            "SHAREPOINT_USERNAME": "user@company.com",
            "SHAREPOINT_PASSWORD": "secret123",
            "SHAREPOINT_URL": "https://company.sharepoint.com",
        },
    )
    def test_load_config_deprecated_warning(self) -> None:
        """Test that deprecated function still works but shows warning."""
        with pytest.warns(DeprecationWarning, match="load_sharepoint_config\\(\\) is deprecated"):
            config = load_sharepoint_config()

        assert config.username == "user@company.com"
        assert config.password.get_secret_value() == "secret123"
        assert config.sharepoint_url == "https://company.sharepoint.com"
        assert config.timeout_seconds == 30
        assert config.max_file_size_mb == 100

    def test_load_config_missing_env_vars(self) -> None:
        """Test that load_sharepoint_config fails when env vars missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Environment variables not found"):
                load_sharepoint_config()
