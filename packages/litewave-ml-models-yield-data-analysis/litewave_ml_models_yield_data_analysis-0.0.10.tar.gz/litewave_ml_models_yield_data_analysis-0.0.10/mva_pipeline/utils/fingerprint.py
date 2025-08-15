"""Fingerprinting utilities for MVA pipeline caching.

This module provides functions to compute fingerprints of Parquet files
to detect when data has changed and analytics need to be re-run.
"""

import hashlib
from pathlib import Path
from typing import List, Tuple


def parquet_fingerprint(raw_dir: Path) -> str:
    """Compute a fingerprint for all Parquet files in a directory.

    For every *.parquet file, collect filename|mtime|size, sort the entries,
    and compute a SHA1 hash of the concatenated string.

    Args:
        raw_dir: Directory containing Parquet files

    Returns:
        SHA1 hash string representing the fingerprint of all Parquet files

    Raises:
        FileNotFoundError: If raw_dir doesn't exist
        OSError: If there are permission issues accessing files
    """
    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory does not exist: {raw_dir}")

    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw directory path is not a directory: {raw_dir}")

    # Collect file information for all Parquet files
    file_info: List[Tuple[str, float, int]] = []

    for parquet_file in raw_dir.glob("*.parquet"):
        try:
            stat = parquet_file.stat()
            file_info.append((parquet_file.name, stat.st_mtime, stat.st_size))
        except OSError as e:
            print(f"WARNING: Could not stat file {parquet_file}: {e}")
            continue

    if not file_info:
        # No Parquet files found - return hash of empty string
        return hashlib.sha1(b"").hexdigest()

    # Sort by filename for consistent ordering
    file_info.sort(key=lambda x: x[0])

    # Create concatenated string: filename|mtime|size for each file
    fingerprint_parts = []
    for filename, mtime, size in file_info:
        fingerprint_parts.append(f"{filename}|{mtime:.6f}|{size}")

    # Join all parts and compute SHA1 hash
    fingerprint_string = "\n".join(fingerprint_parts)
    fingerprint_bytes = fingerprint_string.encode("utf-8")

    return hashlib.sha1(fingerprint_bytes).hexdigest()


def fingerprint_summary(raw_dir: Path) -> dict:
    """Get a summary of the fingerprint computation for debugging.

    Args:
        raw_dir: Directory containing Parquet files

    Returns:
        Dictionary with fingerprint details including file count and individual file info
    """
    if not raw_dir.exists():
        return {"error": f"Directory does not exist: {raw_dir}"}

    file_details = []
    total_size = 0

    for parquet_file in raw_dir.glob("*.parquet"):
        try:
            stat = parquet_file.stat()
            file_details.append(
                {
                    "filename": parquet_file.name,
                    "mtime": stat.st_mtime,
                    "size": stat.st_size,
                    "mtime_readable": parquet_file.stat().st_mtime,
                }
            )
            total_size += stat.st_size
        except OSError as e:
            file_details.append({"filename": parquet_file.name, "error": str(e)})

    # Sort by filename for consistency
    file_details.sort(key=lambda x: x.get("filename", ""))

    fingerprint = parquet_fingerprint(raw_dir)

    return {
        "fingerprint": fingerprint,
        "file_count": len([f for f in file_details if "error" not in f]),
        "total_size_bytes": total_size,
        "raw_dir": str(raw_dir),
        "file_details": file_details,
    }
