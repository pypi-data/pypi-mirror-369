"""Unified feature importance combining PCA and SHAP insights."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..redis_manager import get_redis_manager, is_redis_enabled

logger = logging.getLogger(__name__)


def _map_feature_to_business_concept(feature_name: str) -> str:
    """Convert statistical feature names to meaningful business insights.

    Converts features like 'public.bprpoc_temp_records__temperature_max'
    to 'Process Temperature - Peak Values' to show what this tells us about the process.
    """
    # Remove the technical database prefixes
    clean_name = feature_name.replace("public.bprpoc_", "").replace("public.", "")

    # Extract statistical aggregation and convert to business meaning
    stat_insight = ""
    business_relevance = {
        "_min": "Minimum Levels",
        "_max": "Peak Values",
        "_mean": "Typical Levels",
        "_std": "Process Consistency",  # High std = inconsistent process
        "_r0": "Base Reading",
        "_r1": "Stage 1",
        "_r2": "Stage 2",
        "_r3": "Stage 3",
        "_r4": "Stage 4",
        "_r5": "Final Stage",
    }

    for suffix, business_meaning in business_relevance.items():
        if clean_name.endswith(suffix):
            stat_insight = f" - {business_meaning}"
            clean_name = clean_name[: -len(suffix)]
            break

    # Map to business processes with document context
    if "atrs_test_details" in clean_name:
        if "results" in clean_name:
            return f"ATRS Quality Control Testing{stat_insight}"
        return f"ATRS Quality Specifications{stat_insight}"

    elif "rmi_materials" in clean_name:
        if "quantity_issued" in clean_name:
            return f"RMI Material Issuance{stat_insight}"
        elif "quantity_indented" in clean_name:
            return f"RMI Material Requisition{stat_insight}"
        return f"RMI Raw Material Inventory{stat_insight}"

    elif "temp_records__temperature" in clean_name:
        return f"BPR Process Temperature{stat_insight}"

    elif "temp_vacuum_records__vacuum" in clean_name:
        return f"BPR Vacuum Control{stat_insight}"

    elif "weighing_details__net_wt" in clean_name:
        return f"BPR Net Weight Control{stat_insight}"

    elif "weighing_details__gross_wt" in clean_name:
        return f"BPR Gross Weight Control{stat_insight}"

    elif "weighing_details__tare_wt" in clean_name:
        return f"BPR Container Weight{stat_insight}"

    elif "material_usage_details__actual_quantity" in clean_name:
        return f"BPR Actual Material Usage{stat_insight}"

    elif "material_usage_details__standard_quantity" in clean_name:
        return f"BPR Standard Material Usage{stat_insight}"

    elif "raw_material_usage_records__initial_volume" in clean_name:
        return f"BPR Initial Raw Material Volume{stat_insight}"

    elif "raw_material_usage_records__final_volume" in clean_name:
        return f"BPR Final Raw Material Volume{stat_insight}"

    elif "nitrogen_details__n2_pressure" in clean_name:
        return f"BPR Nitrogen Pressure Control{stat_insight}"

    elif "ph_records__ph" in clean_name:
        return f"BPR pH Control{stat_insight}"

    elif "pressure_records__pressure" in clean_name:
        return f"BPR Pressure Control{stat_insight}"

    # Handle special cases
    elif "doc_id" in clean_name.lower():
        return "Batch Identifier"

    elif "sample_weight" in clean_name.lower():
        return "Data Quality Weight"

    # Fallback: create meaningful name from components
    if "__" in clean_name:
        table_part = clean_name.split("__")[0]
        column_part = clean_name.split("__", 1)[1] if "__" in clean_name else ""

        # Map table types to business areas
        if "temp" in table_part:
            base_concept = "Temperature Control"
        elif "material_usage" in table_part:
            base_concept = "Material Consumption"
        elif "weighing" in table_part:
            base_concept = "Weight Management"
        elif "raw_material" in table_part:
            base_concept = "Raw Material Control"
        elif "nitrogen" in table_part:
            base_concept = "Gas Control"
        else:
            base_concept = table_part.replace("_", " ").title()

        # Add specific measurement context
        if "quantity" in column_part:
            measurement = "Quantity"
        elif "volume" in column_part:
            measurement = "Volume"
        elif "weight" in column_part or "wt" in column_part:
            measurement = "Weight"
        elif "temperature" in column_part:
            measurement = "Temperature"
        elif "pressure" in column_part:
            measurement = "Pressure"
        elif "vacuum" in column_part:
            measurement = "Vacuum"
        else:
            measurement = column_part.replace("_", " ").title()

        if measurement.lower() != base_concept.lower():
            return f"{base_concept} - {measurement}{stat_insight}"
        else:
            return f"{base_concept}{stat_insight}"

    # Final fallback
    readable = (
        clean_name.replace("__", " - ")
        .replace("_", " ")
        .title()
        .replace("Bprpoc", "")
        .replace("Public", "")
        .strip()
    )

    return f"{readable}{stat_insight}" if readable else feature_name


def compute_unified_importance(
    pca_result: dict,
    rca_result: dict,
    *,
    top_k: int = 20,
) -> pd.DataFrame:
    """Combine PCA loadings and SHAP importance into unified feature ranking.

    The approach:
    1. Take absolute PCA loadings for the first 2 components
    2. Weight by explained variance ratio
    3. Filter out ID/batch number features that are artifacts
    4. Combine with SHAP importance using weighted average (70% SHAP, 30% PCA)
    5. Map technical feature names to business concepts for user reporting
    6. Return top-k features
    """
    # Extract PCA loadings
    if "loadings" not in pca_result or pca_result["loadings"] is None:
        logger.warning("No PCA loadings found")
        return pd.DataFrame()

    loadings = pca_result["loadings"]
    n_components = min(2, loadings.shape[1])  # Use first 2 components

    # Weight loadings by explained variance
    variance_ratios = pca_result.get("explained_variance_ratio", [0.5, 0.5])[
        :n_components
    ]

    # Compute weighted absolute loadings
    pca_importance = pd.Series(0.0, index=loadings.index)
    for i in range(n_components):
        pca_importance += np.abs(loadings.iloc[:, i]) * variance_ratios[i]

    # Extract SHAP importance
    shap_importance = rca_result.get("feature_importance", pd.Series())
    if shap_importance.empty:
        logger.warning("No SHAP importance found")
        return pd.DataFrame()

    shap_values = shap_importance.copy()

    # Align indices
    common_features = pca_importance.index.intersection(shap_values.index)
    pca_aligned = pca_importance[common_features]
    shap_aligned = shap_values[common_features]

    # Filter out obvious ID/batch number features that are artifacts
    # Updated to be more specific and preserve valuable ATRS/RMI data
    id_patterns = [
        "doc_id",
        "_ref_",
        "revision_no",
        "format_no",
        "page_no",
        "prepared_by",
        "reviewed_by",
        "approved_by",
        "sign_date",
        "department_name",
        "effective_date",
    ]

    def is_likely_id_feature(feature_name: str) -> bool:
        """Check if feature is likely an ID/batch number that doesn't affect yield."""
        feature_lower = feature_name.lower()
        # Don't filter out ATRS test data or RMI material data even if they contain some ID patterns
        if "atrs" in feature_lower and any(
            keyword in feature_lower
            for keyword in ["test", "results", "specification", "qc", "stage"]
        ):
            return False
        if "rmi" in feature_lower and any(
            keyword in feature_lower
            for keyword in ["material", "quantity", "usage", "issued", "indented"]
        ):
            return False
        return any(pattern in feature_lower for pattern in id_patterns)

    # Filter features
    meaningful_features = [
        str(f) for f in common_features if not is_likely_id_feature(str(f))
    ]

    if not meaningful_features:
        logger.warning("No meaningful features found after filtering")
        return pd.DataFrame()

    pca_filtered = pd.Series(pca_aligned[meaningful_features])
    shap_filtered = pd.Series(shap_aligned[meaningful_features])

    # Normalize after filtering
    pca_filtered = (
        pca_filtered / pca_filtered.sum() if pca_filtered.sum() > 0 else pca_filtered
    )
    shap_filtered = (
        shap_filtered / shap_filtered.sum()
        if shap_filtered.sum() > 0
        else shap_filtered
    )

    # Combine with weighted average: 70% SHAP (predictive power), 30% PCA (variance explanation)
    # SHAP is more reliable for yield prediction, PCA captures overall data variance
    unified_importance = shap_filtered * 0.7 + pca_filtered * 0.3

    # Sort and get top-k
    unified_importance = unified_importance.sort_values(ascending=False).head(top_k)

    # Create result dataframe with both technical and business-friendly names
    result = pd.DataFrame(
        {
            "feature": unified_importance.index.tolist(),
            "business_concept": [
                _map_feature_to_business_concept(str(f))
                for f in unified_importance.index
            ],
            "unified_score": unified_importance.tolist(),
            "pca_score": pca_filtered[unified_importance.index].tolist(),
            "shap_score": shap_filtered[unified_importance.index].tolist(),
        }
    )

    # Create visualization
    _plot_unified_importance(result)

    return result


def _plot_unified_importance(
    importance_df: pd.DataFrame, output_dir: Path = Path("outputs/unified")
):
    """Create bar plot showing unified feature importance."""
    output_dir.mkdir(parents=True, exist_ok=True)

    if importance_df.empty:
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Unified importance using business concepts
    top_10 = importance_df.head(10)
    y_pos = np.arange(len(top_10))

    ax1.barh(y_pos, top_10["unified_score"], color="darkblue", alpha=0.8)
    ax1.set_yticks(y_pos)
    # Use business concepts for readability, truncate if too long
    labels = [f[:30] + "..." if len(f) > 30 else f for f in top_10["business_concept"]]
    ax1.set_yticklabels(labels)
    ax1.set_xlabel("Unified Importance Score")
    ax1.set_title("Top 10 Yield Drivers (Combined PCA + SHAP)", fontsize=14)
    ax1.invert_yaxis()

    # Plot 2: Comparison of PCA vs SHAP
    x = np.arange(len(top_10))
    width = 0.35

    ax2.bar(
        x - width / 2,
        top_10["pca_score"],
        width,
        label="PCA",
        color="skyblue",
        alpha=0.8,
    )
    ax2.bar(
        x + width / 2,
        top_10["shap_score"],
        width,
        label="SHAP",
        color="lightcoral",
        alpha=0.8,
    )

    ax2.set_xlabel("Features")
    ax2.set_ylabel("Normalized Score")
    ax2.set_title("PCA vs SHAP Importance Comparison", fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{i+1}" for i in range(len(top_10))])
    ax2.legend()

    plt.tight_layout()
    plt.savefig(
        output_dir / "unified_feature_importance.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # Save both technical and user-friendly versions to CSV

    # User-friendly version with business concepts
    user_friendly_df = importance_df[
        ["business_concept", "unified_score", "pca_score", "shap_score"]
    ].copy()
    user_friendly_df.to_csv(output_dir / "unified_feature_importance.csv", index=False)

    # Technical version for internal use (preserves original feature names)
    technical_df = importance_df[
        ["feature", "unified_score", "pca_score", "shap_score"]
    ].copy()
    technical_df.to_csv(
        output_dir / "unified_feature_importance_technical.csv", index=False
    )

    # Store in Redis (for production use by agents)
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager()
            redis_manager.store_dataframe("unified_importance", user_friendly_df)
        except Exception as e:
            logger.warning(f"Failed to store unified importance in Redis: {e}")
    else:
        logger.info(
            "Redis storage disabled, skipping Redis storage for unified importance"
        )

    logger.info(f"SUCCESS: Unified feature importance saved to {output_dir}/")
    logger.info(f"   DATA: User-friendly version: unified_feature_importance.csv")
    logger.info(f"   DATA: Technical version: unified_feature_importance_technical.csv")
