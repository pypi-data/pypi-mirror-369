"""
Configuration management for FetchPoint library.

This module provides configuration models and factory methods for SharePoint
authentication with explicit configuration (no environment dependencies).
"""

import logging
from typing import Any, Optional

from pydantic import SecretStr

from .models import SharePointAuthConfig

# Configure logger for this module
logger = logging.getLogger(__name__)

# Default values - centralized configuration
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_FILE_SIZE_MB = 100


def _mask_sensitive_value(value: str, mask_char: str = "*", visible_chars: int = 3) -> str:
    """
    Mask sensitive values for logging while keeping some characters visible.

    Args:
        value: The sensitive value to mask
        mask_char: Character to use for masking (default: "*")
        visible_chars: Number of characters to keep visible at the start (default: 3)

    Returns:
        Masked string for safe logging

    Example:
        _mask_sensitive_value("user@example.com") -> "use***********"
        _mask_sensitive_value("password123") -> "pas*******"
    """
    if not value or len(value) <= visible_chars:
        return mask_char * len(value) if value else ""

    visible_part = value[:visible_chars]
    masked_part = mask_char * (len(value) - visible_chars)
    return visible_part + masked_part


def _log_config_loading(config: SharePointAuthConfig) -> None:
    """
    Log configuration details with sensitive values masked.

    Args:
        config: SharePoint configuration to log
    """
    logger.info("SharePoint configuration loaded successfully")
    logger.debug(
        "Configuration details: username=%s, url=%s, timeout=%ds, max_file_size=%dMB",
        _mask_sensitive_value(config.username),
        config.sharepoint_url,
        config.timeout_seconds,
        config.max_file_size_mb,
    )


def create_sharepoint_config(
    username: str,
    password: str,
    sharepoint_url: str,
    timeout_seconds: Optional[int] = None,
    max_file_size_mb: Optional[int] = None,
) -> SharePointAuthConfig:
    """
    Create SharePoint configuration with explicit parameters.

    Args:
        username: SharePoint username (email)
        password: SharePoint password
        sharepoint_url: SharePoint site URL
        timeout_seconds: Connection timeout in seconds (default: 30)
        max_file_size_mb: Maximum file size limit in MB (default: 100)

    Returns:
        SharePointAuthConfig: Validated configuration object

    Raises:
        ValueError: If required parameters are missing or invalid

    Example:
        config = create_sharepoint_config(
            username="user@example.com",
            password="password",
            sharepoint_url="https://example.sharepoint.com"
        )
    """
    logger.debug("Creating SharePoint configuration with provided parameters")

    # Use provided values or defaults
    final_timeout = timeout_seconds if timeout_seconds is not None else DEFAULT_TIMEOUT_SECONDS
    final_max_size = max_file_size_mb if max_file_size_mb is not None else DEFAULT_MAX_FILE_SIZE_MB

    # Create configuration with all parameters
    config = SharePointAuthConfig(
        username=username,
        password=SecretStr(password),  # Convert to SecretStr explicitly
        sharepoint_url=sharepoint_url,
        timeout_seconds=final_timeout,
        max_file_size_mb=final_max_size,
    )

    # Log successful configuration creation with masked sensitive values
    _log_config_loading(config)

    return config


def create_config_from_dict(config_dict: dict[str, Any]) -> SharePointAuthConfig:
    """
    Create SharePoint configuration from a dictionary.

    Args:
        config_dict: Dictionary with configuration parameters
            Required keys: username, password, sharepoint_url
            Optional keys: timeout_seconds, max_file_size_mb

    Returns:
        SharePointAuthConfig: Validated configuration object

    Raises:
        ValueError: If required parameters are missing or invalid

    Example:
        config = create_config_from_dict({
            "username": "user@example.com",
            "password": "password",
            "sharepoint_url": "https://example.sharepoint.com",
            "timeout_seconds": 60,
            "max_file_size_mb": 200
        })
    """
    logger.debug("Creating SharePoint configuration from dictionary")

    # Extract required parameters
    if "username" not in config_dict:
        raise ValueError("Missing required parameter: username")
    if "password" not in config_dict:
        raise ValueError("Missing required parameter: password")
    if "sharepoint_url" not in config_dict:
        raise ValueError("Missing required parameter: sharepoint_url")

    # Create configuration using the main factory function
    return create_sharepoint_config(
        username=config_dict["username"],
        password=config_dict["password"],
        sharepoint_url=config_dict["sharepoint_url"],
        timeout_seconds=config_dict.get("timeout_seconds"),
        max_file_size_mb=config_dict.get("max_file_size_mb"),
    )


# Backward compatibility wrappers
# These will be removed in future versions
def load_sharepoint_config(**kwargs: Any) -> SharePointAuthConfig:
    """
    DEPRECATED: This function will be removed in v0.3.0.
    Use create_sharepoint_config() or create_config_from_dict() instead.

    For migration, use:
        import os
        from dotenv import load_dotenv
        from fetchpoint import create_sharepoint_config

        load_dotenv()
        config = create_sharepoint_config(
            username=os.getenv("SHAREPOINT_USERNAME"),
            password=os.getenv("SHAREPOINT_PASSWORD"),
            sharepoint_url=os.getenv("SHAREPOINT_URL")
        )
    """
    import os
    import warnings

    warnings.warn(
        "load_sharepoint_config() is deprecated and will be removed in v0.3.0. "
        "Use create_sharepoint_config() or create_config_from_dict() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Try to load from environment for backward compatibility
    username = os.getenv("SHAREPOINT_USERNAME")
    password = os.getenv("SHAREPOINT_PASSWORD")
    url = os.getenv("SHAREPOINT_URL")

    if not username or not password or not url:
        raise ValueError(
            "Environment variables not found. Please use create_sharepoint_config() with explicit parameters instead."
        )

    timeout = os.getenv("SHAREPOINT_TIMEOUT_SECONDS")
    max_size = os.getenv("SHAREPOINT_MAX_FILE_SIZE_MB")

    return create_sharepoint_config(
        username=username,
        password=password,
        sharepoint_url=url,
        timeout_seconds=int(timeout) if timeout else None,
        max_file_size_mb=int(max_size) if max_size else None,
    )


def load_sharepoint_paths() -> dict[str, list[str]]:
    """
    DEPRECATED: This function will be removed in v0.3.0.
    Path management should be handled by the calling application.

    For migration:
        - Store paths in your application configuration
        - Pass paths directly to SharePointClient methods
    """
    import warnings

    warnings.warn(
        "load_sharepoint_paths() is deprecated and will be removed in v0.3.0. "
        "Path management should be handled by the calling application.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Return empty dict for backward compatibility
    return {}


def load_download_path() -> Optional[str]:
    """
    DEPRECATED: This function will be removed in v0.3.0.
    Path management should be handled by the calling application.
    """
    import warnings

    warnings.warn(
        "load_download_path() is deprecated and will be removed in v0.3.0. "
        "Path management should be handled by the calling application.",
        DeprecationWarning,
        stacklevel=2,
    )

    return None


def extract_sharepoint_library_name() -> Optional[str]:
    """
    DEPRECATED: This function will be removed in v0.3.0.
    Library names should be passed explicitly to SharePointClient methods.
    """
    import warnings

    warnings.warn(
        "extract_sharepoint_library_name() is deprecated and will be removed in v0.3.0. "
        "Library names should be passed explicitly to SharePointClient methods.",
        DeprecationWarning,
        stacklevel=2,
    )

    return None


def validate_environment_setup() -> dict[str, Any]:
    """
    DEPRECATED: This function will be removed in v0.3.0.
    Environment validation should be handled by the calling application.
    """
    import warnings

    warnings.warn(
        "validate_environment_setup() is deprecated and will be removed in v0.3.0. "
        "Environment validation should be handled by the calling application.",
        DeprecationWarning,
        stacklevel=2,
    )

    return {"status": "deprecated", "message": "Use explicit configuration instead"}


def get_env_or_raise(key: str) -> str:
    """
    DEPRECATED: This function will be removed in v0.3.0.
    Environment reading should be handled by the calling application.
    """
    import warnings

    warnings.warn(
        "get_env_or_raise() is deprecated and will be removed in v0.3.0. "
        "Environment reading should be handled by the calling application.",
        DeprecationWarning,
        stacklevel=2,
    )

    import os

    value = os.getenv(key)
    if not value:
        raise ValueError(f"Environment variable '{key}' not set (deprecated function)")
    return value
