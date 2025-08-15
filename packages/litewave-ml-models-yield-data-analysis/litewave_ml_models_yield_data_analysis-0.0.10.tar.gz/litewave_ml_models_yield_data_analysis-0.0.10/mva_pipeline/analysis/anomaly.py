from __future__ import annotations

import json
import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from pyod.models.iforest import IForest  # pyod offers sklearn-like API
from sklearn.covariance import EllipticEnvelope, MinCovDet
from sklearn.impute import SimpleImputer
from sklearn.neighbors import LocalOutlierFactor

from ..builder import robust_scale_jitter
from ..redis_manager import get_redis_manager, is_redis_enabled

__all__ = ["detect", "golden_deviation"]

logger = logging.getLogger(__name__)
_DEF_OUTPUT = Path("outputs/anomaly")


# -----------------------------------------------------------------------------
# Core APIs
# -----------------------------------------------------------------------------


def detect(
    df: pd.DataFrame, *, link_key: str = "doc_id", weight_col: str | None = None
) -> pd.DataFrame:
    """Flag *batches* that appear *anomalous* according to an ensemble of three models.

    The implementation purposefully opts for **speed** over *absolute* accuracy -
    the main goal is to rapidly surface potentially problematic batches for
    further manual investigation. Returns the original dataframe with anomaly scores.
    """
    _DEF_OUTPUT.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Calculate contamination level from data
    # ------------------------------------------------------------------
    if "sample_type" in df.columns:
        n_anomalies = (df["sample_type"] == "Synthetic Anomaly").sum()
        contamination = n_anomalies / len(df) if len(df) > 0 else 0.0
    else:
        # Fallback if no synthetic data is used
        contamination = 0.02  # Default to 2%

    # Ensure contamination is within a reasonable range to avoid errors
    contamination = max(0.001, min(contamination, 0.5))
    logger.info(f"Using dynamic contamination level: {contamination:.3f}")

    # Extract numeric features for anomaly detection
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    # Exclude synthetic data artifacts that would bias anomaly detection
    exclude_cols = ["sample_weight"]  # This is a synthetic data artifact
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

    x_raw = df[numeric_cols].copy()

    # Remove columns with zero variance or too many NaN
    x = x_raw.loc[:, x_raw.var() > 1e-8]
    x = x.dropna(axis=1, thresh=int(len(x) * 0.5))

    if x.empty:
        logger.warning("No valid numeric features for anomaly detection")
        # Return original df with default anomaly columns
        result_df = df.copy()
        result_df["anomaly"] = False
        result_df["score_if"] = 0.0
        result_df["score_lof"] = 0.0
        result_df["dist_maha"] = 0.0
        return result_df

    # Median impute the remaining NaNs to keep algorithms happy.
    imp = SimpleImputer(strategy="median")
    x_imp = pd.DataFrame(imp.fit_transform(x), columns=x.columns, index=x.index)

    # Check if we have any non-null rows after cleaning
    if len(x_imp) == 0:
        logger.warning("No valid rows for anomaly detection after cleaning")
        result_df = df.copy()
        result_df["anomaly"] = False
        result_df["score_if"] = 0.0
        result_df["score_lof"] = 0.0
        result_df["dist_maha"] = 0.0
        return result_df

    # Scale the data for better anomaly detection
    x_scaled = robust_scale_jitter(x_imp)

    # ------------------------------------------------------------------
    # Fit three anomaly detection models
    # ------------------------------------------------------------------
    models = {}

    try:
        # 1. Isolation Forest
        models["IF"] = IForest(contamination=contamination, random_state=0)
        if_scores = models["IF"].fit_predict(x_scaled)
        if_outlier_scores = models["IF"].decision_function(x_scaled)
    except Exception as e:
        logger.warning(f"Isolation Forest failed: {e}")
        if_scores = np.zeros(len(x_scaled))
        if_outlier_scores = np.zeros(len(x_scaled))

    try:
        # 2. Local Outlier Factor - use 'auto' for contamination
        models["LOF"] = LocalOutlierFactor(contamination="auto", novelty=False)
        lof_scores = models["LOF"].fit_predict(x_scaled)
        lof_outlier_scores = models["LOF"].negative_outlier_factor_
    except Exception as e:
        logger.warning(f"LOF failed: {e}")
        lof_scores = np.zeros(len(x_scaled))
        lof_outlier_scores = np.zeros(len(x_scaled))

    try:
        # 3. Robust covariance (Mahalanobis distance)
        robust_cov = MinCovDet(random_state=0)
        robust_cov.fit(x_scaled)
        maha_dists = robust_cov.mahalanobis(x_scaled)
    except Exception as e:
        logger.warning(f"Mahalanobis distance failed: {e}")
        maha_dists = np.zeros(len(x_scaled))

    try:
        # 4. Elliptic Envelope
        models["EE"] = EllipticEnvelope(contamination=contamination, random_state=0)
        ee_scores = models["EE"].fit_predict(x_scaled)
    except Exception as e:
        logger.warning(f"Elliptic Envelope failed: {e}")
        ee_scores = np.zeros(len(x_scaled))

    # ------------------------------------------------------------------
    # Ensemble voting: models return -1 for anomalies, 1 for normal
    # ------------------------------------------------------------------
    # Convert Mahalanobis distances to binary anomaly scores
    maha_threshold = np.percentile(maha_dists, 100 * (1 - contamination))
    maha_scores = (maha_dists > maha_threshold).astype(int) * -2 + 1

    votes = (
        (if_scores == -1).astype(int)
        + (lof_scores == -1).astype(int)
        + (ee_scores == -1).astype(int)
        + (maha_scores == -1).astype(int)
    )

    # Build results dataframe
    result_df = df[[link_key]].copy()
    result_df["anomaly"] = votes >= 2  # Require 2 out of 4 models to agree
    result_df["score_if"] = if_scores
    result_df["score_lof"] = lof_scores
    result_df["score_ee"] = ee_scores
    result_df["dist_maha"] = maha_dists

    # Add anomaly flags from each model for better reporting
    result_df["is_anomaly_if"] = if_scores == -1
    result_df["is_anomaly_lof"] = lof_scores == -1
    result_df["is_anomaly_ee"] = ee_scores == -1
    result_df["is_anomaly_maha"] = maha_scores == -1

    # Count anomalies for logging
    n_anomalies = result_df["anomaly"].sum()
    logger.info(
        f"SUCCESS: Anomaly detection complete: {n_anomalies}/{len(df)} batches flagged"
    )

    # -------------------------------------------------------------------
    # Enhanced feature deviation analysis with user-friendly descriptions
    # -------------------------------------------------------------------
    # Z-score of each feature (relative to training data statistics)
    zscores = (x_imp - x_imp.mean()) / x_imp.std()
    zscores_abs = zscores.abs()  # absolute deviation

    # Filter out ID-like features and synthetic artifacts for explanations
    # Updated patterns to be more specific and preserve valuable ATRS/RMI data
    id_patterns = [
        "_id_",
        "_ref_",
        "doc_id",
        "sample_weight",
        "page_no",
        "format_no",
        "revision_no",
        "prepared_by",
        "reviewed_by",
        "approved_by",
        "sign_date",
    ]
    meaningful_cols = [
        col
        for col in zscores.columns
        if not any(pattern in col.lower() for pattern in id_patterns)
    ]

    if meaningful_cols:
        zscores_filtered = zscores[meaningful_cols]
        zscores_abs_filtered = zscores_abs[meaningful_cols]
    else:
        zscores_filtered = zscores  # Fallback if all columns filtered out
        zscores_abs_filtered = zscores_abs

    def _format_feature_name(feature_name: str) -> str:
        """Convert technical feature names to business-friendly names."""
        name = (
            feature_name.replace("public.bprpoc_", "")
            .replace("public.rmi_", "")
            .replace("public.bprv53_", "")
            .replace("public.atrs_", "")
        )
        name = name.replace("__", " → ").replace("_", " ")
        return name

    def _describe_severity(z_score: float) -> str:
        """Convert z-score to user-friendly severity description."""
        abs_z = abs(z_score)
        if abs_z >= 8.0:
            return "severely"
        elif abs_z >= 3.0:
            return "significantly"
        elif abs_z >= 2.0:
            return "moderately"
        else:
            return "slightly"

    def _get_direction(z_score: float) -> str:
        """Get direction description from z-score."""
        return "too high" if z_score > 0 else "too low"

    # Get top 3 deviating features for each row
    top_feats_list = []
    top_z_list = []
    detailed_explanations = []

    for idx in zscores_abs_filtered.index:
        row_scores_abs = zscores_abs_filtered.loc[idx].sort_values(ascending=False)
        row_scores_signed = zscores_filtered.loc[idx]
        top_3_feats = row_scores_abs.head(3)

        # Create user-friendly descriptions
        feat_descriptions = []
        detailed_feat_info = []

        for feat, abs_z in top_3_feats.items():
            signed_z = row_scores_signed[feat]

            # Format feature name for readability
            display_name = _format_feature_name(feat)
            severity = _describe_severity(signed_z)
            direction = _get_direction(signed_z)

            # User-friendly description
            feat_descriptions.append(f"{display_name} is {severity} {direction}")

            # Detailed information for API
            detailed_feat_info.append(
                {
                    "feature": feat,
                    "z_score": float(signed_z),
                    "abs_z_score": float(abs_z),
                    "direction": "high" if signed_z > 0 else "low",
                    "severity": severity,
                    "display_name": display_name,
                }
            )

        top_feats_list.append(" | ".join(feat_descriptions))
        top_z_list.append(top_3_feats.iloc[0])  # Highest z-score for sorting
        detailed_explanations.append(detailed_feat_info)

    result_df["top_dev_feat"] = top_feats_list
    result_df["top_dev_z"] = top_z_list
    result_df["top_dev_feat_details"] = [
        json.dumps(details) for details in detailed_explanations
    ]

    # Add all original columns back to the result
    result_df = pd.concat([result_df, df.drop(columns=[link_key])], axis=1)

    # Persist to local CSV (for development)
    _DEF_OUTPUT.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(_DEF_OUTPUT / "anomaly_results.csv", index=False)

    # Store in Redis (for production use by agents)
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager()
            redis_manager.store_dataframe("anomaly_results", result_df)
        except Exception as e:
            logger.warning(f"Failed to store anomaly results in Redis: {e}")
    else:
        logger.info(
            "Redis storage disabled, skipping Redis storage for anomaly results"
        )

    # Create focused anomaly overview plot
    if len(result_df) > 0:
        try:
            _create_anomaly_overview(
                result_df, maha_dists, float(maha_threshold), x_imp.columns
            )
        except Exception as e:
            logger.warning(f"Anomaly visualization failed: {e}")

    return result_df


# -----------------------------------------------------------------------------
# Golden-batch deviation (simplified - fast)
# -----------------------------------------------------------------------------


def golden_deviation(
    df: pd.DataFrame,
    *,
    link_key: str = "doc_id",
    target_col: str = "yield",
) -> pd.DataFrame:
    """Compute per-batch deviation from a *golden* reference (top-3 yield).

    For the sake of the demo timeline the deviation metric is the **mean
    absolute error** across numeric features instead of a full DTW/SMAPE combo -
    still conveys the idea while executing in milliseconds.
    """
    num_cols = df.select_dtypes(include=[np.number]).columns.difference([target_col])
    top3_idx = df.nlargest(3, target_col).index
    golden_vec = df.loc[top3_idx, num_cols].mean()

    deviation = df[num_cols].sub(golden_vec, axis=1).abs().mean(axis=1)

    return pd.DataFrame({link_key: df[link_key], "golden_dev": deviation})


def _create_anomaly_overview(
    result_df: pd.DataFrame,
    maha_dists: np.ndarray,
    maha_threshold: float,
    feature_names,
) -> None:
    """Create a focused anomaly overview plot showing Mahalanobis distances and explanations."""

    # Identify anomalous batches and get their doc_ids
    anomalous_mask = result_df["anomaly"]
    anomalous_batches = result_df[anomalous_mask]

    fig, ax = plt.subplots(1, 1, figsize=(12, 8))  # Single plot only

    # Single scatter plot of Mahalanobis distances by batch index
    batch_indices = np.arange(len(result_df))
    colors = ["red" if is_anom else "skyblue" for is_anom in anomalous_mask]

    scatter = ax.scatter(batch_indices, maha_dists, c=colors, alpha=0.7, s=50)

    # Add threshold line
    ax.axhline(
        maha_threshold,
        color="orange",
        linestyle="--",
        linewidth=2,
        label=f"Anomaly Threshold = {maha_threshold:.2f}",
    )

    # Annotate top 5 anomalies with batch IDs
    if len(anomalous_batches) > 0:
        top_5_anomalies = anomalous_batches.nlargest(5, columns="dist_maha")
        for _, row in top_5_anomalies.iterrows():
            doc_id = row["doc_id"]
            batch_idx = np.where(result_df["doc_id"] == doc_id)[0][0]
            maha_dist = float(row["dist_maha"])

            ax.annotate(
                f"Batch {doc_id}",
                xy=(batch_idx, maha_dist),
                xytext=(10, 10),
                textcoords="offset points",
                fontsize=8,
                alpha=0.8,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7),
            )

    ax.set_xlabel("Batch Index")
    ax.set_ylabel("Mahalanobis Distance")
    ax.set_title(
        "Anomaly Detection: Mahalanobis Distance by Batch",
        fontsize=14,
        fontweight="bold",
    )

    # Create custom legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(
            facecolor="skyblue",
            alpha=0.7,
            label=f"Normal batches (n={(~anomalous_mask).sum()})",
        ),
        Patch(
            facecolor="red",
            alpha=0.7,
            label=f"Anomalous batches (n={anomalous_mask.sum()})",
        ),
        Line2D(
            [0],
            [0],
            color="orange",
            linestyle="--",
            linewidth=2,
            label="Detection Threshold",
        ),
    ]
    ax.legend(handles=legend_elements)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(_DEF_OUTPUT / "anomaly_overview.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Also save a detailed anomaly report
    if len(anomalous_batches) > 0 and isinstance(anomalous_batches, pd.DataFrame):
        _save_anomaly_report(anomalous_batches)


def _save_anomaly_report(anomalous_batches: pd.DataFrame) -> None:
    """Save a human-readable report of anomalous batches."""
    report_path = _DEF_OUTPUT / "anomaly_report.txt"

    with open(report_path, "w") as f:
        f.write("ANOMALY DETECTION REPORT\n")
        f.write("==================================================\n")
        f.write(f"Total anomalous batches detected: {len(anomalous_batches)}\n\n")

        # Sort by deviation severity
        sorted_anomalies = anomalous_batches.sort_values("top_dev_z", ascending=False)

        f.write("BATCH DETAILS:\n")
        f.write("------------------------------\n")
        for _, row in sorted_anomalies.iterrows():
            is_synthetic = row.get("sample_type", "Real") == "Synthetic"
            batch_type = "Synthetic" if is_synthetic else "Real"

            # Use the precise sample_type from the data if available
            if "sample_type" in row:
                batch_type = row["sample_type"]

            f.write(f"• {batch_type} Batch {row['doc_id']}:\n")
            f.write(f"  - Mahalanobis distance: {row['dist_maha']:.3f}\n")

            # Add voting details with full names
            votes = []
            if row.get("is_anomaly_if"):
                votes.append("Isolation Forest")
            if row.get("is_anomaly_lof"):
                votes.append("Local Outlier Factor")
            if row.get("is_anomaly_ee"):
                votes.append("Elliptic Envelope")
            if row.get("is_anomaly_maha"):
                votes.append("Mahalanobis Distance")
            f.write(f"  - Flagged by: {', '.join(votes)}\n")

            if (
                "top_dev_feat" in row
                and pd.notna(row["top_dev_feat"])
                and str(row["top_dev_feat"]).strip()
            ):
                f.write(f"  - Issues detected: {row['top_dev_feat']}\n")

    logger.info(
        f"REPORT: Detailed anomaly report saved to {_DEF_OUTPUT}/anomaly_report.txt"
    )
