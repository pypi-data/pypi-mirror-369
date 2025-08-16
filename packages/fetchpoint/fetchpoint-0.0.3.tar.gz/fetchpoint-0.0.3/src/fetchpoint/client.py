"""
Main SharePoint client interface for read-only operations.

This module provides the primary interface for connecting to SharePoint Online,
managing federated authentication, and coordinating file operations. The client
follows a stateless design with comprehensive error handling and logging.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]
    from office365.sharepoint.folder import Folder  # type: ignore[import-untyped]

from .authenticator import create_authenticated_context
from .config import SharePointAuthConfig, create_config_from_dict, load_sharepoint_paths
from .exceptions import ConnectionError, FileDownloadError, FileNotFoundError, FileSizeLimitError, PermissionError
from .file_handler import (
    create_file_info,
    list_excel_files_by_path_segments,
    list_files_in_library,
    list_folders_in_library,
)
from .models import FileInfo

# Configure logger for this module
logger = logging.getLogger(__name__)


class PathResolver:
    """
    Helper class for resolving and validating SharePoint paths with hierarchical error reporting.

    This class provides methods to validate path segments incrementally and give
    detailed error messages when paths fail, showing exactly which folder is missing
    and what alternatives are available.
    """

    def __init__(self, context: "ClientContext", library_name: str = "Documents"):
        """
        Initialize PathResolver with SharePoint context.

        Args:
            context: Authenticated SharePoint client context
            library_name: Name of the document library
        """
        self.context = context
        self.library_name = library_name

    def validate_path(self, path_segments: list[str]) -> tuple[bool, str, list[str]]:
        """
        Validate a path by checking each segment hierarchically.

        Args:
            path_segments: List of path segments to validate

        Returns:
            Tuple of (is_valid, error_message, available_folders_at_failure_point)

        Raises:
            ConnectionError: If context is not authenticated
            LibraryNotFoundError: If library cannot be accessed
        """
        if not self.context:
            raise ConnectionError("SharePoint context is not authenticated")

        logger.debug("Validating path: %s", " -> ".join(path_segments))

        try:
            # First, try to access the library to verify it exists
            try:
                library = self.context.web.lists.get_by_title(self.library_name)
                self.context.load(library)
                self.context.execute_query()
                logger.debug("Successfully accessed library: %s", self.library_name)
            except Exception as library_error:
                # Library access failed - this means the library name is wrong
                logger.debug("Library access failed: %s", library_error)
                available_libraries = self.get_available_libraries()
                error_msg = f"Library '{self.library_name}' not found or inaccessible"
                return False, error_msg, available_libraries

            # Validate each segment by building the path incrementally
            current_folder = library.root_folder
            for i, segment in enumerate(path_segments):
                logger.debug("Attempting to access folder segment: '%s' (position %d)", segment, i + 1)

                try:
                    # Instead of using get_by_path, navigate folder by folder
                    # This approach is more reliable for folder names with spaces
                    # Since get_by_name doesn't exist, we need to iterate through folders
                    folders_collection = current_folder.folders
                    self.context.load(folders_collection)  # type: ignore[misc]
                    self.context.execute_query()

                    # Find the folder with matching name
                    found_folder = None
                    for folder_item in folders_collection:  # type: ignore[attr-defined]
                        folder_name = getattr(folder_item, "name", None)
                        if folder_name and str(folder_name) == segment:
                            found_folder = folder_item
                            break

                    if found_folder is None:
                        raise Exception(f"Folder '{segment}' not found")

                    # Update current folder to the found folder
                    current_folder = found_folder
                    logger.debug("Successfully validated path segment: %s", segment)

                except Exception as e:
                    # This segment failed - get available folders at current level
                    logger.debug("Path segment '%s' failed validation: %s", segment, e)
                    logger.debug("Exception type: %s", type(e).__name__)
                    logger.debug("Exception details: %s", str(e))

                    # Get parent folder (current folder before the failed segment)
                    if i == 0:
                        # Failed at first level - get root folders
                        logger.debug("Failed at first level, getting root folders")
                        parent_folder = library.root_folder
                    else:
                        # Parent folder is the current_folder from previous iteration
                        # We need to re-navigate to the parent folder
                        logger.debug("Failed at level %d, getting parent folder", i)
                        parent_folder = library.root_folder
                        # Navigate to parent folder by going through previous segments
                        for parent_segment in path_segments[:i]:
                            try:
                                # Use the same folder iteration approach as above
                                parent_folders_collection = parent_folder.folders
                                self.context.load(parent_folders_collection)  # type: ignore[misc]
                                self.context.execute_query()

                                # Find the folder with matching name
                                found_parent_folder = None
                                for folder_item in parent_folders_collection:  # type: ignore[attr-defined]
                                    folder_name = getattr(folder_item, "name", None)
                                    if folder_name and str(folder_name) == parent_segment:
                                        found_parent_folder = folder_item
                                        break

                                if found_parent_folder is None:
                                    raise Exception(f"Parent folder '{parent_segment}' not found")

                                parent_folder = found_parent_folder
                            except Exception as parent_error:
                                logger.debug(
                                    "Failed to navigate to parent segment '%s': %s", parent_segment, parent_error
                                )
                                # Fall back to root folder if parent navigation fails
                                parent_folder = library.root_folder
                                break

                    # Get available folders at this level
                    logger.debug("Getting available folders at current level")
                    available_folders = self._get_available_folders(parent_folder)  # type: ignore[arg-type]
                    logger.debug("Available folders at failure point: %s", available_folders)

                    # DEBUG: Add detailed comparison of the failed segment with available folders
                    logger.debug("=== DEBUGGING FOLDER MATCHING ===")
                    logger.debug("Failed segment: %r (length: %d)", segment, len(segment))
                    logger.debug("Failed segment chars: %s", [f"{c!r}({ord(c)})" for c in segment])
                    logger.debug("Available folders count: %d", len(available_folders))
                    for idx, folder in enumerate(available_folders):
                        is_match = folder == segment
                        is_case_match = folder.lower() == segment.lower()
                        logger.debug(
                            "  [%d] %r (len: %d) - exact_match: %s, case_match: %s",
                            idx,
                            folder,
                            len(folder),
                            is_match,
                            is_case_match,
                        )
                        if folder == segment:
                            logger.debug("    *** EXACT MATCH FOUND BUT API CALL FAILED! ***")
                        elif folder.lower() == segment.lower():
                            logger.debug("    *** CASE INSENSITIVE MATCH FOUND ***")
                    logger.debug("=== END DEBUGGING ===")

                    # Build current path for error message
                    current_path_segments = path_segments[:i] if i > 0 else []
                    current_path_str = " -> ".join(current_path_segments) if current_path_segments else "root"

                    error_msg = (
                        f"Path validation failed at segment '{segment}' "
                        f"(position {i + 1}/{len(path_segments)}). "
                        f"Current path: {current_path_str}"
                    )

                    return False, error_msg, available_folders

            # All segments validated successfully
            logger.info("Path validation successful: %s", " -> ".join(path_segments))
            return True, "", []

        except Exception as e:
            # Unexpected error during validation
            logger.error("Unexpected error during path validation: %s", e)
            error_msg = f"Unexpected error during path validation: {e}"
            return False, error_msg, []

    def _get_available_folders(self, folder: "Folder") -> list[str]:  # type: ignore[misc]
        """
        Get list of available folders at the current level.

        Args:
            folder: SharePoint folder object

        Returns:
            List of folder names available at this level
        """
        try:
            # Load folders using the same pattern as list_folders_in_library
            folders_query = folder.folders  # type: ignore[misc]
            self.context.load(folders_query)  # type: ignore[misc]
            self.context.execute_query()

            # Extract folder names with type safety (same as list_folders_in_library)
            folder_names: list[str] = []
            for folder_item in folders_query:  # type: ignore[attr-defined]
                folder_name = getattr(folder_item, "name", None)  # type: ignore[misc]
                if folder_name:
                    folder_names.append(str(folder_name))
                    logger.debug("Found folder: %s", folder_name)

            logger.debug("Found %d folders at current level: %s", len(folder_names), folder_names)
            return folder_names

        except Exception as e:
            logger.warning("Failed to get available folders: %s", e)
            return []

    def get_available_libraries(self) -> list[str]:
        """
        Get list of available document libraries in the SharePoint site.

        Returns:
            List of library names available in the site

        Raises:
            ConnectionError: If context is not authenticated
        """
        if not self.context:
            raise ConnectionError("SharePoint context is not authenticated")

        try:
            # Get all lists in the site
            lists = self.context.web.lists
            self.context.load(lists)
            self.context.execute_query()

            # Filter for document libraries (BaseTemplate = 101)
            library_names: list[str] = []
            for lst in lists:  # type: ignore[attr-defined]
                # Check if it's a document library
                base_template = getattr(lst, "base_template", None)
                if base_template == 101:  # Document Library template
                    title = getattr(lst, "title", "")
                    if title:
                        library_names.append(str(title))

            logger.debug("Found %d document libraries: %s", len(library_names), library_names)
            return library_names

        except Exception as e:
            logger.warning("Failed to get available libraries: %s", e)
            return []


class SharePointClient:
    """
    Main FetchPoint client class for SharePoint operations.

    Provides read-only access to SharePoint files with authentication management
    and context manager support for proper resource cleanup.

    Example:
        # Using explicit configuration
        config = SharePointAuthConfig(
            username="user@example.com",
            password="password",
            sharepoint_url="https://example.sharepoint.com"
        )
        client = SharePointClient(config)

        # Using dictionary configuration
        client = SharePointClient.from_dict({
            "username": "user@example.com",
            "password": "password",
            "sharepoint_url": "https://example.sharepoint.com"
        })

        # Using context manager
        with SharePointClient(config) as client:
            # Operations here
            pass
    """

    def __init__(self, config: SharePointAuthConfig, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize SharePoint client with explicit configuration.

        Args:
            config: SharePoint configuration (required)
            logger: Optional logger instance for custom logging

        Raises:
            ValueError: If configuration is invalid or missing required values
        """
        # Use provided logger or module logger
        self.logger = logger or logging.getLogger(__name__)

        self.logger.debug("Initializing SharePoint client")

        if not config:
            raise ValueError("Configuration is required. Use SharePointAuthConfig or SharePointClient.from_dict()")

        self._config = config
        self._context: Optional["ClientContext"] = None
        self._is_connected = False

        self.logger.info("SharePoint client initialized for URL: %s", config.sharepoint_url)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any], logger: Optional[logging.Logger] = None) -> "SharePointClient":
        """
        Create SharePoint client from dictionary configuration.

        Args:
            config_dict: Dictionary with configuration parameters
                Required keys: username, password, sharepoint_url
                Optional keys: timeout_seconds, max_file_size_mb
            logger: Optional logger instance for custom logging

        Returns:
            SharePointClient instance

        Raises:
            ValueError: If required parameters are missing

        Example:
            client = SharePointClient.from_dict({
                "username": "user@example.com",
                "password": "password",
                "sharepoint_url": "https://example.sharepoint.com"
            })
        """
        config = create_config_from_dict(config_dict)
        return cls(config, logger=logger)

    def connect(self) -> bool:
        """
        Establish connection to SharePoint using configured credentials.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails
            FederatedAuthError: If federated authentication fails
            ConnectionError: If connection cannot be established
        """
        self.logger.info("Connecting to SharePoint: %s", self._config.sharepoint_url)

        try:
            # Create authenticated context using the authenticator
            self._context = create_authenticated_context(self._config)
            self._is_connected = True

            self.logger.info("Successfully connected to SharePoint")
            return True

        except Exception as e:
            self.logger.error("Failed to connect to SharePoint: %s", e)
            self._context = None
            self._is_connected = False
            raise

    def test_connection(self) -> bool:
        """
        Test the current connection by attempting to load web properties.

        Returns:
            bool: True if connection is valid and working

        Raises:
            ConnectionError: If not connected or connection test fails
        """
        self.logger.debug("Testing SharePoint connection")

        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        try:
            # Test connection by loading web properties
            web = self._context.web
            self._context.load(web)
            self._context.execute_query()

            self.logger.debug("Connection test successful")
            return True

        except Exception as e:
            self.logger.error("Connection test failed: %s", e)
            raise ConnectionError(f"Connection test failed: {e}", site_url=self._config.sharepoint_url) from e

    def disconnect(self) -> None:
        """
        Disconnect from SharePoint and clean up resources.

        This method is safe to call multiple times and will not raise errors
        if already disconnected.
        """
        if self._is_connected:
            self.logger.info("Disconnecting from SharePoint")

        # Clean up context and reset connection state
        self._context = None
        self._is_connected = False

        self.logger.debug("SharePoint client disconnected")

    @property
    def is_connected(self) -> bool:
        """
        Check if client is currently connected to SharePoint.

        Returns:
            bool: True if connected, False otherwise
        """
        return self._is_connected

    @property
    def config(self) -> SharePointAuthConfig:
        """
        Get the current SharePoint configuration.

        Returns:
            SharePointAuthConfig: Current configuration object
        """
        return self._config

    @property
    def context(self) -> Optional["ClientContext"]:
        """
        Get the authenticated SharePoint context.

        Returns:
            ClientContext: Authenticated context if connected, None otherwise
        """
        return self._context

    def download_file(self, library: str, path: list[str], local_path: str) -> None:
        """
        Download a single file from SharePoint.

        Args:
            library: SharePoint library name (e.g., "Documents")
            path: Path segments to the file (e.g., ["General", "Reports", "file.xlsx"])
            local_path: Local filesystem path to save the file

        Raises:
            ConnectionError: If not connected to SharePoint
            FileNotFoundError: If file not found
            FileDownloadError: If download fails
            FileSizeLimitError: If file exceeds size limit

        Example:
            client.download_file(
                library="Documents",
                path=["General", "Reports", "2024", "report.xlsx"],
                local_path="./downloads/report.xlsx"
            )
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        self.logger.info("Downloading file from %s: %s", library, " -> ".join(path))

        # The last element is the filename
        if not path:
            raise ValueError("Path cannot be empty")

        filename = path[-1]
        folder_segments = path[:-1]

        # Navigate to the file
        file_item = self._get_file_item(library, folder_segments, filename)

        if file_item is None:
            raise FileNotFoundError(f"File not found: {'/'.join(path)}")

        # Check file size
        file_size = getattr(file_item, "length", 0)
        max_size_bytes = self._config.max_file_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            from .exceptions import FileSizeLimitError

            raise FileSizeLimitError(file_path="/".join(path), file_size=file_size, size_limit=max_size_bytes)

        # Download file
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as local_file:
            file_item.download(local_file).execute_query()

        self.logger.info("Downloaded file to: %s", local_path)

    def list_files(self, library: str, path: list[str]) -> list[FileInfo]:
        """
        List files in a SharePoint folder.

        Args:
            library: SharePoint library name (e.g., "Documents")
            path: Path segments to the folder (e.g., ["General", "Reports"])

        Returns:
            List of FileInfo objects for files in the folder

        Raises:
            ConnectionError: If not connected to SharePoint
            LibraryNotFoundError: If library not found

        Example:
            files = client.list_files(
                library="Documents",
                path=["General", "Reports", "2024"]
            )
            for file in files:
                print(f"{file.name} - {file.size_mb}MB")
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        self.logger.info("Listing files in %s: %s", library, " -> ".join(path) if path else "root")

        # Use the existing list_files_in_library function
        folder_path = "/".join(path) if path else None
        return list_files_in_library(self._context, library, folder_path)

    def __enter__(self) -> "SharePointClient":
        """
        Enter context manager - establish connection.

        Returns:
            SharePointClient: Self for method chaining

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection cannot be established
        """
        self.logger.debug("Entering SharePoint client context manager")
        self.connect()
        return self

    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """
        Exit context manager - clean up connection.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        logger.debug("Exiting SharePoint client context manager")
        self.disconnect()

    def __repr__(self) -> str:
        """
        Return detailed string representation for debugging.

        Returns:
            str: Detailed representation with masked sensitive information
        """
        # Mask the username for security
        masked_username = self._config.username[:3] + "***" if len(self._config.username) > 3 else "***"

        return (
            f"SharePointClient("
            f"username={masked_username}, "
            f"url={self._config.sharepoint_url}, "
            f"connected={self._is_connected})"
        )

    def __str__(self) -> str:
        """
        Return user-friendly string representation.

        Returns:
            str: Simple string representation with masked username and connection status
        """
        # Mask the username for security - same logic as __repr__
        masked_username = self._config.username[:3] + "***" if len(self._config.username) > 3 else "***"

        status = "connected" if self._is_connected else "disconnected"

        # Extract domain from URL for display
        url_domain = self._config.sharepoint_url.replace("https://", "").replace("http://", "").split("/")[0]

        return f"SharePointClient (username={masked_username}, url={url_domain}, connected={status})"

    def list_excel_files(self, library_name: str = "Documents", folder_path: Optional[str] = None) -> list[str]:
        """
        List Excel file names in a SharePoint document library.

        This method provides a simplified interface for getting just the names of Excel files,
        without the additional metadata provided by list_files().

        Args:
            library_name: Name of the document library (default: "Documents")
            folder_path: Optional relative path within the library (e.g., "General/13_ AMS")

        Returns:
            List of Excel file names found in the specified location

        Raises:
            ConnectionError: If not connected to SharePoint
            LibraryNotFoundError: If library or folder cannot be found
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        # Convert folder_path to path segments for reliable navigation
        if folder_path:
            # Split the folder path into segments
            path_segments = [segment.strip() for segment in folder_path.split("/") if segment.strip()]
            # Use the new path-segment based function
            return list_excel_files_by_path_segments(self._context, library_name, path_segments)
        else:
            # For root folder, use empty path segments
            return list_excel_files_by_path_segments(self._context, library_name, [])

    def list_folders(self, library_name: str = "Documents", folder_path: Optional[str] = None) -> list[str]:
        """
        List all folders in a SharePoint document library.

        Args:
            library_name: Name of the document library (default: "Documents")
            folder_path: Optional relative path within the library

        Returns:
            List of folder names found

        Raises:
            ConnectionError: If not connected to SharePoint
            LibraryNotFoundError: If library or folder cannot be found
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        return list_folders_in_library(self._context, library_name, folder_path)

    def validate_paths(self, library_name: str = "Documents") -> dict[str, dict[str, Any]]:
        """
        Validate all configured SharePoint paths and provide detailed error information.

        Args:
            library_name: Name of the document library to validate paths in

        Returns:
            Dictionary with validation results for each configured path:
            {
                'path_config_1': {
                    'valid': bool,
                    'path': list[str],
                    'error': str,
                    'available_folders': list[str]
                },
                'path_config_2': { ... }
            }

        Raises:
            ConnectionError: If not connected to SharePoint
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        logger.info("Validating configured SharePoint paths in library '%s'", library_name)

        # Load path configurations
        try:
            paths_config = load_sharepoint_paths()
        except Exception as e:
            logger.error("Failed to load path configurations: %s", e)
            return {}

        # Create path resolver
        resolver = PathResolver(self._context, library_name)

        # Validate each configured path
        results: dict[str, dict[str, Any]] = {}
        for path_name, path_segments in paths_config.items():
            logger.debug("Validating path '%s': %s", path_name, " -> ".join(path_segments))

            try:
                # If the first segment matches the library name, skip it
                # This handles the case where paths are configured with library name as first segment
                path_to_validate = path_segments
                if path_segments and path_segments[0] == library_name:
                    path_to_validate = path_segments[1:]
                    logger.debug("Skipping library name '%s' from path validation", library_name)

                is_valid, error_msg, available_folders = resolver.validate_path(path_to_validate)

                results[path_name] = {
                    "valid": is_valid,
                    "path": path_segments,
                    "error": error_msg,
                    "available_folders": available_folders,
                }

                if is_valid:
                    logger.info("✓ Path '%s' is valid", path_name)
                else:
                    logger.warning("✗ Path '%s' failed: %s", path_name, error_msg)
                    logger.warning("Available folders: %s", available_folders)

            except Exception as e:
                logger.error("Error validating path '%s': %s", path_name, e)
                results[path_name] = {
                    "valid": False,
                    "path": path_segments,
                    "error": f"Validation error: {e}",
                    "available_folders": [],
                }

        return results

    def validate_decoupled_paths(self) -> dict[str, dict[str, Any]]:
        """
        Validate all configured SharePoint paths when they are decoupled (use different libraries).

        This method validates each path using its own library name (first segment of the path),
        which allows for paths that span different SharePoint libraries.

        Returns:
            Dictionary with validation results for each configured path:
            {
                'path_config_1': {
                    'valid': bool,
                    'path': list[str],
                    'library': str,
                    'error': str,
                    'available_folders': list[str]
                },
                'path_config_2': { ... }
            }

        Raises:
            ConnectionError: If not connected to SharePoint
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        logger.info("Validating decoupled SharePoint paths (each using its own library)")

        # Load path configurations
        try:
            paths_config = load_sharepoint_paths()
        except Exception as e:
            logger.error("Failed to load path configurations: %s", e)
            return {}

        # Validate each configured path using its own library
        results: dict[str, dict[str, Any]] = {}
        for path_name, path_segments in paths_config.items():
            if not path_segments:
                logger.warning("Path '%s' is empty - skipping validation", path_name)
                results[path_name] = {
                    "valid": False,
                    "path": path_segments,
                    "library": "",
                    "error": "Path is empty",
                    "available_folders": [],
                }
                continue

            # Extract library name from first segment
            library_name = path_segments[0]
            logger.debug(
                "Validating path '%s' using library '%s': %s", path_name, library_name, " -> ".join(path_segments)
            )

            try:
                # Create path resolver for this specific library
                resolver = PathResolver(self._context, library_name)

                # Validate the path (starting from the second segment since first is library name)
                path_to_validate = path_segments[1:] if len(path_segments) > 1 else []

                if not path_to_validate:
                    # Only library name provided - validate library exists
                    available_libraries = resolver.get_available_libraries()
                    is_valid = library_name in available_libraries
                    error_msg = "" if is_valid else f"Library '{library_name}' not found"
                    available_folders = available_libraries if not is_valid else []
                else:
                    # Validate the full path within the library
                    # Create a custom PathResolver that reports positions correctly for decoupled paths
                    is_valid, error_msg, available_folders = self._validate_path_with_correct_positions(
                        resolver, path_to_validate, path_segments
                    )

                results[path_name] = {
                    "valid": is_valid,
                    "path": path_segments,
                    "library": library_name,
                    "error": error_msg,
                    "available_folders": available_folders,
                }

                if is_valid:
                    logger.info("✓ Path '%s' is valid in library '%s'", path_name, library_name)
                else:
                    logger.warning("✗ Path '%s' failed in library '%s': %s", path_name, library_name, error_msg)
                    logger.warning("Available folders: %s", available_folders)

            except Exception as e:
                logger.error("Error validating path '%s': %s", path_name, e)
                results[path_name] = {
                    "valid": False,
                    "path": path_segments,
                    "library": library_name,
                    "error": f"Validation error: {e}",
                    "available_folders": [],
                }

        return results

    def _validate_path_with_correct_positions(
        self, resolver: PathResolver, path_to_validate: list[str], original_path: list[str]
    ) -> tuple[bool, str, list[str]]:
        """
        Validate a path using PathResolver but with corrected position reporting for decoupled paths.

        Args:
            resolver: PathResolver instance to use for validation
            path_to_validate: Path segments to validate (without library name)
            original_path: Original full path including library name

        Returns:
            Tuple of (is_valid, error_message, available_folders_at_failure_point)
        """
        is_valid, error_msg, available_folders = resolver.validate_path(path_to_validate)

        if not is_valid and error_msg:
            # Fix the position reporting in the error message
            # The original error message has format:
            # "Path validation failed at segment 'X' (position Y/Z). Current path: ..."
            # We need to adjust the position to reflect the position in the original full path

            # Extract the failed segment from the error message
            import re

            match = re.search(r"Path validation failed at segment '([^']+)' \(position (\d+)/(\d+)\)", error_msg)
            if match:
                failed_segment = match.group(1)
                position_in_reduced_path = int(match.group(2))

                # Calculate the correct position in the original path (add 1 for library name offset)
                correct_position = position_in_reduced_path + 1
                total_segments = len(original_path)

                # Find the current path up to the failure point in the original path
                failure_index_in_original = correct_position - 1  # Convert to 0-based index
                current_path_segments = (
                    original_path[:failure_index_in_original] if failure_index_in_original > 0 else []
                )
                current_path_str = " -> ".join(current_path_segments) if current_path_segments else "root"

                # Reconstruct the error message with correct positions
                corrected_error_msg = (
                    f"Path validation failed at segment '{failed_segment}' "
                    f"(position {correct_position}/{total_segments}). "
                    f"Current path: {current_path_str}"
                )

                return False, corrected_error_msg, available_folders

        return is_valid, error_msg, available_folders

    def discover_structure(self, library_name: str = "Documents", max_depth: int = 3) -> dict[str, Any]:
        """
        Discover and map the SharePoint library structure for debugging and setup.

        This method explores the SharePoint library structure up to a specified depth
        and returns a hierarchical representation of folders and files.

        Args:
            library_name: Name of the document library to explore
            max_depth: Maximum depth to explore (default: 3)

        Returns:
            Dictionary representing the library structure:
            {
                'library': str,
                'folders': {
                    'folder_name': {
                        'path': str,
                        'folders': { ... },  # nested folders
                        'files': [str, ...]  # file names
                    }
                },
                'files': [str, ...]  # files in root
            }

        Raises:
            ConnectionError: If not connected to SharePoint
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        logger.info("Discovering SharePoint library structure: %s (max depth: %d)", library_name, max_depth)

        def _explore_folder(folder_path: Optional[str], current_depth: int) -> dict[str, Any]:
            """Recursively explore folder structure."""
            if current_depth >= max_depth:
                return {"folders": {}, "files": [], "max_depth_reached": True}

            if self._context is None:
                raise ConnectionError(
                    "SharePoint context is None. This should not happen after connection check.",
                    site_url=self._config.sharepoint_url,
                )

            try:
                # Get folders at current level
                folders = list_folders_in_library(self._context, library_name, folder_path)

                # Get files at current level
                files = list_files_in_library(self._context, library_name, folder_path)
                file_names = [f.name for f in files]

                structure: dict[str, Any] = {"folders": {}, "files": file_names, "file_count": len(file_names)}

                # Recursively explore subfolders
                for folder_name in folders:
                    subfolder_path = f"{folder_path}/{folder_name}" if folder_path else folder_name

                    logger.debug("Exploring subfolder: %s", subfolder_path)
                    structure["folders"][folder_name] = {
                        "path": subfolder_path,
                        **_explore_folder(subfolder_path, current_depth + 1),
                    }

                return structure

            except Exception as e:
                logger.warning("Failed to explore folder '%s': %s", folder_path or "root", e)
                return {"folders": {}, "files": [], "error": str(e)}

        # Start exploration from root
        structure = {"library": library_name, **_explore_folder(None, 0)}

        logger.info("Structure discovery completed for library '%s'", library_name)
        return structure

    def download_files(
        self, library_name: str, folder_path: Optional[str], filenames: list[str], download_dir: str
    ) -> dict[str, dict[str, Any]]:
        """
        Download multiple files from a SharePoint document library.

        This method downloads files sequentially from the specified library and folder,
        handling errors on a per-file basis. Failed downloads are logged and reported
        but don't stop the processing of remaining files.

        Args:
            library_name: Name of the document library
            folder_path: Optional relative path within the library (e.g., "General/Reports")
            filenames: List of file names to download
            download_dir: Local directory path to save the downloaded files

        Returns:
            Dictionary with download results for each file:
            {
                'filename1.xlsx': {
                    'success': bool,
                    'local_path': str,  # if successful
                    'error': str,       # if failed
                    'size_bytes': int   # if successful
                },
                ...
            }

        Raises:
            ConnectionError: If not connected to SharePoint
            ValueError: If download_dir is not provided
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        if not download_dir:
            raise ValueError("download_dir parameter is required")

        # Ensure download directory exists
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Starting download of %d files from library '%s', folder: %s to '%s'",
            len(filenames),
            library_name,
            folder_path or "root",
            download_path,
        )

        # Convert folder_path to path segments for reliable navigation
        path_segments: list[str] = []
        if folder_path:
            path_segments = [segment.strip() for segment in folder_path.split("/") if segment.strip()]

        # Results dictionary to track each file's download status
        results: dict[str, dict[str, Any]] = {}

        # Download each file sequentially
        for filename in filenames:
            logger.info("Attempting to download file: %s", filename)

            try:
                # Navigate to the target folder and get the file
                file_item = self._get_file_item(library_name, path_segments, filename)

                if file_item is None:
                    error_msg = f"File '{filename}' not found in the specified location"
                    logger.error(error_msg)
                    results[filename] = {"success": False, "error": error_msg}
                    continue

                # Get file size for validation and reporting
                file_size = getattr(file_item, "length", 0)
                logger.debug("File '%s' size: %d bytes", filename, file_size)

                # Check file size limit (100MB as per specs)
                max_size_bytes = self._config.max_file_size_mb * 1024 * 1024
                if file_size > max_size_bytes:
                    error_msg = (
                        f"File '{filename}' exceeds size limit "
                        f"({file_size / (1024 * 1024):.1f}MB > {self._config.max_file_size_mb}MB)"
                    )
                    logger.error(error_msg)
                    results[filename] = {"success": False, "error": error_msg}
                    continue

                # Determine local file path
                local_file_path = download_path / filename

                # Download the file content
                logger.debug("Downloading file content for: %s", filename)

                # Use the Office365 library's download method
                with open(local_file_path, "wb") as local_file:
                    file_item.download(local_file).execute_query()

                # Verify the download by checking file size
                if local_file_path.exists():
                    downloaded_size = local_file_path.stat().st_size
                    if downloaded_size == file_size:
                        logger.info(
                            "Successfully downloaded '%s' (%d bytes) to '%s'", filename, file_size, local_file_path
                        )
                        results[filename] = {
                            "success": True,
                            "local_path": str(local_file_path),
                            "size_bytes": file_size,
                        }
                    else:
                        error_msg = (
                            f"File '{filename}' download incomplete (expected: {file_size}, got: {downloaded_size})"
                        )
                        logger.error(error_msg)
                        # Clean up incomplete download
                        local_file_path.unlink(missing_ok=True)
                        results[filename] = {"success": False, "error": error_msg}
                else:
                    error_msg = f"File '{filename}' was not saved to local path"
                    logger.error(error_msg)
                    results[filename] = {"success": False, "error": error_msg}

            except PermissionError as e:
                error_msg = f"Permission denied accessing file '{filename}': {e}"
                logger.error(error_msg)
                results[filename] = {"success": False, "error": error_msg}
            except FileNotFoundError as e:
                error_msg = f"File '{filename}' not found: {e}"
                logger.error(error_msg)
                results[filename] = {"success": False, "error": error_msg}
            except FileDownloadError as e:
                error_msg = f"Download failed for file '{filename}': {e}"
                logger.error(error_msg)
                results[filename] = {"success": False, "error": error_msg}
            except Exception as e:
                error_msg = f"Unexpected error downloading file '{filename}': {e}"
                logger.error(error_msg)
                results[filename] = {"success": False, "error": error_msg}

        # Log summary
        successful_downloads = sum(1 for result in results.values() if result["success"])
        logger.info("Download completed: %d/%d files successful", successful_downloads, len(filenames))

        return results

    def get_file_content(self, library: str, path: list[str]) -> bytes:
        """
        Get file content as bytes from SharePoint without downloading to disk.

        This method reads a file directly from SharePoint and returns its content
        as bytes, suitable for in-memory processing of Excel files or other content.

        Args:
            library: SharePoint library name (e.g., "Documents")
            path: Path segments to the file (e.g., ["General", "Reports", "file.xlsx"])

        Returns:
            File content as bytes

        Raises:
            ConnectionError: If not connected to SharePoint
            FileNotFoundError: If file not found
            FileDownloadError: If content reading fails
            FileSizeLimitError: If file exceeds size limit

        Example:
            content = client.get_file_content(
                library="Documents",
                path=["General", "Reports", "data.xlsx"]
            )
            # content is now bytes that can be processed in memory
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        self.logger.info("Reading file content from %s: %s", library, " -> ".join(path))

        # The last element is the filename
        *folder_segments, filename = path

        # Get file item
        file_item = self._get_file_item(library, folder_segments, filename)
        if file_item is None:
            raise FileNotFoundError(f"File not found: {'/'.join(path)}", "/".join(path))

        # Check file size before downloading
        try:
            self._context.load(file_item, ["Length"])
            self._context.execute_query()
            file_size = getattr(file_item, "Length", 0)

            # Validate file size against configured limit
            max_size_bytes = self._config.max_file_size_mb * 1024 * 1024
            if file_size > max_size_bytes:
                raise FileSizeLimitError(
                    f"File size {file_size / (1024 * 1024):.1f}MB exceeds limit of {self._config.max_file_size_mb}MB",
                    file_size,
                )
        except Exception as e:
            if "FileSizeLimitError" in str(type(e)):
                raise
            self.logger.warning("Could not check file size: %s", e)

        try:
            # Use get_content() method to read file content into memory
            content_result = file_item.get_content()
            self._context.execute_query()

            # Extract bytes from the result
            content_bytes = content_result.value

            if not content_bytes:
                raise FileDownloadError(file_path="/".join(path), reason="File content is empty")

            self.logger.info("Successfully read %d bytes from file: %s", len(content_bytes), filename)
            return content_bytes

        except Exception as e:
            raise FileDownloadError(file_path="/".join(path), reason=f"Failed to read file content: {e}") from e

    def read_excel_content(
        self,
        library: str,
        path: list[str],
        sheet_name: Optional[str] = None,
        column_mapping: Optional[dict[str, str]] = None,
        skip_empty_rows: bool = True,
    ) -> list[dict[str, Any]]:
        """
        Read Excel file content directly from SharePoint and return as structured data.

        This method combines file reading and Excel processing to provide a seamless
        way to extract data from Excel files stored in SharePoint without downloading
        them to disk first.

        Args:
            library: SharePoint library name (e.g., "Documents")
            path: Path segments to the Excel file (e.g., ["General", "Reports", "data.xlsx"])
            sheet_name: Optional sheet name to read. If None, reads the first sheet.
            column_mapping: Optional dictionary to rename columns {"old_name": "new_name"}
            skip_empty_rows: Whether to skip rows where all values are empty/null

        Returns:
            List of dictionaries representing Excel rows, with column names as keys

        Raises:
            ConnectionError: If not connected to SharePoint
            FileNotFoundError: If file not found
            FileDownloadError: If content reading fails
            ValueError: If Excel processing fails

        Example:
            data = client.read_excel_content(
                library="Documents",
                path=["General", "Reports", "monthly_data.xlsx"],
                sheet_name="Summary",
                column_mapping={"Employee Name": "employee_name", "Salary": "salary"}
            )
            # data is now a list of dicts: [{"employee_name": "John", "salary": 50000}, ...]
        """
        from .excel_reader import ExcelReader

        # Get file content as bytes
        content_bytes = self.get_file_content(library, path)

        # Use ExcelReader to process the content
        excel_reader = ExcelReader()
        try:
            data = excel_reader.read_from_bytes(
                content=content_bytes,
                sheet_name=sheet_name,
                column_mapping=column_mapping,
                skip_empty_rows=skip_empty_rows,
            )

            self.logger.info("Successfully processed Excel data: %d rows from %s", len(data), path[-1])
            return data

        except Exception as e:
            self.logger.error("Failed to process Excel content: %s", e)
            raise ValueError(f"Error processing Excel file: {e}") from e

    def get_excel_sheet_names(self, library: str, path: list[str]) -> list[str]:
        """
        Get list of sheet names from an Excel file in SharePoint.

        This method reads an Excel file from SharePoint and returns the names of
        all sheets in the workbook, useful for sheet selection in read operations.

        Args:
            library: SharePoint library name (e.g., "Documents")
            path: Path segments to the Excel file (e.g., ["General", "Reports", "data.xlsx"])

        Returns:
            List of sheet names in the Excel file

        Raises:
            ConnectionError: If not connected to SharePoint
            FileNotFoundError: If file not found
            FileDownloadError: If content reading fails
            ValueError: If Excel processing fails

        Example:
            sheets = client.get_excel_sheet_names(
                library="Documents",
                path=["General", "Reports", "workbook.xlsx"]
            )
            # sheets: ["Sheet1", "Summary", "Details"]
        """
        from .excel_reader import ExcelReader

        # Get file content as bytes
        content_bytes = self.get_file_content(library, path)

        # Use ExcelReader to get sheet names
        excel_reader = ExcelReader()
        try:
            sheet_names = excel_reader.get_sheet_names_from_bytes(content_bytes)

            self.logger.info("Found %d sheets in Excel file %s: %s", len(sheet_names), path[-1], sheet_names)
            return sheet_names

        except Exception as e:
            self.logger.error("Failed to get Excel sheet names: %s", e)
            raise ValueError(f"Error reading Excel file sheets: {e}") from e

    def get_file_details(self, library_name: str, folder_path: Optional[str], filename: str) -> Optional[FileInfo]:
        """
        Get detailed information about a specific file in SharePoint.

        This method retrieves comprehensive metadata for a single file, including
        all attributes defined in the FileInfo model (name, size, dates, type, etc.).

        Args:
            library_name: Name of the document library
            folder_path: Optional relative path within the library (e.g., "General/Reports")
            filename: Name of the file to get details for

        Returns:
            FileInfo object with complete file metadata, or None if file not found

        Raises:
            ConnectionError: If not connected to SharePoint
            ValueError: If filename is empty or invalid
        """
        if not self._is_connected or self._context is None:
            raise ConnectionError(
                "Not connected to SharePoint. Call connect() first.", site_url=self._config.sharepoint_url
            )

        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")

        logger.info(
            "Getting file details for '%s' in library '%s', folder: %s", filename, library_name, folder_path or "root"
        )

        # Convert folder_path to path segments for reliable navigation
        path_segments: list[str] = []
        if folder_path:
            path_segments = [segment.strip() for segment in folder_path.split("/") if segment.strip()]

        try:
            # Get the SharePoint file item
            file_item = self._get_file_item(library_name, path_segments, filename)

            if file_item is None:
                logger.info(
                    "File '%s' not found in library '%s', path: %s", filename, library_name, folder_path or "root"
                )
                return None

            # Load user properties through the list item
            try:
                # Load the list item associated with the file
                list_item = file_item.listItemAllFields
                # Load list item with user fields explicitly
                self._context.load(list_item, ["Author", "Editor", "Created", "Modified", "AuthorId", "EditorId"])
                self._context.execute_query()

                logger.debug("Successfully loaded list item with user fields for file: %s", filename)

                # Try to resolve user IDs to user names and store them in the file item
                if hasattr(list_item, "properties") and list_item.properties:
                    # Try to get user information for AuthorId
                    if "AuthorId" in list_item.properties:
                        author_id = list_item.properties["AuthorId"]
                        try:
                            # Try to get user by ID from SharePoint
                            author_user = self._context.web.site_users.get_by_id(author_id)  # type: ignore[misc]
                            self._context.load(author_user, ["Title", "LoginName", "Email", "UserPrincipalName"])
                            self._context.execute_query()
                            logger.debug("Successfully loaded author user info for ID %s", author_id)

                            # Store the resolved author user in the file item for later access
                            file_item._resolved_author = author_user

                        except Exception as e:
                            logger.debug("Failed to load author user info for ID %s: %s", author_id, e)

                    # Try to get user information for EditorId
                    if "EditorId" in list_item.properties:
                        editor_id = list_item.properties["EditorId"]
                        try:
                            # Try to get user by ID from SharePoint
                            editor_user = self._context.web.site_users.get_by_id(editor_id)  # type: ignore[misc]
                            self._context.load(editor_user, ["Title", "LoginName", "Email", "UserPrincipalName"])
                            self._context.execute_query()
                            logger.debug("Successfully loaded editor user info for ID %s", editor_id)

                            # Store the resolved editor user in the file item for later access
                            file_item._resolved_editor = editor_user

                        except Exception as e:
                            logger.debug("Failed to load editor user info for ID %s: %s", editor_id, e)

            except Exception as e:
                logger.warning("Failed to load list item user fields for file '%s': %s", filename, e)
                # Continue without user properties - they will be None

            # Create FileInfo object using the existing helper function
            file_info = create_file_info(file_item, library_name, folder_path)

            logger.info("Successfully retrieved details for file: %s", file_info)
            return file_info

        except Exception as e:
            error_msg = (
                f"Failed to get details for file '{filename}' from library '{library_name}', "
                f"path '{folder_path or 'root'}': {e}"
            )
            logger.error(error_msg)
            raise

    def _get_file_item(self, library_name: str, path_segments: list[str], filename: str) -> Optional[Any]:
        """
        Get a specific file item from SharePoint using folder-by-folder navigation.

        This method uses the same reliable path navigation approach as other methods,
        navigating folder by folder instead of using get_by_path which can fail
        with certain folder structures.

        Args:
            library_name: Name of the document library
            path_segments: List of folder path segments (without library name)
            filename: Name of the file to retrieve

        Returns:
            SharePoint file item if found, None otherwise

        Raises:
            ConnectionError: If context is not authenticated
            Exception: If navigation fails
        """
        if not self._context:
            raise ConnectionError("SharePoint context is not authenticated")

        try:
            # Get the document library
            library = self._context.web.lists.get_by_title(library_name)
            self._context.load(library)
            self._context.execute_query()
            logger.debug("Successfully accessed library: %s", library_name)

            # Start from the library root folder
            current_folder = library.root_folder

            # Navigate folder by folder (same approach as list_excel_files_by_path_segments)
            for i, segment in enumerate(path_segments):
                logger.debug("Navigating to folder segment: '%s' (position %d)", segment, i + 1)

                try:
                    # Load folders collection for current folder
                    folders_collection = current_folder.folders
                    self._context.load(folders_collection)
                    self._context.execute_query()

                    # Find the folder with matching name
                    found_folder = None
                    for folder_item in folders_collection:
                        folder_name = getattr(folder_item, "name", None)
                        if folder_name and str(folder_name) == segment:
                            found_folder = folder_item
                            break

                    if found_folder is None:
                        raise Exception(f"Folder '{segment}' not found")

                    # Update current folder to the found folder
                    current_folder = found_folder
                    logger.debug("Successfully navigated to folder segment: %s", segment)

                except Exception as e:
                    error_msg = f"Failed to navigate to folder '{segment}' in path: {e}"
                    logger.error(error_msg)
                    raise

            # Now look for the specific file in the final folder
            logger.debug("Looking for file '%s' in final folder", filename)
            files_collection = current_folder.files
            self._context.load(files_collection)
            self._context.execute_query()

            # Find the file with matching name
            for file_item in files_collection:
                try:
                    file_name = getattr(file_item, "name", None)
                    if file_name and str(file_name) == filename:
                        logger.debug("Found file: %s", filename)
                        return file_item
                except Exception as e:
                    logger.warning("Failed to process file '%s': %s", getattr(file_item, "name", "unknown"), e)
                    continue

            # File not found
            logger.debug("File '%s' not found in the specified location", filename)
            return None

        except Exception as e:
            error_msg = (
                f"Failed to get file '{filename}' from library '{library_name}', "
                f"path '{' -> '.join(path_segments)}': {e}"
            )
            logger.error(error_msg)
            raise
