"""
Integration tests for the SharePoint authenticator public API.

These tests verify that the authenticator can be imported and used
correctly through the public package interface.
"""

from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest
from pydantic import SecretStr

# Test importing from the package
from fetchpoint import SharePointAuthConfig, create_authenticated_context
from fetchpoint.exceptions import FederatedAuthError

if TYPE_CHECKING:
    from unittest.mock import MagicMock


class TestAuthenticatorPublicAPI:
    """Test cases for the public authenticator API."""

    def test_can_import_authenticator_from_package(self) -> None:
        """Test that the authenticator can be imported from the main package."""
        # This test passes if the import above works
        assert callable(create_authenticated_context)

    @patch("fetchpoint.authenticator.ClientContext")
    @patch("fetchpoint.authenticator.UserCredential")
    def test_public_api_successful_authentication(
        self, mock_user_cred: "MagicMock", mock_client_context: "MagicMock"
    ) -> None:
        """Test successful authentication through the public API."""
        # Arrange
        config = SharePointAuthConfig(
            username="test.user@company.com",
            password=SecretStr("test_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
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
    def test_public_api_authentication_failure(self, mock_client_context: "MagicMock") -> None:
        """Test authentication failure through the public API."""
        # Arrange
        config = SharePointAuthConfig(
            username="invalid.user@company.com",
            password=SecretStr("wrong_password"),
            sharepoint_url="https://company.sharepoint.com/sites/test",
        )

        # Simulate authentication failure
        mock_client_context.side_effect = Exception("AADSTS50126: Invalid username or password")

        # Act & Assert
        with pytest.raises(FederatedAuthError) as exc_info:
            create_authenticated_context(config)

        error = exc_info.value
        assert "Invalid username or password" in str(error)
        assert error.context["auth_provider"] == "Azure AD"
        assert error.context["username"] == "inv***"
