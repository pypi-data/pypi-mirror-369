from __future__ import annotations

import logging
from pathlib import Path

import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.impute import SimpleImputer
from sklearn.model_selection import KFold
from tqdm import tqdm

from ..redis_manager import get_redis_manager, is_redis_enabled

__all__ = ["run"]

logger = logging.getLogger(__name__)
_DEF_OUTPUT = Path("outputs/rca")


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
# Root-cause analysis via LightGBM + SHAP
# -----------------------------------------------------------------------------


def _train_model(
    x: pd.DataFrame, y: pd.Series, *, sample_weight: pd.Series | None = None
) -> lgb.LGBMRegressor:
    mdl = lgb.LGBMRegressor(
        max_depth=3,
        n_estimators=100,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_samples=20,
        reg_alpha=0.1,
        reg_lambda=0.1,
        random_state=0,
        verbosity=-1,
    )
    mdl.fit(x, y, sample_weight=sample_weight)
    return mdl


def run(
    df: pd.DataFrame,
    *,
    target_col: str = "yield",
    k_features: int = 15,
    cv_folds: int = 5,
) -> dict:
    """Fit LightGBM to predict ``target_col`` and compute SHAP-based feature importance.

    Returns dictionary with analysis results and saves plots/CSVs to ``outputs/rca/``.
    """
    # ------------------------------------------------------------------
    # Data prep
    # ------------------------------------------------------------------
    y = df[target_col].dropna()
    x_all = df.loc[y.index]
    doc_ids = x_all.get("doc_id", None)

    x = x_all.select_dtypes(include=[np.number]).drop(
        columns=["doc_id", target_col], errors="ignore"
    )

    # Remove columns with zero variance
    x = x.loc[:, x.var() > 1e-8]
    x = x.dropna(axis=1, thresh=int(len(x) * 0.5))  # Keep columns with ≥50% non-null

    # Median impute remaining NaNs
    if x.empty:
        logger.warning("No usable numeric features for root-cause analysis")
        return {}

    imp = SimpleImputer(strategy="median")
    x_imp = pd.DataFrame(imp.fit_transform(x), columns=x.columns, index=x.index)

    sample_weight = df.loc[y.index].get("sample_weight", None)

    # ------------------------------------------------------------------
    # Cross-validation and model training
    # ------------------------------------------------------------------
    logger.info(f"TRAINING: Training LightGBM with {cv_folds}-fold CV...")

    kf = KFold(n_splits=cv_folds, shuffle=True, random_state=0)
    cv_scores = []

    for train_idx, test_idx in kf.split(x_imp):  # noqa: B007 - loop not useless
        mdl = _train_model(
            x_imp.iloc[train_idx],
            y.iloc[train_idx],
            sample_weight=(
                sample_weight.iloc[train_idx] if sample_weight is not None else None
            ),
        )
        score = mdl.score(x_imp.iloc[test_idx], y.iloc[test_idx])
        cv_scores.append(score)

    logger.info(f"   CV R² score: {np.mean(cv_scores):.3f} ± {np.std(cv_scores):.3f}")

    # Train final model on all data
    final_model = _train_model(x_imp, y, sample_weight=sample_weight)

    # ------------------------------------------------------------------
    # SHAP analysis
    # ------------------------------------------------------------------
    logger.info("ANALYSIS: Computing SHAP values...")
    explainer = shap.TreeExplainer(final_model)
    shap_values = explainer.shap_values(x_imp)

    # Global feature importance (mean absolute SHAP)
    glob_shap = np.mean(np.abs(shap_values), axis=0)
    feat_imp = pd.Series(glob_shap, index=x_imp.columns).sort_values(ascending=False)

    # ------------------------------------------------------------------
    # Save results
    # ------------------------------------------------------------------
    _DEF_OUTPUT.mkdir(parents=True, exist_ok=True)

    # 1. Feature importance CSV - both user-friendly and technical versions
    topk = feat_imp.head(k_features)

    # User-friendly version with business concepts
    user_friendly_df = pd.DataFrame(
        {
            "business_concept": [
                _map_feature_to_business_concept(str(f)) for f in topk.index
            ],
            "importance_score": topk.values,
        }
    )
    user_friendly_df.to_csv(_DEF_OUTPUT / "feature_importance.csv", index=False)

    # Technical version for internal use
    technical_df = pd.DataFrame(
        {"feature": topk.index, "importance_score": topk.values}
    )
    technical_df.to_csv(_DEF_OUTPUT / "feature_importance_technical.csv", index=False)

    # 2. Feature importance plot using business concepts
    business_concepts = [_map_feature_to_business_concept(str(f)) for f in topk.index]
    plt.figure(figsize=(10, 6))
    topk_with_concepts = pd.Series(topk.values, index=business_concepts)
    topk_with_concepts[::-1].plot(kind="barh")
    plt.title("Top yield drivers (SHAP mean |value|)")
    plt.xlabel("SHAP Importance Score")
    plt.tight_layout()
    plt.savefig(_DEF_OUTPUT / "feature_importance.png", dpi=150)
    plt.close()

    # 3. SHAP summary plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, x_imp, max_display=k_features, show=False)
    plt.tight_layout()
    plt.savefig(_DEF_OUTPUT / "shap_summary.png", dpi=120, bbox_inches="tight")
    plt.close()

    # 4. Save model and SHAP values
    import joblib

    joblib.dump(final_model, _DEF_OUTPUT / "lightgbm_model.joblib")

    shap_df = pd.DataFrame(shap_values, columns=x_imp.columns)
    if doc_ids is not None:
        shap_df["doc_id"] = doc_ids.values
    shap_df[target_col] = y.values
    shap_df.to_csv(_DEF_OUTPUT / "shap_values.csv", index=False)

    # Store in Redis (for production use by agents)
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager()
            redis_manager.store_dataframe("rca_feature_importance", user_friendly_df)
            redis_manager.store_dataframe("shap_values", shap_df)
        except Exception as e:
            logger.warning(f"Failed to store RCA results in Redis: {e}")
    else:
        logger.info("Redis storage disabled, skipping Redis storage for RCA results")

    logger.info(
        f"SUCCESS: Root cause analysis complete: {len(feat_imp)} features analyzed"
    )
    logger.info(f"   DATA: User-friendly results: feature_importance.csv")
    logger.info(f"   DATA: Technical results: feature_importance_technical.csv")

    return {
        "feature_importance": feat_imp,
        "cv_scores": cv_scores,
        "model": final_model,
        "shap_values": shap_values,
    }
