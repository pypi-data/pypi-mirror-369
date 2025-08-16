"""
Federated authentication handler for enterprise SharePoint access.

This module provides authentication functionality for users accessing
SharePoint Online through federated authentication providers such as Azure AD.
It handles the authentication flow transparently and provides clear error messages.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from office365.runtime.auth.user_credential import UserCredential  # type: ignore[import-untyped]
    from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
else:
    # Import at runtime to avoid missing stub file errors
    try:
        from office365.runtime.auth.user_credential import UserCredential  # type: ignore[import-untyped]
        from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "office365-rest-python-client is required. Install with: pip install office365-rest-python-client>=2.5.0"
        ) from e

from .exceptions import AuthenticationError, FederatedAuthError
from .models import SharePointAuthConfig

# Configure logger for this module
logger = logging.getLogger(__name__)


def create_authenticated_context(config: SharePointAuthConfig) -> ClientContext:
    """
    Create an authenticated SharePoint client context.

    This function handles the complete authentication flow for enterprise users
    accessing SharePoint Online through federated authentication providers.

    Args:
        config: SharePoint authentication configuration

    Returns:
        ClientContext: Authenticated SharePoint client context

    Raises:
        FederatedAuthError: For federated authentication specific issues
        AuthenticationError: For general authentication failures
    """
    logger.info("Starting federated authentication for user: %s", _mask_username(config.username))

    try:
        # Create SharePoint client context
        context = _create_client_context(config)

        # Validate the connection by loading web properties
        _validate_connection(context)

        logger.info("Authentication successful for user: %s", _mask_username(config.username))
        return context

    except Exception as e:
        # Map specific errors to custom exceptions
        raise _map_authentication_error(e, config.username, config.sharepoint_url)


def _create_client_context(config: SharePointAuthConfig) -> ClientContext:
    """
    Create SharePoint client context with user credentials.

    Args:
        config: SharePoint authentication configuration

    Returns:
        ClientContext: SharePoint client context with credentials
    """
    logger.debug("Creating SharePoint client context for URL: %s", config.sharepoint_url)

    # Create client context with the SharePoint site URL
    context = ClientContext(config.sharepoint_url)

    # Set up user credentials for federated authentication
    credentials = UserCredential(config.username, config.password.get_secret_value())

    # Apply credentials to the context
    context.with_credentials(credentials)

    return context


def _validate_connection(context: ClientContext) -> None:
    """
    Validate the authentication by loading web properties.

    This function tests the connection by attempting to load the web properties,
    which requires successful authentication.

    Args:
        context: SharePoint client context to validate

    Raises:
        Exception: If connection validation fails
    """
    logger.debug("Validating connection by loading web properties")

    # Load web properties to test authentication
    web = context.web
    context.load(web)
    context.execute_query()

    logger.debug("Connection validation successful")


def _mask_username(username: str) -> str:
    """
    Mask username for secure logging.

    Shows only the first 3 characters of the username for security.

    Args:
        username: Username to mask

    Returns:
        Masked username for logging
    """
    if len(username) <= 3:
        return "***"
    return username[:3] + "***"


def _map_authentication_error(error: Exception, username: str, site_url: str) -> Exception:
    """
    Map authentication errors to appropriate custom exceptions.

    This function analyzes the original error and maps it to the most
    appropriate custom exception with helpful context.

    Args:
        error: Original exception from authentication
        username: Username that failed authentication
        site_url: SharePoint site URL

    Returns:
        Exception: Mapped custom exception
    """
    error_str = str(error).lower()

    # Handle Azure AD specific errors (federated auth issues)
    if "aadsts" in error_str:
        return _create_federated_auth_error(error_str, username, site_url)

    # Handle permission/authorization errors
    if "403" in error_str or "forbidden" in error_str:
        return _create_permission_error(username, site_url)

    # Handle general authentication errors
    if "401" in error_str or "unauthorized" in error_str:
        return _create_general_auth_error(error_str, username, site_url)

    # Handle network/connection errors
    if "timeout" in error_str or "connection" in error_str:
        return _create_connection_error(error_str, site_url)

    # Default to general authentication error
    return AuthenticationError(f"Authentication failed: {error}", username=username, site_url=site_url)


def _create_federated_auth_error(error_str: str, username: str, site_url: str) -> FederatedAuthError:
    """
    Create specific federated authentication error.

    Args:
        error_str: Error string from original exception
        username: Username that failed authentication
        site_url: SharePoint site URL

    Returns:
        FederatedAuthError: Specific federated auth error
    """
    if "aadsts50034" in error_str:
        message = (
            "User account does not exist in the target tenant. "
            "Verify user is registered as guest in the target SharePoint tenant."
        )
    elif "aadsts50126" in error_str:
        message = "Invalid username or password. Please verify your credentials."
    else:
        message = f"Federated authentication failed. Azure AD error: {error_str}"

    return FederatedAuthError(message, username=username, site_url=site_url, auth_provider="Azure AD")


def _create_permission_error(username: str, site_url: str) -> AuthenticationError:
    """
    Create permission-specific authentication error.

    Args:
        username: Username that was denied access
        site_url: SharePoint site URL

    Returns:
        AuthenticationError: Permission-specific error
    """
    return AuthenticationError(
        "Access denied. User may not be authorized to access this SharePoint site. "
        "Please verify that the user has appropriate permissions.",
        username=username,
        site_url=site_url,
    )


def _create_general_auth_error(error_str: str, username: str, site_url: str) -> AuthenticationError:
    """
    Create general authentication error.

    Args:
        error_str: Error string from original exception
        username: Username that failed authentication
        site_url: SharePoint site URL

    Returns:
        AuthenticationError: General authentication error
    """
    return AuthenticationError(
        f"Authentication failed. Please verify your credentials. Details: {error_str}",
        username=username,
        site_url=site_url,
    )


def _create_connection_error(error_str: str, site_url: str) -> AuthenticationError:
    """
    Create connection-specific authentication error.

    Args:
        error_str: Error string from original exception
        site_url: SharePoint site URL

    Returns:
        AuthenticationError: Connection-specific error
    """
    return AuthenticationError(
        f"Connection failed during authentication. Please check network connectivity. Details: {error_str}",
        site_url=site_url,
    )
