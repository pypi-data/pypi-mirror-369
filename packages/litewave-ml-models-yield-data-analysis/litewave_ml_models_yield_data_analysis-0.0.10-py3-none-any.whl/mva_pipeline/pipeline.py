"""Main MVA pipeline driver with intelligent caching.

This module provides the high-level run_pipeline() function that orchestrates
the entire analytics workflow with fingerprint-based caching to avoid
recomputing results when input data hasn't changed.
"""

import logging
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from .analysis import anomaly, pca_yield, root_cause
from .analysis.unified_importance import compute_unified_importance
from .builder import build_batch_matrix, robust_scale_jitter
from .cli import load_config
from .db.connector import get_engine
from .db.extractor import export_tables
from .redis_manager import get_redis_manager, is_redis_enabled
from .state import get_last_fingerprint, set_last_fingerprint
from .synth import augment
from .utils.fingerprint import parquet_fingerprint

# Package-level logger
logger = logging.getLogger(__name__)


def run_pipeline(
    raw_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    config_path: Optional[Path] = None,
    force_rebuild: bool = False,
    skip_extraction: bool = False,
    redis_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the complete MVA analytics pipeline with intelligent caching.

    This function orchestrates the entire workflow:
    1. Compute fingerprint of current Parquet data
    2. Compare with last known fingerprint
    3. If unchanged and artifacts exist → fast exit (cache hit)
    4. If changed → run full analytics pipeline and cache results

    Args:
        raw_dir: Directory containing raw Parquet files (if None, uses config)
        config_path: Path to configuration file (if None, uses default)
        force_rebuild: If True, skip cache check and force full rebuild
        skip_extraction: If True, skip database extraction step

    Returns:
        Dictionary with pipeline results:
        {
            "updated": bool,  # True if analytics were re-run
            "cache_hit": bool,  # True if cache was used
            "fingerprint": str,  # Current data fingerprint
            "runtime_seconds": float,  # Total runtime
            "artifacts": {
                "batch_matrix": str,  # Path to batch matrix
                "anomaly_results": str,  # Path to anomaly results
                "pca_results": str,  # Path to PCA results
                "rca_results": str,  # Path to RCA results
                "unified_importance": str  # Path to unified importance
            }
        }
    """
    start_time = time.time()

    # Load configuration
    config = load_config(config_path)

    # Initialize Redis Manager with provided URL
    if redis_url:
        get_redis_manager(redis_url=redis_url)

    # Determine raw_dir and output_dir from config if not provided
    if output_dir is None:
        output_dir = Path(config.get("output_dir", "outputs"))

    if raw_dir is None:
        raw_dir = output_dir / "data_raw"

    raw_dir = Path(raw_dir)
    output_dir = Path(output_dir)

    logger.info(
        f"PIPELINE: Starting MVA pipeline (raw_dir: {raw_dir}, output_dir: {output_dir})"
    )

    # Step 1: Extract data if requested and raw_dir doesn't exist or is empty
    if not skip_extraction and (
        not raw_dir.exists() or not list(raw_dir.glob("*.parquet"))
    ):
        logger.info("EXTRACTION: Running data extraction...")
        _run_extraction(config, raw_dir)

    # Step 2: Compute current fingerprint
    try:
        fp_new = parquet_fingerprint(raw_dir)
        logger.info(f"FINGERPRINT: Current data fingerprint: {fp_new[:16]}...")
    except FileNotFoundError as e:
        logger.error(f"FINGERPRINT: {e}")
        logger.error(f"FINGERPRINT TRACEBACK: {traceback.format_exc()}")
        return {
            "updated": False,
            "cache_hit": False,
            "error": str(e),
            "runtime_seconds": time.time() - start_time,
        }

    # Step 3: Check cache if not forcing rebuild
    cache_hit = False
    if not force_rebuild:
        fp_old = get_last_fingerprint(raw_dir, config, redis_url=redis_url)
        if fp_old == fp_new:
            logger.info("CACHE HIT – analytics skipped")
            cache_hit = True

            # Check if artifacts exist
            artifacts = _check_existing_artifacts(output_dir)
            if artifacts["all_exist"]:
                return {
                    "updated": False,
                    "cache_hit": True,
                    "fingerprint": fp_new,
                    "runtime_seconds": time.time() - start_time,
                    "artifacts": artifacts["paths"],
                }
            else:
                logger.warning(
                    "CACHE: Fingerprint match but artifacts missing, rebuilding..."
                )
                cache_hit = False

    # Step 4: Run full analytics pipeline
    logger.info("ANALYTICS: Running full pipeline...")

    try:
        # Create output directories
        _create_output_directories(output_dir)

        # Build batch matrix
        batch_matrix = _build_batch_matrix(raw_dir, config)

        # Save batch matrix
        batch_matrix_path = output_dir / "batch_matrix.parquet"
        batch_matrix.to_parquet(batch_matrix_path, index=False)
        logger.info(
            f"BATCH: Saved batch matrix ({batch_matrix.shape}) to {batch_matrix_path}"
        )

        # Create scaled version
        batch_scaled = robust_scale_jitter(batch_matrix)
        batch_scaled_path = output_dir / "batch_matrix_scaled.parquet"
        batch_scaled.to_parquet(batch_scaled_path, index=False)

        # Store in Redis if enabled
        if is_redis_enabled():
            try:
                redis_manager = get_redis_manager(redis_url=redis_url)
                redis_manager.store_dataframe("batch_matrix", batch_matrix)
                logger.info("REDIS: Stored batch matrix in Redis")
            except Exception as e:
                logger.warning(f"REDIS: Failed to store batch matrix: {e}")

        # Run analytics
        analytics_results = _run_analytics(batch_matrix, config, redis_url=redis_url)

        # Step 5: Update fingerprint
        set_last_fingerprint(fp_new, raw_dir, config, redis_url=redis_url)

        # Prepare artifacts paths
        artifacts = _get_artifact_paths(output_dir)

        runtime = time.time() - start_time
        logger.info(f"PIPELINE: Complete in {runtime:.1f}s (updated: True)")

        return {
            "updated": True,
            "cache_hit": cache_hit,
            "fingerprint": fp_new,
            "runtime_seconds": runtime,
            "artifacts": artifacts,
            "analytics_summary": analytics_results,
        }

    except Exception as e:
        logger.error(f"PIPELINE: Failed to run analytics: {e}")
        logger.error(f"PIPELINE TRACEBACK: {traceback.format_exc()}")
        return {
            "updated": False,
            "cache_hit": False,
            "error": str(e),
            "runtime_seconds": time.time() - start_time,
        }


def _run_extraction(config: dict, raw_dir: Path) -> None:
    """Run the data extraction step."""
    engine = get_engine(config["db_url"])
    raw_dir.mkdir(parents=True, exist_ok=True)

    files = export_tables(
        engine,
        config.get("link_keys", ["doc_id"]),
        output_dir=str(raw_dir),
    )
    logger.info(f"EXTRACTION: Extracted {len(files)} tables to {raw_dir}")


def _build_batch_matrix(raw_dir: Path, config: dict):
    """Build the batch matrix from raw data."""
    link_key = config.get("link_keys", ["doc_id"])[0]

    batch_matrix = build_batch_matrix(
        raw_dir,
        link_key=link_key,
        use_llm_filter=config.get("use_llm_filter", True),
        config_path=None,  # Config already loaded
    )

    logger.info(f"BATCH: Built batch matrix: {batch_matrix.shape}")
    return batch_matrix


def _run_analytics(batch_matrix, config: dict, redis_url: Optional[str] = None) -> dict:
    """Run the complete analytics suite."""
    # Make a copy to prevent caller side-effects
    df_aug = batch_matrix.copy()
    results = {}

    # Find yield column
    yield_col = "yield"
    all_yield_cols = [col for col in df_aug.columns if "yield" in col.lower()]

    if all_yield_cols:
        potential_yield_cols = [
            col for col in all_yield_cols if "actual_yield" in col.lower()
        ]
        if not potential_yield_cols:
            potential_yield_cols = all_yield_cols

        # Create unified yield column
        df_aug[yield_col] = None
        for col in potential_yield_cols:
            df_aug[yield_col] = df_aug[yield_col].fillna(df_aug[col])

        # Remove original yield columns to prevent data leakage
        yield_cols_to_remove = [
            col for col in df_aug.columns if "yield" in col.lower() and col != yield_col
        ]
        df_aug = df_aug.drop(columns=yield_cols_to_remove)

        logger.info(
            f"YIELD: Using yield column with {df_aug[yield_col].notna().sum()}/{len(df_aug)} valid values"
        )

    # Synthetic augmentation
    n_need = max(0, 500 - len(df_aug))
    df_aug = augment(df_aug, n=n_need, sigma=5, anomaly_frac=0.02)

    # Anomaly detection
    logger.info("ANALYTICS: Running anomaly detection...")
    anomaly_result = anomaly.detect(df_aug)
    results["anomaly"] = {
        "n_anomalies": int(anomaly_result["anomaly"].sum())
        if "anomaly" in anomaly_result
        else 0
    }

    # Store in Redis
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager(redis_url=redis_url)
            redis_manager.store_dataframe("anomaly_results", anomaly_result)
        except Exception as e:
            logger.warning(f"REDIS: Failed to store anomaly results: {e}")

    # PCA analysis (if yield column exists)
    if yield_col in df_aug.columns and df_aug[yield_col].notna().sum() > 10:
        logger.info("ANALYTICS: Running supervised PCA...")
        pca_result = pca_yield.supervised_pca(df_aug, target_col=yield_col)
        results["pca"] = {
            "n_components": pca_result.get("n_components", 0),
            "variance_explained": pca_result.get("variance_explained", 0),
        }

        # Store PCA results in Redis
        if is_redis_enabled():
            try:
                redis_manager = get_redis_manager(redis_url=redis_url)
                if "loadings" in pca_result:
                    redis_manager.store_dataframe(
                        "pca_loadings", pca_result["loadings"]
                    )
                if "scores" in pca_result:
                    redis_manager.store_dataframe("pca_scores", pca_result["scores"])
            except Exception as e:
                logger.warning(f"REDIS: Failed to store PCA results: {e}")

        # Root cause analysis
        logger.info("ANALYTICS: Running root cause analysis...")
        rca_result = root_cause.run(df_aug, target_col=yield_col, k_features=20)
        results["rca"] = {"n_features": len(rca_result.get("feature_importance", []))}

        # Store RCA results in Redis
        if is_redis_enabled():
            try:
                redis_manager = get_redis_manager(redis_url=redis_url)
                if "feature_importance" in rca_result:
                    importance_df = rca_result["feature_importance"].reset_index()
                    importance_df.columns = ["feature", "importance"]
                    redis_manager.store_dataframe("rca_importance", importance_df)
            except Exception as e:
                logger.warning(f"REDIS: Failed to store RCA results: {e}")

        # Unified importance
        logger.info("ANALYTICS: Computing unified importance...")
        unified_result = compute_unified_importance(pca_result, rca_result, top_k=15)
        results["unified"] = {"n_features": len(unified_result)}

        # Store unified results in Redis
        if is_redis_enabled():
            try:
                redis_manager = get_redis_manager(redis_url=redis_url)
                redis_manager.store_dataframe("unified_importance", unified_result)
            except Exception as e:
                logger.warning(f"REDIS: Failed to store unified importance: {e}")
    else:
        logger.warning(
            "ANALYTICS: Skipping yield-based analysis due to insufficient yield data"
        )

    return results


def _create_output_directories(output_dir: Path) -> None:
    """Create all necessary output directories."""
    directories = [
        output_dir,
        output_dir / "anomaly",
        output_dir / "pca",
        output_dir / "rca",
        output_dir / "unified",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def _check_existing_artifacts(output_dir: Path) -> dict:
    """Check if all expected artifacts exist."""
    # Use actual file names that are generated by the analysis modules
    expected_files = [
        "batch_matrix.parquet",
        "batch_matrix_scaled.parquet",
        "anomaly/anomaly_results.csv",
        "pca/pca_loadings.csv",
        "rca/feature_importance.csv",
        "unified/unified_feature_importance.csv",
    ]

    paths = {}
    all_exist = True

    for file_path in expected_files:
        full_path = output_dir / file_path
        paths[file_path] = str(full_path)
        if not full_path.exists():
            all_exist = False

    return {"all_exist": all_exist, "paths": paths}


def _get_artifact_paths(output_dir: Path) -> dict:
    """Get paths to all generated artifacts."""
    return {
        "batch_matrix": str(output_dir / "batch_matrix.parquet"),
        "batch_matrix_scaled": str(output_dir / "batch_matrix_scaled.parquet"),
        "anomaly_results": str(output_dir / "anomaly"),
        "pca_results": str(output_dir / "pca"),
        "rca_results": str(output_dir / "rca"),
        "unified_importance": str(output_dir / "unified"),
    }
