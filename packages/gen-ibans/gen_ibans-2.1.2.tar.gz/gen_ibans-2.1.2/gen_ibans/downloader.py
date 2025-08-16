"""
Bundesbank Data Downloader Module

This module provides functionality to download bank data from the Deutsche Bundesbank
official website when no local data file is provided.

Copyright (c) 2025 Sebastian Wallat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import tempfile
import urllib.request
import urllib.parse
import re
import json
from pathlib import Path
from typing import Optional
import time


class BundesbankDownloader:
    """Downloads bank data from Deutsche Bundesbank official website."""

    # Bundesbank download page URL
    INDEX_URL = (
        "https://www.bundesbank.de/de/aufgaben/"
        "unbarer-zahlungsverkehr/serviceangebot/"
        "bankleitzahlen/download-bankleitzahlen-602592"
    )

    # Fallback URLs (in case scraping fails)
    FALLBACK_URLS = {
        "csv": "https://www.bundesbank.de/resource/blob/602592/4f3ba1d2fb3aa8de9c5e71c6cc3f6e59/mL/bankleitzahlen-csv-data.zip",
        "txt": "https://www.bundesbank.de/resource/blob/602592/4f3ba1d2fb3aa8de9c5e71c6cc3f6e59/mL/bankleitzahlen-txt-data.zip",
        "xml": "https://www.bundesbank.de/resource/blob/602592/4f3ba1d2fb3aa8de9c5e71c6cc3f6e59/mL/bankleitzahlen-xml-data.zip",
    }

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the downloader.

        Args:
            cache_dir: Directory to cache downloaded files. If None, uses system temp directory.
        """
        if cache_dir is None:
            cache_dir = os.path.join(tempfile.gettempdir(), "bundesbank_data")

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, format_type: str) -> Path:
        """Get the cache file path for a specific format."""
        return self.cache_dir / f"bundesbank_data.{format_type}"

    def _get_cache_metadata_path(self, format_type: str) -> Path:
        """Get the cache metadata file path for a specific format."""
        return self.cache_dir / f"bundesbank_data.{format_type}.meta"

    def _save_cache_metadata(
        self, format_type: str, etag: str = None, last_modified: str = None
    ) -> None:
        """Save cache metadata (ETag, Last-Modified, etc.) to file."""
        metadata_path = self._get_cache_metadata_path(format_type)
        metadata = {
            "timestamp": time.time(),
            "etag": etag,
            "last_modified": last_modified,
        }

        try:
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            # If metadata save fails, don't break the main functionality
            pass

    def _load_cache_metadata(self, format_type: str) -> dict:
        """Load cache metadata from file."""
        metadata_path = self._get_cache_metadata_path(format_type)

        if not metadata_path.exists():
            return {}

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _get_remote_etag(self, format_type: str) -> str:
        """Get ETag from remote file without downloading."""
        try:
            url = self._resolve_url(format_type)
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.headers.get("ETag", "").strip('"')
        except Exception:
            return None

    def _is_cache_valid(
        self,
        cache_path: Path,
        format_type: str,
        max_age_hours: int = 24,
        check_version: bool = True,
    ) -> bool:
        """
        Check if cached file is still valid (not too old and up-to-date).

        Args:
            cache_path: Path to cached file
            format_type: File format for metadata lookup
            max_age_hours: Maximum age in hours before forcing refresh
            check_version: Whether to check for newer versions online

        Returns:
            True if cache is valid, False otherwise
        """
        if not cache_path.exists():
            return False

        # Check file age first (quick check)
        file_age = time.time() - cache_path.stat().st_mtime
        max_age_seconds = max_age_hours * 3600

        # If file is too old, it's invalid regardless of version
        if file_age >= max_age_seconds:
            return False

        # If version checking is disabled, rely only on age
        if not check_version:
            return True

        # Check if we have a newer version available online
        try:
            metadata = self._load_cache_metadata(format_type)
            cached_etag = metadata.get("etag")

            # If we don't have cached ETag, assume cache is valid for now
            # (to avoid excessive network calls)
            if not cached_etag:
                return True

            # Get current ETag from remote server
            remote_etag = self._get_remote_etag(format_type)

            # If we can't get remote ETag, assume cache is valid
            if not remote_etag:
                return True

            # If ETags differ, we have a newer version available
            return cached_etag == remote_etag

        except Exception:
            # If version check fails, fall back to age-based validation
            return True

    def _resolve_url(self, format_type: str) -> str:
        """
        Resolve the current download URL by scraping the Bundesbank page.

        Args:
            format_type: File format (csv, txt, xml)

        Returns:
            Current download URL for the specified format

        Raises:
            Exception: If URL resolution fails
        """
        try:
            with urllib.request.urlopen(self.INDEX_URL, timeout=10) as resp:
                html = resp.read().decode("utf-8", "ignore")

            # Look for download links in the HTML
            pattern = rf"href=\"([^\"]+blz-aktuell-{format_type}-zip-data\.zip)\""
            match = re.search(pattern, html, re.IGNORECASE)

            if match:
                relative_url = match.group(1)
                return urllib.parse.urljoin(self.INDEX_URL, relative_url)
            else:
                # Try fallback URL
                if format_type in self.FALLBACK_URLS:
                    return self.FALLBACK_URLS[format_type]
                else:
                    raise RuntimeError(f"No {format_type} download link found")

        except Exception as e:
            # Use fallback URL if scraping fails
            if format_type in self.FALLBACK_URLS:
                return self.FALLBACK_URLS[format_type]
            else:
                raise Exception(f"Failed to resolve download URL: {e}")

    def _download_and_extract(self, url: str, format_type: str) -> str:
        """
        Download and extract data file from Bundesbank.

        Args:
            url: Download URL
            format_type: File format (csv, txt, xml)

        Returns:
            Path to the extracted file

        Raises:
            Exception: If download or extraction fails
        """
        try:
            # Create a temporary file for the zip download
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
                temp_zip_path = temp_zip.name

            # Download the zip file and capture headers
            etag = None
            last_modified = None
            try:
                with urllib.request.urlopen(url, timeout=30) as response:
                    etag = response.headers.get("ETag", "").strip('"')
                    last_modified = response.headers.get("Last-Modified", "")

                    with open(temp_zip_path, "wb") as temp_file:
                        temp_file.write(response.read())
            except Exception:
                # Fallback to simple download if headers fail
                urllib.request.urlretrieve(url, temp_zip_path)

            # Extract the zip file
            import zipfile

            with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
                # List all files in zip for debugging
                all_files = zip_ref.namelist()

                # Find the data file in the zip - be flexible with extensions
                data_files = []
                for filename in all_files:
                    # Check for exact extension match first
                    if filename.lower().endswith(f".{format_type}"):
                        data_files.append(filename)
                    # Also check for files that contain the format type
                    elif format_type in filename.lower() and (
                        filename.lower().endswith(".txt")
                        or filename.lower().endswith(".csv")
                        or filename.lower().endswith(".xml")
                    ):
                        data_files.append(filename)

                if not data_files:
                    # If no files found, raise error with available files info
                    raise ValueError(
                        f"No {format_type} file found in downloaded archive. "
                        f"Available files: {', '.join(all_files)}"
                    )

                # Extract the first matching file
                data_file = data_files[0]
                extracted_path = self.cache_dir / f"bundesbank_data.{format_type}"

                with zip_ref.open(data_file) as source:
                    with open(extracted_path, "wb") as target:
                        target.write(source.read())

            # Save metadata if we captured it
            if etag or last_modified:
                self._save_cache_metadata(format_type, etag, last_modified)

            # Clean up temporary zip file
            os.unlink(temp_zip_path)

            return str(extracted_path)

        except Exception as e:
            # Clean up on error
            if "temp_zip_path" in locals() and os.path.exists(temp_zip_path):
                os.unlink(temp_zip_path)
            raise Exception(f"Failed to download Bundesbank data: {e}")

    def get_data_file(
        self,
        format_type: str = "csv",
        force_download: bool = False,
        max_cache_age_hours: int = 24,
        check_version: bool = True,
    ) -> str:
        """
        Get bank data file, downloading if necessary.

        Args:
            format_type: Preferred format (csv, txt, xml)
            force_download: Force re-download even if cache is valid
            max_cache_age_hours: Maximum age of cached file in hours
            check_version: Whether to check for newer versions online

        Returns:
            Path to the data file

        Raises:
            ValueError: If format_type is not supported
            Exception: If download fails
        """
        if format_type not in ["csv", "txt", "xml"]:
            raise ValueError(
                f"Unsupported format: {format_type}. Supported formats: csv, txt, xml"
            )

        cache_path = self._get_cache_path(format_type)

        # Check if we can use cached file
        if not force_download and self._is_cache_valid(
            cache_path, format_type, max_cache_age_hours, check_version
        ):
            return str(cache_path)

        # Download fresh data
        url = self._resolve_url(format_type)
        return self._download_and_extract(url, format_type)

    def clear_cache(self) -> None:
        """Clear all cached data files."""
        for file in self.cache_dir.glob("bundesbank_data.*"):
            file.unlink()

    def get_cache_info(self) -> dict:
        """Get information about cached files."""
        info = {}
        for format_type in ["csv", "txt", "xml"]:
            cache_path = self._get_cache_path(format_type)
            if cache_path.exists():
                stat = cache_path.stat()
                metadata = self._load_cache_metadata(format_type)
                info[format_type] = {
                    "path": str(cache_path),
                    "size": stat.st_size,
                    "modified": time.ctime(stat.st_mtime),
                    "age_hours": (time.time() - stat.st_mtime) / 3600,
                    "etag": metadata.get("etag", "N/A"),
                    "last_modified": metadata.get("last_modified", "N/A"),
                }
        return info


def download_bundesbank_data(
    format_type: str = "csv",
    force_download: bool = False,
    cache_dir: Optional[str] = None,
    check_version: bool = True,
) -> str:
    """
    Convenience function to download Bundesbank data.

    Args:
        format_type: File format to download (csv, txt, xml)
        force_download: Force re-download even if cache is valid
        cache_dir: Cache directory path
        check_version: Whether to check for newer versions online

    Returns:
        Path to the downloaded data file
    """
    downloader = BundesbankDownloader(cache_dir)
    return downloader.get_data_file(
        format_type, force_download, check_version=check_version
    )
