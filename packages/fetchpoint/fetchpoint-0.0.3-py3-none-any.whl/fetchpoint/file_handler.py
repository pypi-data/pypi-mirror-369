"""
File handling operations for SharePoint integration.

This module provides functions for listing and processing files from SharePoint
document libraries, with optimized support for Excel files and comprehensive
metadata extraction.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext  # type: ignore[import-untyped]

from .exceptions import ConnectionError, LibraryNotFoundError
from .models import FileInfo, FileType

# Configure logger for this module
logger = logging.getLogger(__name__)


def list_files_in_library(
    context: "ClientContext", library_name: str = "Documents", folder_path: Optional[str] = None
) -> list[FileInfo]:
    """
    List all Excel files in a SharePoint document library.

    This function retrieves all files from the specified library and folder,
    filters them by Excel extensions, and returns FileInfo objects with metadata.

    Args:
        context: Authenticated SharePoint client context
        library_name: Name of the document library (default: "Documents")
        folder_path: Optional relative path within the library (e.g., "General/13_AMS")

    Returns:
        List of FileInfo objects for Excel files found

    Raises:
        ConnectionError: If context is not authenticated
        FileOperationError: If library access fails
    """
    logger.info("Listing files in library '%s', folder: %s", library_name, folder_path or "root")

    if not context:
        raise ConnectionError("SharePoint context is not authenticated")

    try:
        # Get the document library
        library = context.web.lists.get_by_title(library_name)

        # Determine the folder to query
        if folder_path:
            # Navigate to specific folder
            folder = library.root_folder.folders.get_by_path(folder_path)  # type: ignore[misc]
            items_query = folder.files
        else:
            # Query root of library
            items_query = library.root_folder.files

        # Load files with metadata
        context.load(items_query)
        context.execute_query()

        # Process files and filter by Excel extensions
        excel_files: list[FileInfo] = []
        for file_item in items_query:
            try:
                # Check if file has Excel extension and name is not None
                file_name = getattr(file_item, "name", None)
                if file_name and _is_excel_file(str(file_name)):
                    file_info = create_file_info(file_item, library_name, folder_path)
                    excel_files.append(file_info)
                    logger.debug("Found Excel file: %s", file_info.name)

            except Exception as e:
                logger.warning("Failed to process file '%s': %s", getattr(file_item, "name", "unknown"), e)
                continue

        logger.info("Found %d Excel files in library '%s'", len(excel_files), library_name)
        return excel_files

    except Exception as e:
        error_msg = f"Failed to list files in library '{library_name}'"
        if folder_path:
            error_msg += f", folder '{folder_path}'"
        error_msg += f": {e}"

        logger.error(error_msg)
        raise LibraryNotFoundError(library_name) from e


def list_folders_in_library(
    context: "ClientContext", library_name: str = "Documents", folder_path: Optional[str] = None
) -> list[str]:
    """
    List all folders in a SharePoint document library.

    This function retrieves folder names from the specified library and path,
    useful for navigation and understanding the library structure.

    Args:
        context: Authenticated SharePoint client context
        library_name: Name of the document library (default: "Documents")
        folder_path: Optional relative path within the library

    Returns:
        List of folder names found

    Raises:
        ConnectionError: If context is not authenticated
        FileOperationError: If library access fails
    """
    logger.info("Listing folders in library '%s', folder: %s", library_name, folder_path or "root")

    if not context:
        raise ConnectionError("SharePoint context is not authenticated")

    try:
        # Get the document library
        library = context.web.lists.get_by_title(library_name)

        # Determine the folder to query
        if folder_path:
            # Navigate to specific folder
            folder = library.root_folder.folders.get_by_path(folder_path)  # type: ignore[misc]
            folders_query = folder.folders
        else:
            # Query root of library
            folders_query = library.root_folder.folders

        # Load folders
        context.load(folders_query)
        context.execute_query()

        # Extract folder names with type safety
        folder_names: list[str] = []
        for folder_item in folders_query:
            folder_name = getattr(folder_item, "name", None)
            if folder_name:
                folder_names.append(str(folder_name))
                logger.debug("Found folder: %s", folder_name)

        logger.info("Found %d folders in library '%s'", len(folder_names), library_name)
        return folder_names

    except Exception as e:
        error_msg = f"Failed to list folders in library '{library_name}'"
        if folder_path:
            error_msg += f", folder '{folder_path}'"
        error_msg += f": {e}"

        logger.error(error_msg)
        raise LibraryNotFoundError(library_name) from e


def list_excel_files_by_path_segments(
    context: "ClientContext", library_name: str, path_segments: list[str]
) -> list[str]:
    """
    List Excel file names using folder-by-folder navigation.

    This function uses the same reliable path navigation approach as PathResolver,
    navigating folder by folder instead of using get_by_path which can fail
    with certain folder structures.

    Args:
        context: Authenticated SharePoint client context
        library_name: Name of the document library
        path_segments: List of folder path segments (without library name)

    Returns:
        List of Excel file names found in the target folder

    Raises:
        ConnectionError: If context is not authenticated
        LibraryNotFoundError: If library or folder cannot be found
    """
    logger.info("Listing Excel files using path segments: %s -> %s", library_name, " -> ".join(path_segments))

    if not context:
        raise ConnectionError("SharePoint context is not authenticated")

    try:
        # Get the document library
        library = context.web.lists.get_by_title(library_name)
        context.load(library)
        context.execute_query()
        logger.debug("Successfully accessed library: %s", library_name)

        # Start from the library root folder
        current_folder = library.root_folder

        # Navigate folder by folder (same approach as PathResolver)
        for i, segment in enumerate(path_segments):
            logger.debug("Navigating to folder segment: '%s' (position %d)", segment, i + 1)

            try:
                # Load folders collection for current folder
                folders_collection = current_folder.folders
                context.load(folders_collection)
                context.execute_query()

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
                raise LibraryNotFoundError(library_name) from e

        # Now list files from the final folder
        logger.debug("Listing files from final folder")
        files_collection = current_folder.files
        context.load(files_collection)
        context.execute_query()

        # Process files and filter by Excel extensions
        excel_file_names: list[str] = []
        for file_item in files_collection:
            try:
                file_name = getattr(file_item, "name", None)
                if file_name and _is_excel_file(str(file_name)):
                    excel_file_names.append(str(file_name))
                    logger.debug("Found Excel file: %s", file_name)

            except Exception as e:
                logger.warning("Failed to process file '%s': %s", getattr(file_item, "name", "unknown"), e)
                continue

        logger.info(
            "Found %d Excel files in path %s -> %s", len(excel_file_names), library_name, " -> ".join(path_segments)
        )
        return excel_file_names

    except Exception as e:
        error_msg = f"Failed to list Excel files in library '{library_name}', path '{' -> '.join(path_segments)}': {e}"
        logger.error(error_msg)
        raise LibraryNotFoundError(library_name) from e


def _is_excel_file(filename: str) -> bool:
    """
    Check if a file has a supported Excel extension.

    Args:
        filename: Name of the file to check

    Returns:
        True if file has Excel extension, False otherwise
    """
    if not filename:
        return False

    # Get file extension in lowercase
    extension = filename.lower().split(".")[-1] if "." in filename else ""

    # Check against supported Excel extensions
    excel_extensions = {ft.value.lstrip(".") for ft in FileType}
    return extension in excel_extensions


def _safe_get_dict_value(obj: Any, key: str) -> Any:
    """
    Safely get a value from a dictionary-like object.

    Args:
        obj: Object that may be a dictionary
        key: Key to look up

    Returns:
        Value if found, None otherwise
    """
    try:
        if hasattr(obj, "get") and callable(getattr(obj, "get")):
            return obj.get(key)  # type: ignore[misc]
        elif hasattr(obj, "__getitem__"):
            return obj[key]  # type: ignore[misc]
        else:
            return None
    except (KeyError, TypeError, AttributeError):
        return None


def _safe_str_conversion(value: Any) -> Optional[str]:
    """
    Safely convert a value to string, handling None and empty values.

    Args:
        value: Value to convert

    Returns:
        String representation if valid, None otherwise
    """
    if value is None:
        return None

    try:
        str_value = str(value)
        return str_value.strip() if str_value.strip() else None
    except (TypeError, AttributeError):
        return None


def _extract_user_info_from_dict(user_dict: Any) -> Optional[str]:
    """
    Extract user information from a dictionary-like object.

    Args:
        user_dict: Dictionary containing user information

    Returns:
        User string if found, None otherwise
    """
    if not user_dict:
        return None

    # Try to get user info from common SharePoint user properties
    title = _safe_get_dict_value(user_dict, "Title")
    if title:
        title_str = _safe_str_conversion(title)
        if title_str:
            return title_str

    email = _safe_get_dict_value(user_dict, "Email")
    if email:
        email_str = _safe_str_conversion(email)
        if email_str:
            return email_str

    login_name = _safe_get_dict_value(user_dict, "LoginName")
    if login_name:
        login_str = _safe_str_conversion(login_name)
        if login_str:
            return login_str

    return None


def create_file_info(file_item: Any, library_name: str, folder_path: Optional[str] = None) -> FileInfo:
    """
    Create FileInfo object from SharePoint file item.

    Args:
        file_item: SharePoint file object
        library_name: SharePoint library name containing the file
        folder_path: Optional folder path for relative path construction

    Returns:
        FileInfo object with populated metadata

    Raises:
        ValueError: If file metadata is invalid
    """
    # Construct relative path
    if folder_path:
        relative_path = f"{folder_path}/{file_item.name}"
    else:
        relative_path = file_item.name

    # Parse file extension to determine FileType
    extension = "." + file_item.name.lower().split(".")[-1] if "." in file_item.name else ""
    file_type = FileType(extension)

    # Convert SharePoint datetime to Python datetime
    # SharePoint typically provides datetime as string or datetime object
    modified_date = file_item.time_last_modified
    if isinstance(modified_date, str):
        # Parse ISO format datetime string
        modified_date = datetime.fromisoformat(modified_date.replace("Z", "+00:00"))

    # Handle created date conversion
    created_date = getattr(file_item, "time_created", None)
    if created_date and isinstance(created_date, str):
        try:
            created_date = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            created_date = None

    # Extract Created By user information
    # SharePoint provides user info through Author field for created by
    # Try multiple possible property names and access patterns
    created_by_str = None

    # First, try to get user info from resolved user objects (most reliable)
    if hasattr(file_item, "_resolved_author"):
        try:
            resolved_author = file_item._resolved_author
            logger.debug("Found resolved author: %s", resolved_author)

            # Try to extract user name from resolved author
            if hasattr(resolved_author, "title") and resolved_author.title and str(resolved_author.title).strip():
                created_by_str = str(resolved_author.title)
                logger.debug("Got created_by from resolved author title: %s", created_by_str)
            elif (
                hasattr(resolved_author, "login_name")
                and resolved_author.login_name
                and str(resolved_author.login_name).strip()
            ):
                created_by_str = str(resolved_author.login_name)
                logger.debug("Got created_by from resolved author login_name: %s", created_by_str)
            elif hasattr(resolved_author, "email") and resolved_author.email and str(resolved_author.email).strip():
                created_by_str = str(resolved_author.email)
                logger.debug("Got created_by from resolved author email: %s", created_by_str)
            elif (
                hasattr(resolved_author, "user_principal_name")
                and resolved_author.user_principal_name
                and str(resolved_author.user_principal_name).strip()
            ):
                created_by_str = str(resolved_author.user_principal_name)
                logger.debug("Got created_by from resolved author UPN: %s", created_by_str)
            else:
                logger.debug("Resolved author has no accessible properties")

        except Exception as e:
            logger.debug("Exception accessing resolved author: %s", e)

    # If not found from resolved user, try to get user info from list item properties
    if not created_by_str and hasattr(file_item, "listItemAllFields"):
        try:
            list_item = file_item.listItemAllFields
            if hasattr(list_item, "properties") and list_item.properties:
                logger.debug("List item has properties available")

                # Log all properties to see what's available (safely handle unknown types)
                try:
                    if hasattr(list_item.properties, "items"):
                        for key, value in list_item.properties.items():
                            # Use safe string conversion for logging
                            value_type_str = str(type(value).__name__)
                            logger.debug("List item property: %s = %s (type: %s)", key, value, value_type_str)
                except Exception as e:
                    logger.debug("Could not iterate list item properties: %s", e)

                # Try to get Author from list item properties
                author_list_prop = _safe_get_dict_value(list_item.properties, "Author")
                if author_list_prop:
                    # Use safe string conversion for logging
                    prop_type_str = str(type(author_list_prop).__name__)
                    logger.debug("Author from list item: %s (type: %s)", author_list_prop, prop_type_str)

                    # Handle different types of Author property
                    if isinstance(author_list_prop, dict):
                        # Extract user info from dictionary using safe methods
                        created_by_str = _extract_user_info_from_dict(author_list_prop)
                    elif hasattr(author_list_prop, "Title"):
                        # User object with Title property
                        created_by_str = _safe_str_conversion(author_list_prop.Title)
                    elif hasattr(author_list_prop, "title"):
                        # User object with title property
                        created_by_str = _safe_str_conversion(author_list_prop.title)
                    else:
                        # Fallback to string representation
                        created_by_str = _safe_str_conversion(author_list_prop)
                        # Don't use generic object representations
                        if created_by_str == "SP.User":
                            created_by_str = None

                    logger.debug("Extracted created_by from list item: %s", created_by_str)

                # If no Author property, try AuthorId
                if not created_by_str:
                    author_id = _safe_get_dict_value(list_item.properties, "AuthorId")
                    if author_id:
                        # Use safe string conversion for logging
                        id_type_str = str(type(author_id).__name__)
                        logger.debug("Found AuthorId: %s (type: %s)", author_id, id_type_str)
                        # For now, just use the ID as fallback
                        created_by_str = f"User ID: {author_id}" if author_id else None
                        logger.debug("Using AuthorId as created_by: %s", created_by_str)

        except Exception as e:
            logger.debug("Exception accessing Author from list item: %s", e)

    # If not found in list item, try the file item author object
    if not created_by_str:
        # First, try to debug what's actually available
        logger.debug("Debugging file_item properties: %s", dir(file_item))
        if hasattr(file_item, "properties"):
            logger.debug(
                "File item properties keys: %s",
                list(file_item.properties.keys()) if hasattr(file_item.properties, "keys") else "No keys method",
            )

        # Try different ways to access author information
        author_obj = getattr(file_item, "author", None)
        if not author_obj:
            # Try alternative property names
            author_obj = getattr(file_item, "created_by", None)

        if author_obj:
            # Use safe string conversion for logging
            obj_type_str = str(type(author_obj).__name__)
            logger.debug("Author object type: %s, dir: %s", obj_type_str, dir(author_obj))
            logger.debug("Author object properties dict: %s", getattr(author_obj, "properties", "No properties"))

            # Try to ensure properties are loaded
            try:
                if hasattr(author_obj, "ensure_property"):
                    author_obj.ensure_property("Title")
                    author_obj.ensure_property("LoginName")
                    author_obj.ensure_property("Email")
                    author_obj.ensure_property("UserPrincipalName")
                    logger.debug("Ensured author properties")
            except Exception as e:
                logger.debug("Failed to ensure author properties: %s", e)

            # Check properties after ensuring them
            logger.debug("Author title: %s", getattr(author_obj, "title", "No title"))
            logger.debug("Author login_name: %s", getattr(author_obj, "login_name", "No login_name"))
            logger.debug("Author email: %s", getattr(author_obj, "email", "No email"))
            logger.debug("Author user_principal_name: %s", getattr(author_obj, "user_principal_name", "No UPN"))

            # Try to access properties directly through the _properties dict
            if hasattr(author_obj, "_properties"):
                logger.debug("Author _properties: %s", author_obj._properties)

            # Try to extract string representation from SharePoint User object
            # Check for non-empty values before using them
            if hasattr(author_obj, "title") and author_obj.title:
                created_by_str = _safe_str_conversion(author_obj.title)
            elif hasattr(author_obj, "login_name") and author_obj.login_name:
                created_by_str = _safe_str_conversion(author_obj.login_name)
            elif hasattr(author_obj, "email") and author_obj.email:
                created_by_str = _safe_str_conversion(author_obj.email)
            elif hasattr(author_obj, "user_principal_name") and author_obj.user_principal_name:
                created_by_str = _safe_str_conversion(author_obj.user_principal_name)
            else:
                # Try to get properties from the user object
                if hasattr(author_obj, "properties") and author_obj.properties:
                    logger.debug("Author properties: %s", author_obj.properties)
                    # Try common SharePoint user property names
                    for prop_name in ["Title", "Name", "LoginName", "Email", "UserPrincipalName"]:
                        prop_value = _safe_get_dict_value(author_obj.properties, prop_name)
                        if prop_value:
                            created_by_str = _safe_str_conversion(prop_value)
                            if created_by_str:
                                break

                # Try to access from _properties if available
                if not created_by_str and hasattr(author_obj, "_properties"):
                    for prop_name in ["Title", "Name", "LoginName", "Email", "UserPrincipalName"]:
                        prop_value = _safe_get_dict_value(author_obj._properties, prop_name)
                        if prop_value:
                            created_by_str = _safe_str_conversion(prop_value)
                            if created_by_str:
                                break

                # Fallback to string representation if object exists but no known properties
                if not created_by_str:
                    created_by_str = _safe_str_conversion(author_obj)

        # Try to get author from properties dictionary as fallback
        if not created_by_str and hasattr(file_item, "properties"):
            try:
                # SharePoint sometimes stores user info in properties
                author_prop = _safe_get_dict_value(file_item.properties, "Author")
                if author_prop:
                    logger.debug("Author property from file_item: %s", author_prop)
                    if isinstance(author_prop, dict):
                        # Extract user info from dictionary using safe methods
                        created_by_str = _extract_user_info_from_dict(author_prop)
                    else:
                        created_by_str = _safe_str_conversion(author_prop)
            except Exception as e:
                logger.debug("Exception accessing Author from properties: %s", e)

    # Extract Modified By user information
    # SharePoint provides user info through ModifiedBy field
    modified_by_str = None

    # First, try to get user info from resolved user objects (most reliable)
    if hasattr(file_item, "_resolved_editor"):
        try:
            resolved_editor = file_item._resolved_editor
            logger.debug("Found resolved editor: %s", resolved_editor)

            # Try to extract user name from resolved editor
            if hasattr(resolved_editor, "title") and resolved_editor.title:
                modified_by_str = _safe_str_conversion(resolved_editor.title)
                logger.debug("Got modified_by from resolved editor title: %s", modified_by_str)
            elif hasattr(resolved_editor, "login_name") and resolved_editor.login_name:
                modified_by_str = _safe_str_conversion(resolved_editor.login_name)
                logger.debug("Got modified_by from resolved editor login_name: %s", modified_by_str)
            elif hasattr(resolved_editor, "email") and resolved_editor.email:
                modified_by_str = _safe_str_conversion(resolved_editor.email)
                logger.debug("Got modified_by from resolved editor email: %s", modified_by_str)
            elif hasattr(resolved_editor, "user_principal_name") and resolved_editor.user_principal_name:
                modified_by_str = _safe_str_conversion(resolved_editor.user_principal_name)
                logger.debug("Got modified_by from resolved editor UPN: %s", modified_by_str)
            else:
                logger.debug("Resolved editor has no accessible properties")

        except Exception as e:
            logger.debug("Exception accessing resolved editor: %s", e)

    # If not found from resolved user, try other methods
    if not modified_by_str:
        # Try to get modified by from properties dictionary as fallback
        if hasattr(file_item, "properties"):
            try:
                # SharePoint sometimes stores user info in properties
                editor_prop = _safe_get_dict_value(file_item.properties, "Editor")
                if editor_prop:
                    if isinstance(editor_prop, dict):
                        # Extract user info from dictionary using safe methods
                        modified_by_str = _extract_user_info_from_dict(editor_prop)
                    else:
                        modified_by_str = _safe_str_conversion(editor_prop)

                if not modified_by_str:
                    modified_prop = _safe_get_dict_value(file_item.properties, "ModifiedBy")
                    if modified_prop:
                        if isinstance(modified_prop, dict):
                            # Extract user info from dictionary using safe methods
                            modified_by_str = _extract_user_info_from_dict(modified_prop)
                        else:
                            modified_by_str = _safe_str_conversion(modified_prop)
            except Exception:
                pass

    # Create FileInfo object
    return FileInfo(
        name=file_item.name,
        library=library_name,
        relative_path=relative_path,
        size_bytes=file_item.length,
        modified_date=modified_date,
        file_type=file_type,
        created_date=created_date,
        created_by=created_by_str,
        modified_by=modified_by_str,
    )
