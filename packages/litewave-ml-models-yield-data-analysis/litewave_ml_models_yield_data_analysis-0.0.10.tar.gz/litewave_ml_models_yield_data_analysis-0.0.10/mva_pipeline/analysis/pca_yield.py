from __future__ import annotations

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer

from ..redis_manager import get_redis_manager, is_redis_enabled

__all__ = ["supervised_pca"]

logger = logging.getLogger(__name__)
_DEF_OUTPUT = Path("outputs/pca")


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


# -----------------------------------------------------------------------------
# Supervised (yield-weighted) PCA
# -----------------------------------------------------------------------------


def supervised_pca(
    df: pd.DataFrame,
    *,
    target_col: str = "yield",
    var_threshold: float = 0.90,
):
    """Perform a simple **supervised PCA** by weighting each feature with its
    absolute *Pearson* correlation to the target before running standard PCA.

    The function persists (1) *scree* plot, (2) *biplot* of the first two PCs,
    and (3) components + loadings CSV files to ``outputs/pca/``.
    """
    # ------------------------------------------------------------------
    # Data prep: remove non-numeric, drop columns with low yield correlation
    # ------------------------------------------------------------------
    y = df[target_col].dropna()
    x_all = df.loc[y.index]
    doc_ids = x_all.get("doc_id", None)

    # --- FIX: Explicitly remove all yield-related columns from features ---
    yield_cols = [c for c in x_all.columns if "yield" in c.lower()]
    x_all = x_all.drop(columns=yield_cols, errors="ignore")

    x = x_all.select_dtypes(include=[np.number]).drop(
        columns=["doc_id"], errors="ignore"
    )

    # Remove columns with zero variance
    x = x.loc[:, x.var() > 1e-8]

    # Impute missing values
    imputer = SimpleImputer(strategy="median")
    x_imputed = pd.DataFrame(imputer.fit_transform(x), columns=x.columns, index=x.index)

    # Remove columns with low correlation (<0.01) to target to focus PCA (reduced from 0.05)
    corrs = x_imputed.corrwith(y).abs()
    x_filt = x_imputed.loc[:, corrs > 0.01]

    if x_filt.shape[1] < 2:
        logger.warning(
            "Not enough correlated numeric features for meaningful PCA - skipping"
        )
        return {}

    # Create output directory first
    _DEF_OUTPUT.mkdir(parents=True, exist_ok=True)

    # Yield correlation plot and CSV with business concepts
    top_corr = corrs.sort_values(ascending=False).head(15)

    # Create user-friendly version for plot and CSV
    business_concepts = [
        _map_feature_to_business_concept(str(feat)) for feat in top_corr.index
    ]
    top_corr_friendly = pd.Series(top_corr.values, index=business_concepts)

    # Plot with business concepts
    plt.figure(figsize=(12, 8))
    top_corr_friendly[::-1].plot(kind="barh")
    plt.title("Top features correlated with yield", fontsize=14)
    plt.xlabel("Correlation coefficient")
    plt.tight_layout()
    plt.savefig(_DEF_OUTPUT / "yield_correlations.png", dpi=300)
    plt.close()

    # Save CSV with both technical and user-friendly versions
    corr_user_friendly_df = pd.DataFrame(
        {"business_concept": business_concepts, "correlation": top_corr.values}
    )
    corr_user_friendly_df.to_csv(_DEF_OUTPUT / "yield_correlations.csv", index=False)

    # Technical version for internal use
    corr_technical_df = pd.DataFrame(
        {"feature": top_corr.index, "correlation": top_corr.values}
    )
    corr_technical_df.to_csv(
        _DEF_OUTPUT / "yield_correlations_technical.csv", index=False
    )

    # Fill remaining NaN with column means
    x_filt = x_filt.fillna(x_filt.mean())

    # Compute correlations with target and weight features
    correlations = x_filt.corrwith(y).abs()
    correlations = correlations.fillna(
        0
    )  # Handle cases where correlation can't be computed

    # Apply correlation-based weighting to features
    x_weighted = x_filt * np.sqrt(
        correlations + 1e-8
    )  # small epsilon to prevent zero weights

    # ------------------------------------------------------------------
    # Fit PCA and determine number of components
    # ------------------------------------------------------------------
    # Apply filtering
    x = x_filt

    # ------------------------------------------------------------------
    # Supervised PCA: weight covariance by |correlation| to target.
    # ------------------------------------------------------------------
    weights = corrs.loc[x.columns].abs().values
    weighted_x = x * np.sqrt(weights)

    pca = PCA()
    components = pca.fit_transform(weighted_x)

    # Find number of components for variance threshold
    cumvar = pca.explained_variance_ratio_.cumsum()
    n_components = int(np.argmax(cumvar >= var_threshold) + 1)

    # ------------------------------------------------------------------
    # Persist outputs
    # ------------------------------------------------------------------
    # 1. Scree plot
    plt.figure(figsize=(8, 5))
    plt.plot(
        range(1, min(21, len(pca.explained_variance_ratio_) + 1)),
        pca.explained_variance_ratio_[:20],
        "bo-",
    )
    plt.xlabel("Component Number")
    plt.ylabel("Explained Variance Ratio")
    plt.title("Scree Plot - Supervised PCA")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(_DEF_OUTPUT / "scree_plot.png", dpi=300)
    plt.close()

    # 2. Biplot (PC1 vs PC2) - using business concepts for labels
    if components.shape[1] >= 2:
        fig, ax = plt.subplots(figsize=(12, 10))

        # Plot samples colored by yield
        scatter = ax.scatter(
            components[:, 0],
            components[:, 1],
            c=y,
            cmap="RdYlBu_r",
            s=50,
            alpha=0.6,
            edgecolors="k",
            linewidth=0.5,
        )

        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label("Yield", fontsize=12)

        # Plot loading vectors
        loadings = pca.components_[:2, :].T * np.sqrt(pca.explained_variance_[:2])

        # Select top features to label (avoid clutter)
        loading_norms = np.linalg.norm(loadings, axis=1)
        top_loading_idx = np.argsort(loading_norms)[-10:]

        for i in top_loading_idx:
            ax.arrow(
                0,
                0,
                loadings[i, 0],
                loadings[i, 1],
                head_width=0.05,
                head_length=0.05,
                fc="red",
                ec="red",
                alpha=0.5,
            )

            # Add business concept name with some offset to avoid overlap
            offset_x = loadings[i, 0] * 1.1
            offset_y = loadings[i, 1] * 1.1
            feature_name = _map_feature_to_business_concept(str(x.columns[i]))
            # Truncate long feature names
            if len(feature_name) > 35:
                feature_name = feature_name[:32] + "..."
            ax.text(
                offset_x,
                offset_y,
                feature_name,
                fontsize=8,
                ha="center",
                va="center",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7),
            )

        ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)")
        ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)")
        ax.set_title("PCA Biplot - Yield-Weighted Features")
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(_DEF_OUTPUT / "biplot.png", dpi=300)
        plt.close()

    # 3. Component loadings CSV
    loadings_df = pd.DataFrame(
        pca.components_[:n_components, :].T,
        index=x.columns,
        columns=[f"PC{i+1}" for i in range(n_components)],
    )
    loadings_df.to_csv(_DEF_OUTPUT / "pca_loadings.csv")

    # 4. Components (transformed data)
    components_df = pd.DataFrame(
        components[:, :n_components], columns=[f"PC{i+1}" for i in range(n_components)]
    )
    if doc_ids is not None:
        components_df["doc_id"] = doc_ids.values
    components_df[target_col] = y.values
    components_df.to_csv(_DEF_OUTPUT / "pca_components.csv", index=False)

    # Store in Redis (for production use by agents)
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager()
            redis_manager.store_dataframe(
                "pca_loadings", loadings_df.reset_index()
            )  # Reset index to include feature names as column
            redis_manager.store_dataframe("pca_components", components_df)
        except Exception as e:
            logger.warning(f"Failed to store PCA results in Redis: {e}")
    else:
        logger.info("Redis storage disabled, skipping Redis storage for PCA results")

    logger.info(
        f"SUCCESS: Supervised PCA complete: {n_components} components explain {cumvar[n_components - 1]:.1%} variance"
    )
    logger.info(f"   DATA: User-friendly yield correlations: yield_correlations.csv")
    logger.info(
        f"   DATA: Technical yield correlations: yield_correlations_technical.csv"
    )

    return {
        "n_components": n_components,
        "variance_explained": cumvar[n_components - 1],
        "explained_variance_ratio": pca.explained_variance_ratio_.tolist(),
        "loadings": loadings_df,
        "components": components_df,
    }
