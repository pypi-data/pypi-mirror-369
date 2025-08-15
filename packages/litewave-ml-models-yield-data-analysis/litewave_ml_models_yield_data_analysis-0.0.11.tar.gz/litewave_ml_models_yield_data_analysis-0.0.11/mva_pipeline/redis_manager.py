"""Redis data manager for MVA pipeline results.

This module handles storing and retrieving analysis results to/from Redis
for consumption by external agents.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import pandas as pd
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# Definitive list of dataframes that contain doc_id and are managed in Redis
MVA_DATAFRAMES_WITH_DOC_ID = [
    "anomaly_results",
    "pca_components",
    "shap_values",
    "batch_matrix",
]


class MVARedisManager:
    """Manages storing and retrieving MVA analysis results in Redis."""

    def __init__(self, redis_url: Optional[str] = None):
        """Initialize Redis connection.

        Args:
            redis_url: Redis connection URL. If None, uses REDIS_URL env var or default.
        """
        if redis_url is None:
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        else:
            self.redis_url = redis_url

        self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        self.key_prefix = "mva_analysis"

        # Test connection
        try:
            self.redis_client.ping()
            logger.info(f"SUCCESS: Connected to Redis at {self.redis_url}")
        except redis.ConnectionError as e:
            logger.error(f"ERROR: Failed to connect to Redis: {e}")
            raise

    def _make_key(self, data_type: str) -> str:
        """Create Redis key for data type."""
        return f"{self.key_prefix}:{data_type}"

    def store_dataframe(self, data_type: str, df: pd.DataFrame) -> None:
        """Store a DataFrame as JSON in Redis.

        Args:
            data_type: Type of data (e.g., 'anomaly_results', 'unified_importance')
            df: DataFrame to store
        """
        try:
            # Convert DataFrame to JSON
            json_data = df.to_json(orient="records", date_format="iso")

            # Store in Redis with metadata
            key = self._make_key(data_type)
            metadata = {
                "shape": df.shape,
                "columns": list(df.columns),
                "timestamp": pd.Timestamp.now().isoformat(),
            }

            # Use a hash to store both data and metadata
            self.redis_client.hset(
                key, mapping={"data": json_data, "metadata": json.dumps(metadata)}
            )

            logger.info(
                f"SUCCESS: Stored {data_type} in Redis: {df.shape[0]} rows, {df.shape[1]} columns"
            )

        except Exception as e:
            logger.error(f"ERROR: Failed to store {data_type} in Redis: {e}")
            raise

    def get_dataframe(self, data_type: str) -> pd.DataFrame:
        """Retrieve a DataFrame from Redis.

        Args:
            data_type: Type of data to retrieve

        Returns:
            DataFrame from Redis

        Raises:
            FileNotFoundError: If data not found in Redis
        """
        try:
            key = self._make_key(data_type)

            # Check if key exists
            if not self.redis_client.hexists(key, "data"):
                raise FileNotFoundError(
                    f"{data_type} not found in Redis. Run the analysis pipeline first."
                )

            # Get data from Redis
            json_data = self.redis_client.hget(key, "data")
            metadata_str = self.redis_client.hget(key, "metadata")

            if json_data is None:
                raise FileNotFoundError(f"{data_type} data is empty in Redis.")

            # Convert back to DataFrame
            from io import StringIO

            df = pd.read_json(StringIO(json_data), orient="records")

            # Log metadata if available
            if metadata_str:
                metadata = json.loads(metadata_str)
                logger.info(
                    f"DATA: Retrieved {data_type} from Redis: {metadata['shape'][0]} rows, {metadata['shape'][1]} columns"
                )

            return df

        except redis.ConnectionError as e:
            raise ConnectionError(f"Redis connection failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for {data_type}: {e}")
        except Exception as e:
            if "not found in Redis" in str(e):
                raise
            raise RuntimeError(f"Failed to retrieve {data_type} from Redis: {e}")

    def store_dict(self, data_type: str, data: Dict[str, Any]) -> None:
        """Store a dictionary as JSON in Redis.

        Args:
            data_type: Type of data
            data: Dictionary to store
        """
        try:
            key = self._make_key(data_type)
            json_data = json.dumps(
                data, default=str
            )  # default=str handles non-serializable objects

            metadata = {
                "timestamp": pd.Timestamp.now().isoformat(),
                "keys": list(data.keys()) if isinstance(data, dict) else [],
            }

            self.redis_client.hset(
                key, mapping={"data": json_data, "metadata": json.dumps(metadata)}
            )

            logger.info(f"SUCCESS: Stored {data_type} dict in Redis")

        except Exception as e:
            logger.error(f"ERROR: Failed to store {data_type} dict in Redis: {e}")
            raise

    def get_dict(self, data_type: str) -> Dict[str, Any]:
        """Retrieve a dictionary from Redis.

        Args:
            data_type: Type of data to retrieve

        Returns:
            Dictionary from Redis
        """
        try:
            key = self._make_key(data_type)

            if not self.redis_client.hexists(key, "data"):
                raise FileNotFoundError(f"{data_type} not found in Redis.")

            json_data = self.redis_client.hget(key, "data")
            if json_data is None:
                raise FileNotFoundError(f"{data_type} data is empty in Redis.")

            return json.loads(json_data)

        except redis.ConnectionError as e:
            raise ConnectionError(f"Redis connection failed: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data for {data_type}: {e}")
        except Exception as e:
            if "not found in Redis" in str(e):
                raise
            raise RuntimeError(f"Failed to retrieve {data_type} from Redis: {e}")

    def check_data_availability(self) -> Dict[str, bool]:
        """Check which analysis results are available in Redis.

        Returns:
            Dictionary mapping data types to availability status
        """
        data_types = [
            "anomaly_results",
            "unified_importance",
            "rca_feature_importance",
            "pca_loadings",
            "pca_components",
            "shap_values",
            "batch_matrix",
        ]

        availability = {}
        for data_type in data_types:
            try:
                key = self._make_key(data_type)
                availability[data_type] = self.redis_client.hexists(key, "data")
            except Exception:
                availability[data_type] = False

        return availability

    def clear_all_data(self) -> None:
        """Clear all MVA analysis data from Redis."""
        try:
            pattern = f"{self.key_prefix}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(
                    f"SUCCESS: Cleared {len(keys)} MVA analysis keys from Redis"
                )
            else:
                logger.info("INFO: No MVA analysis data found in Redis to clear")
        except Exception as e:
            logger.error(f"ERROR: Failed to clear Redis data: {e}")
            raise


# Global instance for easy access
_redis_manager = None


def get_redis_manager(redis_url: Optional[str] = None) -> "MVARedisManager":
    """Get or create the global Redis manager instance.
    If redis_url is provided, it will re-initialize the manager.
    """
    global _redis_manager
    if _redis_manager is None or (
        _redis_manager is not None
        and redis_url is not None
        and redis_url != _redis_manager.redis_url
    ):
        _redis_manager = MVARedisManager(redis_url)
    return _redis_manager


def is_redis_enabled() -> bool:
    """Check if Redis storage is enabled via environment variable."""
    return os.getenv("ENABLE_REDIS_STORAGE", "true").lower() in ("true", "1", "yes")
