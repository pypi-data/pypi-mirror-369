from __future__ import annotations

"""mva_pipeline.tools
=====================

A lightweight, import-only API that exposes the most useful analytics
artifacts (already computed by the pipeline and stored in the ``outputs``
folder) as easily callable *tools*.

The goal is to let external LLM agents (or any other Python process)
fetch key insights without needing to re-run heavy computations or load
large models.  Every public function below:

1. Has a short, clear docstring - suitable for use as the *description*
   field when registering a tool for OpenAI function-calling or
   LangChain ``Tool`` wrappers.
2. Accepts only JSON-serialisable arguments and returns data that is
   immediately JSON-serialisable (lists / dicts / primitives).
3. Loads the required CSV once and caches it with ``functools.lru_cache``
   so calls are fast and stateless.

Example
-------
>>> from mva_pipeline.tools import get_top_anomalies
>>> get_top_anomalies(n=5)
[{"doc_id": 470, "score_if": 6.79, "top_dev_feat": "weighing details …"}, ...]
"""

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from .redis_manager import get_redis_manager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration and Cache Management ----------------------------------------
# ---------------------------------------------------------------------------


def set_redis_url(redis_url: str) -> None:
    """Configure the Redis connection URL for all tools and clear caches.

    This must be called by the agent before executing any tools to ensure
    they connect to the correct Redis instance.
    """
    logger.info(f"Setting MVA tools Redis URL to: {redis_url}")
    get_redis_manager(redis_url=redis_url)  # Re-initializes the global manager
    clear_caches()  # Clear LRU caches to force reload from new source


def clear_caches() -> None:
    """Clear all LRU caches for data-loading functions."""
    logger.info("Clearing all MVA tool data loader caches...")
    _load_anomaly.cache_clear()
    _load_unified.cache_clear()
    _load_rca.cache_clear()
    _load_pca_loadings.cache_clear()
    _load_pca_components.cache_clear()
    _load_shap_values.cache_clear()
    _load_batch_matrix.cache_clear()
    logger.info("MVA tool caches cleared.")


# ---------------------------------------------------------------------------
# Redis-based loaders (cached) ----------------------------------------------
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _load_anomaly() -> pd.DataFrame:
    """Load anomaly results from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        return redis_manager.get_dataframe("anomaly_results")
    except Exception as e:
        raise FileNotFoundError(
            f"Anomaly results not found in Redis: {e}. Run the analysis pipeline first: `python -m mva_pipeline.cli analyze`."
        )


@lru_cache(maxsize=1)
def _load_unified() -> pd.DataFrame:
    """Load unified feature importance table from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        return redis_manager.get_dataframe("unified_importance")
    except Exception as e:
        raise FileNotFoundError(
            f"Unified feature-importance not found in Redis: {e}. Make sure the analysis step completed successfully."
        )


@lru_cache(maxsize=1)
def _load_rca() -> pd.DataFrame:
    """Load SHAP / RCA feature importance table from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        return redis_manager.get_dataframe("rca_feature_importance")
    except Exception as e:
        raise FileNotFoundError(
            f"RCA feature-importance not found in Redis: {e}. Make sure the analysis step completed successfully."
        )


@lru_cache(maxsize=1)
def _load_pca_loadings() -> pd.DataFrame:
    """Load PCA loadings table from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        df = redis_manager.get_dataframe("pca_loadings")
        # Set the first column (feature names) as index if it exists
        if len(df.columns) > 1 and "index" in df.columns:
            df = df.set_index("index")
        return df
    except Exception as e:
        raise FileNotFoundError(
            f"PCA loadings not found in Redis: {e}. Make sure the analysis step completed successfully."
        )


@lru_cache(maxsize=1)
def _load_pca_components() -> pd.DataFrame:
    """Load PCA components table from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        return redis_manager.get_dataframe("pca_components")
    except Exception as e:
        raise FileNotFoundError(
            f"PCA components not found in Redis: {e}. Make sure the analysis step completed successfully."
        )


@lru_cache(maxsize=1)
def _load_shap_values() -> pd.DataFrame:
    """Load SHAP values table from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        return redis_manager.get_dataframe("shap_values")
    except Exception as e:
        raise FileNotFoundError(
            f"SHAP values not found in Redis: {e}. Make sure the analysis step completed successfully."
        )


@lru_cache(maxsize=1)
def _load_batch_matrix() -> pd.DataFrame:
    """Load the batch matrix from Redis (cached)."""
    try:
        redis_manager = get_redis_manager()
        return redis_manager.get_dataframe("batch_matrix")
    except Exception as e:
        raise FileNotFoundError(
            f"Batch matrix not found in Redis: {e}. Run the build step first: `python -m mva_pipeline.cli build`."
        )


# ---------------------------------------------------------------------------
# Public API - Anomaly Detection Tools --------------------------------------
# ---------------------------------------------------------------------------


def get_top_anomalies(n: int = 10) -> List[Dict[str, Any]]:
    """Return *n* batches with the highest Isolation-Forest anomaly score.

    Parameters
    ----------
    n : int, optional
        Number of top-scoring batches to return (default 10).

    Returns
    -------
    list of dict
        Each dict contains ``doc_id``, the Isolation-Forest score
        (``score_if``), and the user-friendly explanation of what
        process parameters are problematic.
    """
    df = _load_anomaly()

    # Ensure we have the necessary columns
    required_cols = ["doc_id", "score_if"]
    if not set(required_cols).issubset(df.columns):
        raise ValueError(
            "Expected columns missing in anomaly_results.csv. Consider rerunning the pipeline."
        )

    # Get the top n anomalies by Isolation Forest score
    top_anomalies = df.sort_values("score_if", ascending=False).head(n)

    results = []
    for _, row in top_anomalies.iterrows():
        result = {
            "doc_id": int(row["doc_id"]),
            "anomaly_score": float(row["score_if"]),
            # "is_anomaly": bool(row.get("anomaly", False)),
        }

        # Add user-friendly explanation
        if "top_dev_feat" in row and pd.notna(row["top_dev_feat"]):
            result["issues_detected"] = str(row["top_dev_feat"])

        # Add sample type if available
        # if "sample_type" in row:
        #     result["batch_type"] = str(row["sample_type"])

        results.append(result)

    return results


def explain_batch(doc_id: int) -> Dict[str, Any]:
    """Return the anomaly profile & yield for a single batch.

    The response contains the raw anomaly scores (*Isolation Forest*,
    *Local Outlier Factor*, *Elliptic Envelope*, and *Mahalanobis*) along
    with boolean *is_anomaly_*** flags and the user-friendly explanation
    of what process parameters are problematic.
    """
    df = _load_anomaly()
    if doc_id not in df["doc_id"].values:
        raise ValueError(f"doc_id {doc_id} not found in anomaly results.")

    row = df[df["doc_id"] == doc_id].iloc[0]

    # Basic anomaly information
    result = {
        "doc_id": int(row["doc_id"]),
        "is_anomaly": bool(row.get("anomaly", False)),
        "anomaly_scores": {
            "isolation_forest": float(row.get("score_if", 0)),
            "local_outlier_factor": float(row.get("score_lof", 0)),
            "elliptic_envelope": float(row.get("score_ee", 0)),
            "mahalanobis_distance": float(row.get("dist_maha", 0)),
        },
        "detection_methods": {
            "isolation_forest": bool(row.get("is_anomaly_if", False)),
            "local_outlier_factor": bool(row.get("is_anomaly_lof", False)),
            "elliptic_envelope": bool(row.get("is_anomaly_ee", False)),
            "mahalanobis_distance": bool(row.get("is_anomaly_maha", False)),
        },
        "yield": float(row.get("yield", 0)),
    }

    # Add user-friendly explanation
    if "top_dev_feat" in row and pd.notna(row["top_dev_feat"]):
        result["issues_detected"] = str(row["top_dev_feat"])

    # Add detailed feature analysis if available
    if "top_dev_feat_details" in row and pd.notna(row["top_dev_feat_details"]):
        try:
            import json

            detailed_features = json.loads(row["top_dev_feat_details"])
            result["detailed_feature_analysis"] = detailed_features
        except (json.JSONDecodeError, ValueError):
            # Fallback if JSON parsing fails
            pass

    return result


def filter_anomalies_by_doc_ids(doc_ids: List[int]) -> List[Dict[str, Any]]:
    """Return anomaly information *only* for the specified ``doc_ids``.

    Parameters
    ----------
    doc_ids : list[int]
        Batch identifiers to retrieve. IDs not present in the results are
        silently ignored (they may correspond to filtered-out or
        non-existent batches).

    Returns
    -------
    list of dict
        Same schema as ``explain_batch`` but one entry per *existing*
        ``doc_id`` in the provided list (order preserved).
    """

    if not doc_ids:
        return []

    df = _load_anomaly()
    subset = df[df["doc_id"].isin(doc_ids)]

    if subset.empty:
        return []

    # Preserve the order of the input doc_ids
    subset["_order"] = pd.Categorical(
        subset["doc_id"], categories=doc_ids, ordered=True
    )
    subset_sorted = subset.sort_values("_order").drop(columns="_order")  # type: ignore[call-overload]

    results = []
    for _, row in subset_sorted.iterrows():
        result = {
            "doc_id": int(row["doc_id"]),
            "is_anomaly": bool(row.get("anomaly", False)),
            "anomaly_scores": {
                "isolation_forest": float(row.get("score_if", 0)),
                "local_outlier_factor": float(row.get("score_lof", 0)),
                "elliptic_envelope": float(row.get("score_ee", 0)),
                "mahalanobis_distance": float(row.get("dist_maha", 0)),
            },
            "detection_methods": {
                "isolation_forest": bool(row.get("is_anomaly_if", False)),
                "local_outlier_factor": bool(row.get("is_anomaly_lof", False)),
                "elliptic_envelope": bool(row.get("is_anomaly_ee", False)),
                "mahalanobis_distance": bool(row.get("is_anomaly_maha", False)),
            },
            "yield": float(row.get("yield", 0)),
        }

        # Add user-friendly explanation
        if "top_dev_feat" in row and pd.notna(row["top_dev_feat"]):
            result["issues_detected"] = str(row["top_dev_feat"])

        # Add detailed feature analysis if available
        if "top_dev_feat_details" in row and pd.notna(row["top_dev_feat_details"]):
            try:
                import json

                detailed_features = json.loads(row["top_dev_feat_details"])
                result["detailed_feature_analysis"] = detailed_features
            except (json.JSONDecodeError, ValueError):
                # Fallback if JSON parsing fails
                pass

        # Add sample type if available
        if "sample_type" in row:
            result["batch_type"] = str(row["sample_type"])

        results.append(result)

    return results


def get_anomaly_statistics() -> Dict[str, Any]:
    """Get overall anomaly detection statistics and model performance summary.

    Returns summary statistics about anomaly detection results including
    total batches analyzed, number flagged as anomalous, and breakdown by
    detection method.
    """
    df = _load_anomaly()

    total_batches = len(df)
    anomalous_batches = df["anomaly"].sum() if "anomaly" in df.columns else 0

    # Count by detection method
    method_counts = {}
    for method in ["if", "lof", "ee", "maha"]:
        col = f"is_anomaly_{method}"
        if col in df.columns:
            method_counts[method.upper()] = int(df[col].sum())

    # Top problematic features from user-friendly descriptions
    problematic_features = []
    if "top_dev_feat" in df.columns:
        for feat_str in df["top_dev_feat"].dropna():
            if feat_str and isinstance(feat_str, str):
                # Split by " | " and extract the main feature names
                issues = feat_str.split(" | ")
                for issue in issues:
                    # Extract the feature name (everything before " is ")
                    if " is " in issue:
                        feature_part = issue.split(" is ")[0].strip()
                        problematic_features.append(feature_part)

        from collections import Counter

        top_features = Counter(problematic_features).most_common(10)
    else:
        top_features = []

    # Get batch type breakdown if available
    batch_type_counts = {}
    if "sample_type" in df.columns:
        anomalous_subset = df[df["anomaly"] == True] if "anomaly" in df.columns else df
        batch_type_counts = anomalous_subset["sample_type"].value_counts().to_dict()

    return {
        "total_batches": int(total_batches),
        "anomalous_batches": int(anomalous_batches),
        "anomaly_rate": (
            float(anomalous_batches / total_batches) if total_batches > 0 else 0.0
        ),
        "detection_method_counts": method_counts,
        "most_problematic_parameters": [
            {"parameter": f, "frequency": c} for f, c in top_features
        ],
        "anomaly_breakdown_by_batch_type": batch_type_counts,
    }


# ---------------------------------------------------------------------------
# Public API - Yield Driver Analysis ----------------------------------------
# ---------------------------------------------------------------------------


def get_top_yield_drivers(n: int = 15) -> List[Dict[str, Any]]:
    """Return the *n* most critical process parameters driving yield.

    Rankings are based on the *unified_score* which blends supervised PCA
    loadings and SHAP feature importances, giving a holistic picture of
    both variance explanation and predictive power.
    """
    df = _load_unified()
    cols = ["business_concept", "unified_score"]
    out = (
        df.sort_values("unified_score", ascending=False)
        .head(n)
        .loc[:, cols]
        .to_dict(orient="records")
    )
    return out


def get_feature_scores(feature: str) -> Dict[str, Any]:
    """Return PCA-loading, SHAP score, and unified score for *feature*.

    If the feature is not present in the unified table we fall back to
    the RCA SHAP table.
    """
    uni = _load_unified().set_index("feature")
    if feature in uni.index:
        row = uni.loc[feature]
        return {
            "feature": feature,
            "unified_score": float(row["unified_score"]),
            "pca_score": float(row["pca_score"]),
            "shap_score": float(row["shap_score"]),
        }

    # fallback to RCA only
    rca = _load_rca().set_index("feature")
    if feature in rca.index:
        shap_score = float(rca.loc[feature].iloc[0])
        return {
            "feature": feature,
            "unified_score": None,
            "pca_score": None,
            "shap_score": shap_score,
        }

    raise ValueError(f"Feature '{feature}' not found in importance tables.")


def compare_feature_importance_methods() -> Dict[str, Any]:
    """Compare feature rankings across PCA, SHAP, and unified methods.

    Returns analysis of how different importance methods rank the same features,
    helping understand which features are consistently important vs method-specific.
    """
    df = _load_unified()

    # Get top 20 from each method
    top_pca = df.nlargest(20, "pca_score")["feature"].tolist()
    top_shap = df.nlargest(20, "shap_score")["feature"].tolist()
    top_unified = df.nlargest(20, "unified_score")["feature"].tolist()

    # Find overlaps
    pca_shap_overlap = set(top_pca) & set(top_shap)
    all_methods_overlap = set(top_pca) & set(top_shap) & set(top_unified)

    # Method-specific features
    pca_only = set(top_pca) - set(top_shap) - set(top_unified)
    shap_only = set(top_shap) - set(top_pca) - set(top_unified)

    return {
        "top_features_by_method": {
            "pca": top_pca[:10],
            "shap": top_shap[:10],
            "unified": top_unified[:10],
        },
        "consensus_features": list(all_methods_overlap),
        "method_specific": {"pca_only": list(pca_only), "shap_only": list(shap_only)},
        "overlap_stats": {
            "pca_shap_overlap_count": len(pca_shap_overlap),
            "all_methods_overlap_count": len(all_methods_overlap),
        },
    }


# ---------------------------------------------------------------------------
# Public API - PCA Analysis Tools -------------------------------------------
# ---------------------------------------------------------------------------


def get_pca_summary() -> Dict[str, Any]:
    """Get PCA analysis summary including explained variance and key loadings.

    Returns overview of PCA results including variance explained by each
    component and top features loading on the first few components.
    """
    try:
        loadings = _load_pca_loadings()
        components = _load_pca_components()

        # Calculate explained variance ratios from components if available
        variance_explained = []
        component_cols = [col for col in components.columns if col.startswith("PC")]

        for col in component_cols[:5]:  # First 5 components
            if col in components.columns:
                variance = components[col].var()
                variance_explained.append(float(variance))

        # Normalize to ratios
        total_var = sum(variance_explained)
        if total_var > 0:
            variance_ratios = [v / total_var for v in variance_explained]
        else:
            variance_ratios = variance_explained

        # Top loadings for first 2 components
        top_loadings = {}
        for i, pc in enumerate(["PC1", "PC2"]):
            if pc in loadings.columns:
                pc_loadings = loadings[pc].abs().nlargest(10)
                top_loadings[pc] = [
                    {"feature": idx, "loading": float(val)}
                    for idx, val in pc_loadings.items()
                ]

        return {
            "n_components": len(component_cols),
            "variance_explained_ratios": variance_ratios,
            "cumulative_variance": [
                sum(variance_ratios[: i + 1]) for i in range(len(variance_ratios))
            ],
            "top_loadings_by_component": top_loadings,
            "total_features_analyzed": len(loadings),
        }

    except FileNotFoundError as e:
        return {"error": str(e)}


def get_batch_pca_scores(
    doc_ids: List[int] = None, n_components: int = 3
) -> List[Dict[str, Any]]:
    """Get PCA component scores for specific batches.

    Returns the transformed feature space coordinates for batches, useful for
    understanding where batches fall in the reduced dimensional space.
    """
    try:
        components = _load_pca_components()

        if doc_ids is not None:
            # Filter to specific doc_ids if available
            if "doc_id" in components.columns:
                components = components[components["doc_id"].isin(doc_ids)]
            else:
                # Assume row index corresponds to doc_id order from batch matrix
                batch_matrix = _load_batch_matrix()
                if "doc_id" in batch_matrix.columns:
                    doc_id_to_idx = {
                        doc_id: i for i, doc_id in enumerate(batch_matrix["doc_id"])
                    }
                    valid_indices = [
                        doc_id_to_idx[doc_id]
                        for doc_id in doc_ids
                        if doc_id in doc_id_to_idx
                    ]
                    components = components.iloc[valid_indices]

        # Get component columns
        component_cols = [col for col in components.columns if col.startswith("PC")][
            :n_components
        ]
        result_cols = ["yield"] + component_cols

        # Include doc_id if available
        if "doc_id" in components.columns:
            result_cols = ["doc_id"] + result_cols

        available_cols = [col for col in result_cols if col in components.columns]

        return components[available_cols].to_dict(orient="records")

    except FileNotFoundError as e:
        return [{"error": str(e)}]


# ---------------------------------------------------------------------------
# Public API - SHAP Analysis Tools ------------------------------------------
# ---------------------------------------------------------------------------


def get_batch_shap_explanation(doc_id: int, top_n: int = 10) -> Dict[str, Any]:
    """Get SHAP value explanation for a specific batch.

    Returns the SHAP values showing which features pushed the yield prediction
    up or down for this specific batch.
    """
    try:
        shap_df = _load_shap_values()

        # Find the batch row (assuming doc_id order matches batch matrix)
        batch_matrix = _load_batch_matrix()
        if "doc_id" in batch_matrix.columns:
            doc_id_to_idx = {
                doc_id: i for i, doc_id in enumerate(batch_matrix["doc_id"])
            }
            if doc_id not in doc_id_to_idx:
                return {"error": f"doc_id {doc_id} not found"}
            row_idx = doc_id_to_idx[doc_id]
        else:
            return {"error": "doc_id mapping not available"}

        if row_idx >= len(shap_df):
            return {"error": f"doc_id {doc_id} index out of range"}

        # Get SHAP values for this batch
        shap_row = shap_df.iloc[row_idx]

        # Get feature columns (exclude yield)
        feature_cols = [col for col in shap_df.columns if col != "yield"]

        # Get top positive and negative SHAP values
        feature_shaps = shap_row[feature_cols]

        # Sort by absolute value but keep sign
        top_positive = feature_shaps[feature_shaps > 0].nlargest(top_n // 2)
        top_negative = feature_shaps[feature_shaps < 0].nsmallest(top_n // 2)

        return {
            "doc_id": int(doc_id),
            "predicted_yield": float(shap_row.get("yield", 0)),
            "top_positive_contributors": [
                {"feature": feat, "shap_value": float(val)}
                for feat, val in top_positive.items()
            ],
            "top_negative_contributors": [
                {"feature": feat, "shap_value": float(val)}
                for feat, val in top_negative.items()
            ],
            "total_shap_impact": float(feature_shaps.sum()),
        }

    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Analysis failed: {str(e)}"}


def get_global_shap_patterns() -> Dict[str, Any]:
    """Analyze global SHAP patterns across all batches.

    Returns insights about which features consistently drive yield up/down
    and identifies features with high variance in their impact.
    """
    try:
        shap_df = _load_shap_values()
        rca_df = _load_rca()

        # Get feature columns (exclude yield)
        feature_cols = [col for col in shap_df.columns if col != "yield"]

        # Calculate statistics for each feature
        feature_stats = {}
        for feature in feature_cols:
            values = shap_df[feature]
            feature_stats[feature] = {
                "mean_impact": float(values.mean()),
                "std_impact": float(values.std()),
                "positive_rate": float((values > 0).mean()),
                "max_positive": float(values.max()),
                "max_negative": float(values.min()),
            }

        # Find consistently positive/negative features
        consistent_positive = [
            f
            for f, stats in feature_stats.items()
            if stats["positive_rate"] > 0.8 and stats["mean_impact"] > 0
        ]
        consistent_negative = [
            f
            for f, stats in feature_stats.items()
            if stats["positive_rate"] < 0.2 and stats["mean_impact"] < 0
        ]

        # High variance features (contextual - depend on other conditions)
        high_variance = sorted(
            feature_stats.items(), key=lambda x: x[1]["std_impact"], reverse=True
        )[:10]

        return {
            "consistent_yield_boosters": consistent_positive[:10],
            "consistent_yield_reducers": consistent_negative[:10],
            "most_contextual_features": [
                {"feature": f, "std_impact": stats["std_impact"]}
                for f, stats in high_variance
            ],
            "feature_statistics": {
                k: v
                for k, v in sorted(
                    feature_stats.items(),
                    key=lambda x: abs(x[1]["mean_impact"]),
                    reverse=True,
                )[:20]
            },
        }

    except FileNotFoundError as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Public API - Batch Comparison Tools ---------------------------------------
# ---------------------------------------------------------------------------


def compare_batches(
    doc_ids: List[int], focus_features: List[str] = None
) -> Dict[str, Any]:
    """Compare multiple batches across key process parameters and outcomes.

    Useful for understanding differences between good vs bad batches or
    comparing similar batches that had different outcomes.
    """
    try:
        batch_matrix = _load_batch_matrix()
        anomaly_df = _load_anomaly()

        if "doc_id" not in batch_matrix.columns:
            return {"error": "doc_id column not found in batch matrix"}

        # Filter to requested batches
        batch_subset = batch_matrix[batch_matrix["doc_id"].isin(doc_ids)]
        anomaly_subset = anomaly_df[anomaly_df["doc_id"].isin(doc_ids)]

        if len(batch_subset) == 0:
            return {"error": "No batches found for provided doc_ids"}

        # Get basic comparison data
        comparison_data = []
        for _, row in batch_subset.iterrows():
            doc_id = row["doc_id"]

            # Get anomaly info
            anomaly_info = anomaly_subset[anomaly_subset["doc_id"] == doc_id]
            anomaly_score = (
                float(anomaly_info["score_if"].iloc[0])
                if len(anomaly_info) > 0
                else 0.0
            )
            is_anomaly = (
                bool(anomaly_info["anomaly"].iloc[0])
                if len(anomaly_info) > 0
                else False
            )

            batch_data = {
                "doc_id": int(doc_id),
                "yield": float(row.get("yield", 0)),
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly,
            }

            # Add focus features if specified
            if focus_features:
                for feature in focus_features:
                    if feature in row:
                        batch_data[feature] = (
                            float(row[feature]) if pd.notna(row[feature]) else None
                        )

            comparison_data.append(batch_data)

        # Calculate summary statistics
        yields = [b["yield"] for b in comparison_data]
        anomaly_scores = [b["anomaly_score"] for b in comparison_data]

        summary = {
            "batch_count": len(comparison_data),
            "yield_range": {
                "min": min(yields),
                "max": max(yields),
                "mean": sum(yields) / len(yields),
            },
            "anomaly_score_range": {
                "min": min(anomaly_scores),
                "max": max(anomaly_scores),
            },
            "anomaly_count": sum(1 for b in comparison_data if b["is_anomaly"]),
        }

        return {"batch_comparison": comparison_data, "summary": summary}

    except Exception as e:
        return {"error": f"Comparison failed: {str(e)}"}


def find_similar_batches(
    doc_id: int, n_similar: int = 5, method: str = "yield"
) -> List[Dict[str, Any]]:
    """Find batches most similar to a reference batch.

    Can find similarity based on yield outcome, process conditions, or
    anomaly characteristics.
    """
    try:
        batch_matrix = _load_batch_matrix()
        anomaly_df = _load_anomaly()

        if "doc_id" not in batch_matrix.columns:
            return [{"error": "doc_id column not found in batch matrix"}]

        # Get reference batch
        ref_batch = batch_matrix[batch_matrix["doc_id"] == doc_id]
        if len(ref_batch) == 0:
            return [{"error": f"Reference batch {doc_id} not found"}]

        ref_batch = ref_batch.iloc[0]

        if method == "yield":
            # Find batches with similar yield
            ref_yield = ref_batch.get("yield", 0)
            batch_matrix["yield_diff"] = abs(batch_matrix.get("yield", 0) - ref_yield)
            similar = batch_matrix[batch_matrix["doc_id"] != doc_id].nsmallest(
                n_similar, "yield_diff"
            )

        elif method == "anomaly_score":
            # Find batches with similar anomaly characteristics
            ref_anomaly = anomaly_df[anomaly_df["doc_id"] == doc_id]
            if len(ref_anomaly) == 0:
                return [{"error": f"No anomaly data for batch {doc_id}"}]

            ref_score = ref_anomaly.iloc[0]["score_if"]
            anomaly_df["score_diff"] = abs(anomaly_df["score_if"] - ref_score)
            similar_anomaly = anomaly_df[anomaly_df["doc_id"] != doc_id].nsmallest(
                n_similar, "score_diff"
            )

            # Join back to batch matrix
            similar = batch_matrix[
                batch_matrix["doc_id"].isin(similar_anomaly["doc_id"])
            ]

        else:
            return [{"error": f"Unknown similarity method: {method}"}]

        # Format results
        results = []
        for _, row in similar.iterrows():
            batch_doc_id = int(row["doc_id"])

            # Get anomaly info
            anomaly_info = anomaly_df[anomaly_df["doc_id"] == batch_doc_id]

            results.append(
                {
                    "doc_id": batch_doc_id,
                    "yield": float(row.get("yield", 0)),
                    "anomaly_score": (
                        float(anomaly_info["score_if"].iloc[0])
                        if len(anomaly_info) > 0
                        else 0.0
                    ),
                    "similarity_metric": method,
                    "similarity_value": (
                        float(row.get("yield_diff", 0))
                        if method == "yield"
                        else (
                            float(anomaly_info["score_diff"].iloc[0])
                            if len(anomaly_info) > 0
                            else 0.0
                        )
                    ),
                }
            )

        return results

    except Exception as e:
        return [{"error": f"Similarity search failed: {str(e)}"}]


# ---------------------------------------------------------------------------
# Public API - Utility Functions --------------------------------------------
# ---------------------------------------------------------------------------


def list_available_features() -> List[str]:
    """Return a sorted list of features present in the unified importance table."""
    return sorted(_load_unified()["feature"].unique())


def get_pipeline_status() -> Dict[str, Any]:
    """Check which analysis outputs are available in Redis and provide pipeline status.

    Useful for understanding what analyses have been completed and what
    tools are available to use.
    """
    status = {
        "anomaly_detection": False,
        "pca_analysis": False,
        "rca_shap": False,
        "unified_importance": False,
        "batch_matrix": False,
    }

    details = {}

    # Check Redis availability first
    try:
        redis_manager = get_redis_manager()
        availability = redis_manager.check_data_availability()
    except Exception as e:
        return {
            "pipeline_status": status,
            "details": {"error": f"Redis connection failed: {e}"},
            "available_tools": 0,
        }

    # Check each output
    try:
        if availability.get("anomaly_results", False):
            status["anomaly_detection"] = True
            df = _load_anomaly()
            details["anomaly_detection"] = {
                "total_batches": len(df),
                "anomalous_batches": (
                    int(df["anomaly"].sum()) if "anomaly" in df.columns else 0
                ),
            }
        else:
            details["anomaly_detection"] = {"error": "Not available in Redis"}
    except Exception as e:
        details["anomaly_detection"] = {"error": f"Failed to load: {e}"}

    try:
        if availability.get("pca_loadings", False):
            status["pca_analysis"] = True
            loadings = _load_pca_loadings()
            details["pca_analysis"] = {
                "n_components": len(
                    [c for c in loadings.columns if c.startswith("PC")]
                ),
                "n_features": len(loadings),
            }
        else:
            details["pca_analysis"] = {"error": "Not available in Redis"}
    except Exception as e:
        details["pca_analysis"] = {"error": f"Failed to load: {e}"}

    try:
        if availability.get("rca_feature_importance", False):
            status["rca_shap"] = True
            rca = _load_rca()
            details["rca_shap"] = {"n_features": len(rca)}
        else:
            details["rca_shap"] = {"error": "Not available in Redis"}
    except Exception as e:
        details["rca_shap"] = {"error": f"Failed to load: {e}"}

    try:
        if availability.get("unified_importance", False):
            status["unified_importance"] = True
            unified = _load_unified()
            details["unified_importance"] = {"n_features": len(unified)}
        else:
            details["unified_importance"] = {"error": "Not available in Redis"}
    except Exception as e:
        details["unified_importance"] = {"error": f"Failed to load: {e}"}

    try:
        if availability.get("batch_matrix", False):
            status["batch_matrix"] = True
            batch = _load_batch_matrix()
            details["batch_matrix"] = {
                "n_batches": len(batch),
                "n_features": len(batch.columns),
            }
        else:
            details["batch_matrix"] = {"error": "Not available in Redis"}
    except Exception as e:
        details["batch_matrix"] = {"error": f"Failed to load: {e}"}

    return {
        "pipeline_status": status,
        "details": details,
        "available_tools": len([k for k, v in status.items() if v]),
        "redis_availability": availability,
    }


def get_tool_specs() -> List[Dict[str, Any]]:
    """Export tool specifications for external LLM agents.

    Returns a list of tool definitions that can be used by external agents
    for OpenAI function calling, LangChain tools, or other frameworks.

    Returns
    -------
    list of dict
        Each dict contains 'name', 'description', 'parameters' schema,
        and 'function' (the actual callable).
    """
    return [
        {
            "name": "get_top_anomalies",
            "description": "Get batches with highest anomaly scores from pharmaceutical manufacturing data. Returns batch IDs, scores, and user-friendly explanations of process issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of top anomalies to return",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 100,
                    }
                },
                "required": [],
            },
            "function": get_top_anomalies,
        },
        {
            "name": "explain_batch",
            "description": "Get detailed anomaly analysis for a specific manufacturing batch. Returns anomaly scores, detection methods, and user-friendly explanation of process issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "integer",
                        "description": "Batch identifier (doc_id) to analyze",
                    }
                },
                "required": ["doc_id"],
            },
            "function": explain_batch,
        },
        {
            "name": "filter_anomalies_by_doc_ids",
            "description": "Get anomaly information for multiple specific batch IDs. Returns detailed analysis with user-friendly explanations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of batch identifiers to retrieve anomaly data for",
                    }
                },
                "required": ["doc_ids"],
            },
            "function": filter_anomalies_by_doc_ids,
        },
        {
            "name": "get_anomaly_statistics",
            "description": "Get overall anomaly detection statistics including total batches, anomaly rates, breakdown by detection method, and most problematic process parameters.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": get_anomaly_statistics,
        },
        {
            "name": "get_top_yield_drivers",
            "description": "Get the most important process parameters that drive manufacturing yield. Based on combined PCA and SHAP analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Number of top yield drivers to return",
                        "default": 15,
                        "minimum": 1,
                        "maximum": 50,
                    }
                },
                "required": [],
            },
            "function": get_top_yield_drivers,
        },
        {
            "name": "get_feature_scores",
            "description": "Get importance scores (PCA, SHAP, unified) for a specific process parameter or feature.",
            "parameters": {
                "type": "object",
                "properties": {
                    "feature": {
                        "type": "string",
                        "description": "Feature name to get scores for (e.g., 'public.bprpoc_naocl_calc_weight__value_r0')",
                    }
                },
                "required": ["feature"],
            },
            "function": get_feature_scores,
        },
        {
            "name": "compare_feature_importance_methods",
            "description": "Compare how different importance methods (PCA, SHAP, unified) rank features. Shows consensus vs method-specific insights.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": compare_feature_importance_methods,
        },
        {
            "name": "get_pca_summary",
            "description": "Get PCA analysis summary including explained variance ratios and top feature loadings for the first components.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": get_pca_summary,
        },
        {
            "name": "get_batch_pca_scores",
            "description": "Get PCA component scores for specific batches to understand their position in reduced dimensional space.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of batch IDs to get PCA scores for. If not provided, returns all batches.",
                    },
                    "n_components": {
                        "type": "integer",
                        "description": "Number of PCA components to return",
                        "default": 3,
                        "minimum": 1,
                        "maximum": 10,
                    },
                },
                "required": [],
            },
            "function": get_batch_pca_scores,
        },
        {
            "name": "get_batch_shap_explanation",
            "description": "Get SHAP explanation for a specific batch showing which features drove the yield prediction up or down.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "integer",
                        "description": "Batch identifier to explain",
                    },
                    "top_n": {
                        "type": "integer",
                        "description": "Number of top contributing features to return",
                        "default": 10,
                        "minimum": 5,
                        "maximum": 20,
                    },
                },
                "required": ["doc_id"],
            },
            "function": get_batch_shap_explanation,
        },
        {
            "name": "get_global_shap_patterns",
            "description": "Analyze global SHAP patterns to identify features that consistently boost/reduce yield vs contextual features.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": get_global_shap_patterns,
        },
        {
            "name": "compare_batches",
            "description": "Compare multiple batches across key process parameters and outcomes. Useful for good vs bad batch analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of batch IDs to compare",
                    },
                    "focus_features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific features to focus the comparison on. If not provided, uses yield and anomaly data.",
                    },
                },
                "required": ["doc_ids"],
            },
            "function": compare_batches,
        },
        {
            "name": "find_similar_batches",
            "description": "Find batches most similar to a reference batch based on yield, process conditions, or anomaly characteristics.",
            "parameters": {
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "integer",
                        "description": "Reference batch ID to find similar batches for",
                    },
                    "n_similar": {
                        "type": "integer",
                        "description": "Number of similar batches to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20,
                    },
                    "method": {
                        "type": "string",
                        "enum": ["yield", "anomaly_score"],
                        "description": "Method for determining similarity",
                        "default": "yield",
                    },
                },
                "required": ["doc_id"],
            },
            "function": find_similar_batches,
        },
        {
            "name": "list_available_features",
            "description": "Get a list of all available process parameters/features that have importance scores.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": list_available_features,
        },
        {
            "name": "get_pipeline_status",
            "description": "Check which analysis outputs are available and get overall pipeline status. Useful for debugging and understanding available capabilities.",
            "parameters": {"type": "object", "properties": {}, "required": []},
            "function": get_pipeline_status,
        },
    ]


__all__ = [
    "get_top_anomalies",
    "explain_batch",
    "filter_anomalies_by_doc_ids",
    "get_anomaly_statistics",
    "get_top_yield_drivers",
    "get_feature_scores",
    "compare_feature_importance_methods",
    "get_pca_summary",
    "get_batch_pca_scores",
    "get_batch_shap_explanation",
    "get_global_shap_patterns",
    "compare_batches",
    "find_similar_batches",
    "list_available_features",
    "get_pipeline_status",
    "get_tool_specs",
    "set_redis_url",
    "clear_caches",
]
