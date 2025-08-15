import logging
import re
from functools import reduce
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yaml

from mva_pipeline.llm_filter import filter_columns_with_llm

logger = logging.getLogger(__name__)
# -----------------------------------------------------------------------------
# Public helpers
# -----------------------------------------------------------------------------

_RE_NUMERIC = re.compile(r"[^0-9+\-.eE]")


def clean_numeric(series: pd.Series) -> pd.Series:
    """Return *series* with non-numeric characters stripped then cast to float.

    Any value that still fails to parse as ``float`` becomes ``NaN``. The helper
    is intentionally conservative - it is meant for quick demo-level cleanup of
    numerical columns that may contain engineering units, commas, or other
    artefacts (e.g. ``"1,234 rpm"`` → ``1234``).
    """
    if series.dtype.kind in {"i", "f", "u"}:
        return series  # Already numeric

    def _to_float(val: str | int | float) -> float:  # noqa: ANN401 - loose typing
        try:
            # Handle None, NaN, empty strings
            if pd.isna(val) or str(val).lower() in ("none", "nan", ""):
                return float("nan")

            val_str = str(val).strip()

            # First, check if it's a European-style decimal (e.g., "670,00")
            # Pattern: digits + comma + exactly 2 digits at end
            if re.match(r"^\d+,\d{2}$", val_str):
                val_str = val_str.replace(",", ".")

            # Remove common units at the end (kg, g, ml, etc.)
            val_str = re.sub(
                r"\s*(kg|g|ml|l|°C|°F|%|rpm)\s*$", "", val_str, flags=re.IGNORECASE
            )

            # Remove thousands separators (commas not followed by exactly 2 digits)
            val_str = re.sub(r",(?!\d{2}$)", "", val_str)

            # Handle dashes that aren't minus signs (e.g., "652-0" should be invalid)
            if "-" in val_str and not re.match(r"^-?\d", val_str):
                return float("nan")

            # Now try to parse
            return float(val_str) if val_str else float("nan")
        except ValueError:
            return float("nan")

    return series.apply(_to_float)  # type: ignore[return-value]


# -----------------------------------------------------------------------------
# Configuration loading
# -----------------------------------------------------------------------------


def _load_config(config_path: str | Path | None = None) -> dict:
    """Load configuration file with filtering patterns."""
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {}


def _apply_config_based_filtering(
    df: pd.DataFrame, config: dict, link_key: str
) -> pd.DataFrame:
    """Apply whitelist/blacklist filtering based on config patterns."""
    if df.empty:
        return df

    # Get patterns from config
    whitelist_pattern = config.get("feature_whitelist", "")
    blacklist_pattern = config.get("feature_blacklist", "")

    columns_to_keep = [link_key]  # Always keep the link key

    for col in df.columns:
        if col == link_key:
            continue

        # Check blacklist first (more restrictive)
        if blacklist_pattern and re.search(blacklist_pattern, col, re.IGNORECASE):
            continue  # Skip blacklisted columns

        # Check whitelist
        if whitelist_pattern and re.search(whitelist_pattern, col, re.IGNORECASE):
            columns_to_keep.append(col)
            continue

        # Special handling for ATRS QC data - keep test results even if not in whitelist
        if "atrs" in col.lower() and any(
            keyword in col.lower()
            for keyword in ["test", "results", "specification", "qc", "stage"]
        ):
            columns_to_keep.append(col)
            continue

        # Special handling for RMI material data - keep material tracking even if not in whitelist
        if "rmi" in col.lower() and any(
            keyword in col.lower() for keyword in ["material", "raw_material", "units"]
        ):
            columns_to_keep.append(col)
            continue

    # Filter dataframe
    filtered_df = df[columns_to_keep]

    dropped_cols = len(df.columns) - len(filtered_df.columns)
    if dropped_cols > 0:
        logger.info(
            f"   Config-based filtering: kept {len(filtered_df.columns)} / {len(df.columns)} columns"
        )

    return filtered_df


# -----------------------------------------------------------------------------
# Batch-matrix builder
# -----------------------------------------------------------------------------


def _pivot_narrow_table(df: pd.DataFrame, link_key: str, max_rows: int) -> pd.DataFrame:
    """Pivot tables with *≤ max_rows* per ``link_key`` to a wide representation."""

    # Tag original order within each *link_key* group - this later becomes the
    # column suffix ``_r{idx}``.
    df = df.copy()
    df["__row_idx"] = df.groupby(link_key).cumcount()

    values_cols: list[str] = [c for c in df.columns if c not in {link_key, "__row_idx"}]
    wide = (
        df.pivot_table(
            index=link_key, columns="__row_idx", values=values_cols, aggfunc="first"
        )
        .sort_index(axis=1)  # deterministic column order
        .reset_index()
    )

    # Flatten the resulting MultiIndex - ``col_r{row}``.
    flat_cols: list[str] = []
    for col in wide.columns.to_flat_index():
        if isinstance(col, tuple):
            base, idx = col
            flat_cols.append(link_key if base == link_key else f"{base}_r{idx}")
        else:
            flat_cols.append(col)
    wide.columns = flat_cols
    return wide


def _aggregate_wide_table(df: pd.DataFrame, link_key: str) -> pd.DataFrame:
    """Aggregate tables with many rows per ``link_key`` using simple stats."""
    # Attempt to coerce object columns to float where feasible to ensure aggregation works.
    df = df.copy()
    for col in df.select_dtypes(include=["object"]).columns.difference([link_key]):
        df[col] = clean_numeric(df[col])  # type: ignore[arg-type]

    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if link_key in numeric_cols:
        numeric_cols.remove(link_key)

    logger.info(
        f"Aggregating table. Link key: {link_key}. Numeric columns: {numeric_cols}"
    )

    if not numeric_cols:
        logger.warning("No numeric columns to aggregate. Returning unique link keys.")
        return pd.DataFrame({link_key: df[link_key].unique()})

    agg_dict = {col: ["min", "max", "mean", "std"] for col in numeric_cols}

    try:
        agg = df.groupby(link_key).agg(agg_dict).reset_index()
        agg.columns = [
            link_key if c[0] == link_key else f"{c[0]}_{c[1]}"
            for c in agg.columns.to_flat_index()
        ]
        logger.info(f"Aggregation successful. Shape: {agg.shape}")
        return agg
    except Exception as e:
        logger.error(f"An error occurred during aggregation: {e}")
        logger.warning("Returning unique link keys as a fallback.")
        return pd.DataFrame({link_key: df[link_key].unique()})


def _merge_on_key(frames: Iterable[pd.DataFrame], link_key: str) -> pd.DataFrame:
    return reduce(
        lambda left, right: pd.merge(left, right, on=link_key, how="outer"), frames
    )


def build_batch_matrix(
    raw_dir: str | Path,
    *,
    link_key: str = "doc_id",
    max_rows_flatten: int = 10,
    use_llm_filter: bool = True,
    config_path: str | Path | None = None,
) -> pd.DataFrame:
    """Create a *wide* batch matrix from many **Parquet** tables.

    Parameters
    ----------
    raw_dir
        Directory containing the tables produced by the *extract* step.
    link_key
        Primary/foreign-key that links all relational tables together.
    max_rows_flatten
        Threshold to decide between **row-flattening** versus **aggregation**.
    use_llm_filter
        Whether to use the LLM-based column filter.
    config_path
        Path to config file with filtering patterns. If None, uses default config.

    Returns
    -------
    pd.DataFrame
        The assembled, wide batch matrix where one row represents one batch
        (``link_key``).
    """
    raw_path = Path(raw_dir)
    if not raw_path.is_dir():  # pragma: no cover - sanity only
        raise FileNotFoundError(raw_path)

    # Load configuration for filtering patterns
    config = _load_config(config_path)

    processed: list[pd.DataFrame] = []
    for pq_file in raw_path.glob("*.parquet"):
        logger.info(f"Processing {pq_file.stem}...")

        table = pd.read_parquet(pq_file)

        if link_key not in table.columns:
            # Skip unrelated tables - common in heterogeneous DB snapshots.
            continue

        # Apply config-based filtering BEFORE other processing to reduce noise
        table = _apply_config_based_filtering(table, config, link_key)

        # Apply LLM filtering if enabled (after config filtering to reduce LLM load)
        if (
            use_llm_filter and len(table.columns) > 2
        ):  # Only if we have columns beyond link_key
            task_description = (
                "The task is to perform anomaly detection and yield prediction on manufacturing batch data. "
                "The goal is to identify batches that deviate from standard process and predict yield. "
                "Keep columns relevant for statistical analysis: process parameters, measurements, test results, "
                "material quantities, and quality control data. Remove administrative fields like names, dates, "
                "document references, and pure text descriptions."
            )
            table = filter_columns_with_llm(
                table,
                task_description,
                columns_to_keep=[link_key],
            )

        # Decide strategy based on *max* group size.
        n_max = table[link_key].value_counts().max()
        if n_max <= max_rows_flatten:
            frame = _pivot_narrow_table(table, link_key, max_rows_flatten)
        else:
            frame = _aggregate_wide_table(table, link_key)

        # Coerce any leftover object columns that *look numeric*.
        for col in frame.select_dtypes(include=["object"]).columns:
            frame[col] = clean_numeric(frame[col])  # type: ignore[arg-type]

        # ------------------------------------------------------------------
        # Ensure *unique* column names across different source tables by
        # prefixing with the Parquet file stem (except for the link key).
        # This prevents ``pandas.MergeError`` due to overlapping names.
        # ------------------------------------------------------------------
        stem = pq_file.stem.replace(" ", "_")  # hygienic
        rename_map = {c: f"{stem}__{c}" for c in frame.columns if c != link_key}
        frame = frame.rename(columns=rename_map)

        processed.append(frame)

    if not processed:
        raise ValueError(
            f"No Parquet files with column '{link_key}' found in {raw_dir}"
        )

    batch_matrix = _merge_on_key(processed, link_key)
    logger.info(f"SUCCESS: Built batch matrix: {batch_matrix.shape}")

    return batch_matrix


# -----------------------------------------------------------------------------
# Robust scaling with stochastic jitter
# -----------------------------------------------------------------------------


def robust_scale_jitter(df: pd.DataFrame, *, jitter_frac: float = 0.10) -> pd.DataFrame:
    """Median/IQR scaling with small *Gaussian* noise (jitter) per feature.

    ``scaled = (x - median) / IQR + ε`` where ``ε ~ Normal(0, (jitter_frac / IQR)^2)``.
    Non-numeric columns are passed through unchanged.
    """
    df_scaled = df.copy()

    numeric_cols = df_scaled.select_dtypes(include=[np.number]).columns.tolist()
    rng = np.random.default_rng()

    for col in numeric_cols:
        col_data = df_scaled[col].astype(float)
        # Skip columns that are entirely NaN
        if col_data.isna().all():
            continue

        median = np.nanmedian(col_data)
        q75, q25 = np.nanpercentile(col_data, [75, 25])
        iqr = max(q75 - q25, 1e-9)  # guard against zero division

        scale = (col_data - median) / iqr
        noise = rng.normal(loc=0.0, scale=jitter_frac / iqr, size=len(scale))
        df_scaled[col] = scale + noise

    return df_scaled
