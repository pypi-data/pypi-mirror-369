"""State management for MVA pipeline caching.

This module provides functions to get and set fingerprints for tracking
when the pipeline needs to re-run analytics based on data changes.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional

from .redis_manager import get_redis_manager, is_redis_enabled

logger = logging.getLogger(__name__)


def get_last_fingerprint(
    raw_dir: Path, config: Optional[dict] = None, redis_url: Optional[str] = None
) -> Optional[str]:
    """Get the last computed fingerprint for the given raw data directory.

    Args:
        raw_dir: Path to the raw data directory
        config: Configuration dictionary (optional)

    Returns:
        The last fingerprint string, or None if not found
    """
    # Try Redis first if enabled
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager(redis_url=redis_url)
            # Use path-specific Redis key to support multi-tenant scenarios
            redis_key = _get_redis_key(raw_dir)
            fingerprint = redis_manager.redis_client.get(redis_key)
            if fingerprint:
                return fingerprint
        except Exception as e:
            logger.warning(f"WARNING: Could not read fingerprint from Redis: {e}")

    # Fallback to file-based storage
    state_file = _get_state_file_path(raw_dir, config)
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state_data = json.load(f)
                return state_data.get("last_fingerprint")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"WARNING: Could not read state file {state_file}: {e}")

    return None


def set_last_fingerprint(
    fingerprint: str,
    raw_dir: Path,
    config: Optional[dict] = None,
    redis_url: Optional[str] = None,
) -> None:
    """Set the last computed fingerprint for the given raw data directory.

    Args:
        fingerprint: The fingerprint string to store
        raw_dir: Path to the raw data directory
        config: Configuration dictionary (optional)
    """
    # Try Redis first if enabled
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager(redis_url=redis_url)
            # Use path-specific Redis key to support multi-tenant scenarios
            redis_key = _get_redis_key(raw_dir)
            redis_manager.redis_client.set(redis_key, fingerprint)
            logger.info(
                f"INFO: Stored fingerprint in Redis ({redis_key}): {fingerprint[:16]}..."
            )
        except Exception as e:
            logger.warning(f"WARNING: Could not store fingerprint in Redis: {e}")

    # Always also store in file as backup
    state_file = _get_state_file_path(raw_dir, config)
    state_data = {}

    # Read existing data if file exists
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            state_data = {}

    # Update fingerprint
    state_data["last_fingerprint"] = fingerprint

    # Write back to file
    try:
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2)
        logger.info(f"INFO: Stored fingerprint in state file: {state_file}")
    except OSError as e:
        logger.error(f"ERROR: Could not write state file {state_file}: {e}")


def _get_state_file_path(raw_dir: Path, config: Optional[dict] = None) -> Path:
    """Get the path to the state file based on configuration.

    Args:
        raw_dir: Path to the raw data directory
        config: Configuration dictionary (optional)

    Returns:
        Path to the state file
    """
    # Check environment variable first
    env_state_file = os.getenv("MVA_STATE_FILE")
    if env_state_file:
        return Path(env_state_file)

    # Check config
    if config and "state_file" in config:
        state_file = config["state_file"]
        # If relative path, make it relative to raw_dir
        if not os.path.isabs(state_file):
            return raw_dir / state_file
        return Path(state_file)

    # Default: .mva_state.json in raw_dir
    return raw_dir / ".mva_state.json"


def get_state_store_type(config: Optional[dict] = None) -> str:
    """Get the configured state store type.

    Args:
        config: Configuration dictionary (optional)

    Returns:
        State store type: 'redis' or 'file'
    """
    # Check environment variable first
    env_state_store = os.getenv("MVA_STATE_STORE")
    if env_state_store:
        return env_state_store.lower()

    # Check config
    if config and "state_store" in config:
        return config["state_store"].lower()

    # Default to redis if available, otherwise file
    return "redis" if is_redis_enabled() else "file"


def _get_redis_key(raw_dir: Path) -> str:
    """Generate a unique Redis key for the given raw_dir.

    This supports multi-tenant scenarios where different projects
    or data directories need separate fingerprint tracking.

    Args:
        raw_dir: Path to the raw data directory

    Returns:
        Unique Redis key for this directory
    """
    import hashlib

    # Use absolute path to ensure uniqueness
    abs_path = str(raw_dir.absolute())

    # Create a short hash of the path for the key
    path_hash = hashlib.sha1(abs_path.encode("utf-8")).hexdigest()[:12]

    return f"mva_pipeline:fingerprint:{path_hash}"
