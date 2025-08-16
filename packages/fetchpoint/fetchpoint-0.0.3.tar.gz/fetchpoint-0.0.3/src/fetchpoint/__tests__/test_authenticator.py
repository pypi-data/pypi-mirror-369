"""
Unit tests for the SharePoint authenticator module.

Tests cover authentication success/failure scenarios, error mapping,
and edge cases for federated authentication with enterprise users.
"""

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

from fetchpoint.authenticator import (
    _create_client_context,  # pyright: ignore[reportPrivateUsage]
    _create_connection_error,  # pyright: ignore[reportPrivateUsage]
    _create_federated_auth_error,  # pyright: ignore[reportPrivateUsage]
    _create_general_auth_error,  # pyright: ignore[reportPrivateUsage]
    _create_permission_error,  # pyright: ignore[reportPrivateUsage]
    _map_authentication_error,  # pyright: ignore[reportPrivateUsage]
    _mask_username,  # pyright: ignore[reportPrivateUsage]
    _validate_connection,  # pyright: ignore[reportPrivateUsage]
    create_authenticated_context,
)
from fetchpoint.exceptions import AuthenticationError, FederatedAuthError
from fetchpoint.models import SharePointAuthConfig

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestCreateAuthenticatedContext:
    """Test cases for the main authentication function."""

    def test_successful_authentication(self) -> None:
        """Test successful authentication flow."""
        # Arrange
        config = SharePointAuthConfig(
            username="test.user@company.com",
            password=SecretStr("test_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        with (
            patch("fetchpoint.authenticator._create_client_context") as mock_create,
            patch("fetchpoint.authenticator._validate_connection") as mock_validate,
        ):
            mock_context = Mock()
            mock_create.return_value = mock_context
            mock_validate.return_value = None

            # Act
            result = create_authenticated_context(config)

            # Assert
            assert result == mock_context
            mock_create.assert_called_once_with(config)
            mock_validate.assert_called_once_with(mock_context)

    def test_authentication_failure_maps_error(self) -> None:
        """Test that authentication failures are properly mapped to custom exceptions."""
        # Arrange
        config = SharePointAuthConfig(
            username="test.user@company.com",
            password=SecretStr("wrong_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        original_error = Exception("AADSTS50126: Invalid username or password")

        with patch("fetchpoint.authenticator._create_client_context", side_effect=original_error):
            # Act & Assert
            with pytest.raises(FederatedAuthError) as exc_info:
                create_authenticated_context(config)

            assert "Invalid username or password" in str(exc_info.value)
            assert exc_info.value.context["auth_provider"] == "Azure AD"

    def test_validation_failure_maps_error(self) -> None:
        """Test that connection validation failures are properly mapped."""
        # Arrange
        config = SharePointAuthConfig(
            username="test.user@company.com",
            password=SecretStr("test_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        validation_error = Exception("403 Forbidden")

        with (
            patch("fetchpoint.authenticator._create_client_context") as mock_create,
            patch("fetchpoint.authenticator._validate_connection", side_effect=validation_error),
        ):
            mock_context = Mock()
            mock_create.return_value = mock_context

            # Act & Assert
            with pytest.raises(AuthenticationError) as exc_info:
                create_authenticated_context(config)

            assert "Access denied" in str(exc_info.value)


class TestCreateClientContext:
    """Test cases for client context creation."""

    @patch("fetchpoint.authenticator.ClientContext")
    @patch("fetchpoint.authenticator.UserCredential")
    def test_creates_context_with_credentials(
        self, mock_user_cred: "MagicMock", mock_client_context: "MagicMock"
    ) -> None:
        """Test that client context is created with proper credentials."""
        # Arrange
        config = SharePointAuthConfig(
            username="test.user@company.com",
            password=SecretStr("test_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        mock_context = Mock()
        mock_client_context.return_value = mock_context
        mock_credentials = Mock()
        mock_user_cred.return_value = mock_credentials

        # Act
        result = _create_client_context(config)

        # Assert
        mock_client_context.assert_called_once_with(config.sharepoint_url)
        mock_user_cred.assert_called_once_with("test.user@company.com", "test_password")
        mock_context.with_credentials.assert_called_once_with(mock_credentials)
        assert result == mock_context


class TestValidateConnection:
    """Test cases for connection validation."""

    def test_successful_validation(self) -> None:
        """Test successful connection validation."""
        # Arrange
        mock_context = Mock()
        mock_web = Mock()
        mock_context.web = mock_web

        # Act
        _validate_connection(mock_context)

        # Assert
        mock_context.load.assert_called_once_with(mock_web)
        mock_context.execute_query.assert_called_once()

    def test_validation_failure_raises_exception(self) -> None:
        """Test that validation failures raise exceptions."""
        # Arrange
        mock_context = Mock()
        mock_context.execute_query.side_effect = Exception("Connection failed")

        # Act & Assert
        with pytest.raises(Exception, match="Connection failed"):
            _validate_connection(mock_context)


class TestMaskUsername:
    """Test cases for username masking utility."""

    def test_mask_normal_username(self) -> None:
        """Test masking of normal length username."""
        result = _mask_username("test.user@company.com")
        assert result == "tes***"

    def test_mask_short_username(self) -> None:
        """Test masking of short username."""
        result = _mask_username("ab")
        assert result == "***"

    def test_mask_exact_length_username(self) -> None:
        """Test masking of exactly 3 character username."""
        result = _mask_username("abc")
        assert result == "***"

    def test_mask_empty_username(self) -> None:
        """Test masking of empty username."""
        result = _mask_username("")
        assert result == "***"


class TestMapAuthenticationError:
    """Test cases for error mapping functionality."""

    def test_maps_aadsts_error_to_federated_auth_error(self) -> None:
        """Test mapping of AADSTS errors to FederatedAuthError."""
        error = Exception("AADSTS50034: User account does not exist")

        result = _map_authentication_error(error, "test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, FederatedAuthError)
        assert "User account does not exist in the target tenant" in str(result)
        assert result.context["auth_provider"] == "Azure AD"

    def test_maps_403_error_to_permission_error(self) -> None:
        """Test mapping of 403 errors to permission error."""
        error = Exception("403 Forbidden")

        result = _map_authentication_error(error, "test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Access denied" in str(result)

    def test_maps_401_error_to_general_auth_error(self) -> None:
        """Test mapping of 401 errors to general authentication error."""
        error = Exception("401 Unauthorized")

        result = _map_authentication_error(error, "test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Authentication failed" in str(result)

    def test_maps_timeout_error_to_connection_error(self) -> None:
        """Test mapping of timeout errors to connection error."""
        error = Exception("Connection timeout")

        result = _map_authentication_error(error, "test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Connection failed during authentication" in str(result)

    def test_maps_unknown_error_to_general_auth_error(self) -> None:
        """Test mapping of unknown errors to general authentication error."""
        error = Exception("Unknown error")

        result = _map_authentication_error(error, "test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Authentication failed: Unknown error" in str(result)


class TestCreateFederatedAuthError:
    """Test cases for federated authentication error creation."""

    def test_creates_user_not_exist_error(self) -> None:
        """Test creation of user does not exist error."""
        result = _create_federated_auth_error(
            "aadsts50034: user account does not exist", "test@company.com", "https://test.sharepoint.com"
        )

        assert isinstance(result, FederatedAuthError)
        assert "User account does not exist in the target tenant" in str(result)
        assert result.context["auth_provider"] == "Azure AD"

    def test_creates_invalid_credentials_error(self) -> None:
        """Test creation of invalid credentials error."""
        result = _create_federated_auth_error(
            "aadsts50126: invalid username or password", "test@company.com", "https://test.sharepoint.com"
        )

        assert isinstance(result, FederatedAuthError)
        assert "Invalid username or password" in str(result)

    def test_creates_generic_azure_error(self) -> None:
        """Test creation of generic Azure AD error."""
        result = _create_federated_auth_error(
            "aadsts99999: unknown azure error", "test@company.com", "https://test.sharepoint.com"
        )

        assert isinstance(result, FederatedAuthError)
        assert "Federated authentication failed. Azure AD error" in str(result)


class TestCreatePermissionError:
    """Test cases for permission error creation."""

    def test_creates_permission_error_with_context(self) -> None:
        """Test creation of permission error with proper context."""
        result = _create_permission_error("test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Access denied" in str(result)
        assert "user has appropriate permissions" in str(result)
        assert result.context["username"] == "tes***"
        assert result.context["site_url"] == "https://test.sharepoint.com"


class TestCreateGeneralAuthError:
    """Test cases for general authentication error creation."""

    def test_creates_general_error_with_details(self) -> None:
        """Test creation of general auth error with error details."""
        result = _create_general_auth_error("authentication failed", "test@company.com", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Authentication failed" in str(result)
        assert "verify your credentials" in str(result)
        assert "authentication failed" in str(result)


class TestCreateConnectionError:
    """Test cases for connection error creation."""

    def test_creates_connection_error_with_details(self) -> None:
        """Test creation of connection error with network details."""
        result = _create_connection_error("connection timeout", "https://test.sharepoint.com")

        assert isinstance(result, AuthenticationError)
        assert "Connection failed during authentication" in str(result)
        assert "check network connectivity" in str(result)
        assert "connection timeout" in str(result)
        assert result.context["site_url"] == "https://test.sharepoint.com"


class TestIntegrationScenarios:
    """Integration test scenarios for complete authentication flows."""

    @patch("fetchpoint.authenticator.ClientContext")
    @patch("fetchpoint.authenticator.UserCredential")
    def test_complete_successful_flow(self, mock_user_cred: "MagicMock", mock_client_context: "MagicMock") -> None:
        """Test complete successful authentication flow."""
        # Arrange
        config = SharePointAuthConfig(
            username="name.surname@company.com",
            password=SecretStr("valid_password"),
            sharepoint_url="https://company.sharepoint.com/sites/MercatoLiberonuovapiattaforma",
        )

        mock_context = Mock()
        mock_client_context.return_value = mock_context
        mock_web = Mock()
        mock_context.web = mock_web

        # Act
        result = create_authenticated_context(config)

        # Assert
        assert result == mock_context
        mock_client_context.assert_called_once_with(config.sharepoint_url)
        mock_context.with_credentials.assert_called_once()
        mock_context.load.assert_called_once_with(mock_web)
        mock_context.execute_query.assert_called_once()

    @patch("fetchpoint.authenticator.ClientContext")
    def test_complete_failure_flow_with_aadsts_error(self, mock_client_context: "MagicMock") -> None:
        """Test complete failure flow with AADSTS error."""
        # Arrange
        config = SharePointAuthConfig(
            username="invalid.user@company.com",
            password=SecretStr("wrong_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        # Simulate Office365 library raising an exception with AADSTS error
        mock_client_context.side_effect = Exception("AADSTS50126: Invalid username or password")

        # Act & Assert
        with pytest.raises(FederatedAuthError) as exc_info:
            create_authenticated_context(config)

        error = exc_info.value
        assert "Invalid username or password" in str(error)
        assert error.context["auth_provider"] == "Azure AD"
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
        assert error.context["username"] == "inv***"
        assert error.context["site_url"] == config.sharepoint_url
