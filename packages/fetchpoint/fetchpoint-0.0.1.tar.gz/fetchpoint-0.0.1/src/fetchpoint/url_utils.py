"""
URL utilities for SharePoint path handling.

This module provides utilities for parsing SharePoint URLs and converting
them to library and folder path components.
"""

from typing import Optional, Tuple
from urllib.parse import unquote, urlparse


def parse_sharepoint_url(sharepoint_url: str) -> Tuple[str, str, Optional[str]]:
    """
    Parse a SharePoint URL into components.

    Args:
        sharepoint_url: Full SharePoint URL (e.g.,
            'https://org.sharepoint.com/sites/ProjectX/Shared%20Documents/Folder/SubFolder')

    Returns:
        Tuple of (site_url, library_name, folder_path)
        - site_url: Base site URL (e.g., 'https://org.sharepoint.com/sites/ProjectX')
        - library_name: Document library name (e.g., 'Shared Documents')
        - folder_path: Folder path within library or None if at library root

    Raises:
        ValueError: If URL format is invalid or doesn't match expected SharePoint pattern
    """
    if not sharepoint_url:
        raise ValueError("SharePoint URL cannot be empty")

    try:
        parsed = urlparse(sharepoint_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")

        # Decode URL-encoded characters
        path = unquote(parsed.path)

        # Split path into segments
        path_segments = [segment for segment in path.split("/") if segment]

        if len(path_segments) < 3:
            raise ValueError("URL must contain at least /sites/sitename/library")

        # Validate sites structure
        if path_segments[0] != "sites":
            raise ValueError("URL must contain '/sites/' segment")

        site_name = path_segments[1]
        library_name = path_segments[2]

        # Construct site URL
        site_url = f"{parsed.scheme}://{parsed.netloc}/sites/{site_name}"

        # Extract folder path if present
        folder_path = None
        if len(path_segments) > 3:
            folder_path = "/".join(path_segments[3:])

        return site_url, library_name, folder_path

    except Exception as e:
        raise ValueError(f"Failed to parse SharePoint URL '{sharepoint_url}': {e}") from e


def extract_site_url_from_sharepoint_url(sharepoint_url: str) -> str:
    """
    Extract the base site URL from a SharePoint URL.

    Args:
        sharepoint_url: Full SharePoint URL

    Returns:
        Base site URL (e.g., 'https://org.sharepoint.com/sites/ProjectX')

    Raises:
        ValueError: If URL format is invalid
    """
    site_url, _, _ = parse_sharepoint_url(sharepoint_url)
    return site_url


def validate_same_site(urls: list[str]) -> bool:
    """
    Validate that all URLs belong to the same SharePoint site.

    Args:
        urls: List of SharePoint URLs to validate

    Returns:
        True if all URLs belong to the same site, False otherwise

    Raises:
        ValueError: If any URL is invalid
    """
    if not urls:
        return True

    try:
        base_site = extract_site_url_from_sharepoint_url(urls[0])

        for url in urls[1:]:
            site_url = extract_site_url_from_sharepoint_url(url)
            if site_url != base_site:
                return False

        return True

    except ValueError:
        # Re-raise ValueError for invalid URLs
        raise


def sharepoint_url_to_path_segments(sharepoint_url: str) -> list[str]:
    """
    Convert SharePoint URL to path segments for backward compatibility.

    Args:
        sharepoint_url: Full SharePoint URL

    Returns:
        List of path segments [library_name, folder1, folder2, ...]

    Raises:
        ValueError: If URL format is invalid
    """
    _, library_name, folder_path = parse_sharepoint_url(sharepoint_url)

    segments = [library_name]
    if folder_path:
        segments.extend(folder_path.split("/"))

    return segments
