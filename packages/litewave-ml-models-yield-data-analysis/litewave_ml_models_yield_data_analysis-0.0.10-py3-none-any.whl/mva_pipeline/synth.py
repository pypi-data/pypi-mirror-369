from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

# -----------------------------------------------------------------------------
# Synthetic data augmentation with robust handling of sparse/missing data
# -----------------------------------------------------------------------------


_DEF_OUTPUT = Path("outputs")


def augment(
    df: pd.DataFrame,
    *,
    target: str = "yield",
    n: int = 1_000,
    sigma: float | int = 10,
    anomaly_frac: float | int = 0.02,
) -> pd.DataFrame:
    """Return *df* concatenated with **synthetic** rows, including anomalies.

    Parameters
    ----------
    df
        Original batch data (wide format)
    target
        Target column name for yield prediction
    n
        Number of synthetic rows to generate
    sigma
        Noise level for synthetic target values
    anomaly_frac
        Fraction of synthetic rows to make anomalous (0-1)

    Returns
    -------
    pd.DataFrame
        Original data + synthetic data with a 'sample_weight' column
    """
    if n <= 0:
        return df

    if target not in df.columns:
        raise KeyError(f"'{target}' column not found in input frame")

    rng = np.random.default_rng(42)  # Fixed seed for reproducibility

    # Separate target from features
    y_orig = df[target].copy()
    X_orig = df.drop(columns=[target])

    # Get numeric features only
    numeric_cols = X_orig.select_dtypes(include=[np.number]).columns.tolist()
    X_numeric = X_orig[numeric_cols].copy()

    # Remove constant columns
    X_numeric = X_numeric.loc[:, X_numeric.var() > 1e-8]

    if X_numeric.empty or len(X_numeric.columns) < 5:
        print(
            "WARNING: Insufficient numeric features for synthetic augmentation - returning original data"
        )
        df_out = df.copy()
        df_out["sample_weight"] = 3.0  # High weight for real samples
        return df_out

    # Impute missing values with median
    imputer = SimpleImputer(strategy="median")
    X_imputed = pd.DataFrame(
        imputer.fit_transform(X_numeric),
        columns=X_numeric.columns,
        index=X_numeric.index,
    )

    # Handle missing y values
    valid_mask = ~y_orig.isna()
    if valid_mask.sum() < 5:
        print(
            "WARNING: Insufficient valid target values for synthetic augmentation - returning original data"
        )
        df_out = df.copy()
        df_out["sample_weight"] = 3.0
        return df_out

    X_train = X_imputed[valid_mask]
    y_train = y_orig[valid_mask]

    # Standardize for better numerical stability
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)

    # Generate synthetic features
    print(f"GENERATING: Generating {n} synthetic samples...")

    # Use feature-wise sampling with correlation structure
    means = X_scaled.mean(axis=0)
    stds = X_scaled.std(axis=0)

    # Add some correlation by using a simple factor model
    n_factors = min(10, X_scaled.shape[1] // 5)
    factor_loadings = rng.normal(0, 1, (X_scaled.shape[1], n_factors))
    factors = rng.normal(0, 1, (n, n_factors))

    # Generate base synthetic features
    X_synth_scaled = factors @ factor_loadings.T

    # Add independent noise (reduced from 0.5 to 0.3 for more realistic data)
    X_synth_scaled += rng.normal(0, 0.3, X_synth_scaled.shape)

    # Match original distribution statistics
    for i in range(X_scaled.shape[1]):
        if stds[i] > 0:  # Avoid division by zero
            X_synth_scaled[:, i] = (
                X_synth_scaled[:, i] - X_synth_scaled[:, i].mean()
            ) / X_synth_scaled[:, i].std()
            X_synth_scaled[:, i] = X_synth_scaled[:, i] * stds[i] + means[i]

    # Transform back to original scale
    X_synth = scaler.inverse_transform(X_synth_scaled)
    X_synth_df = pd.DataFrame(X_synth, columns=X_train.columns)

    # Predict yield using Ridge regression
    ridge = Ridge(alpha=10.0, random_state=42)  # Increased regularization
    ridge.fit(X_scaled, y_train)
    y_synth_base = ridge.predict(X_synth_scaled)

    # Add realistic noise to predictions (reduced from sigma to sigma/2)
    y_synth = y_synth_base + rng.normal(0, sigma / 2, len(y_synth_base))

    # Ensure synthetic yields are in reasonable range
    y_min, y_max = y_train.min(), y_train.max()
    y_range = y_max - y_min
    y_synth = np.clip(y_synth, y_min - 0.1 * y_range, y_max + 0.1 * y_range)

    # Inject anomalies
    n_anomalies = int(n * anomaly_frac)
    if n_anomalies > 0:
        anomaly_idx = rng.choice(n, n_anomalies, replace=False)

        # Find pH and temperature columns based on pharmaceutical naming patterns
        ph_cols = [
            col
            for col in X_synth_df.columns
            if "bprpoc_ph" in col.lower()
            or "ph_records" in col.lower()
            or (("ph" in col.lower() and "value" in col.lower()))
        ]
        temp_cols = [
            col
            for col in X_synth_df.columns
            if "temp_records" in col.lower() or "temperature" in col.lower()
        ]

        print(
            f"ANOMALIES: Found {len(ph_cols)} pH columns and {len(temp_cols)} temperature columns for anomaly injection"
        )

        # Apply pH and temperature anomalies to decrease yield
        for i in anomaly_idx:
            # Increase pH values (customer says this decreases yield)
            for ph_col in ph_cols:
                if ph_col in X_synth_df.columns:
                    ph_col_idx = X_synth_df.columns.get_loc(ph_col)
                    # Increase pH significantly above normal range
                    current_ph = X_synth[i, ph_col_idx]
                    ph_increase = rng.uniform(2.0, 4.0)  # Increase pH by 2-4 units
                    X_synth[i, ph_col_idx] = current_ph + ph_increase

            # Decrease temperature values (customer says this decreases yield)
            for temp_col in temp_cols:
                if temp_col in X_synth_df.columns:
                    temp_col_idx = X_synth_df.columns.get_loc(temp_col)
                    # Decrease temperature significantly below normal range
                    current_temp = X_synth[i, temp_col_idx]
                    temp_decrease = rng.uniform(
                        10.0, 30.0
                    )  # Decrease temperature by 10-30 degrees
                    X_synth[i, temp_col_idx] = current_temp - temp_decrease

            # Set yield to be significantly lower for these anomalous conditions
            y_synth[i] = y_min - rng.uniform(2.0, 5.0) * y_train.std()

    # Create synthetic dataframe
    df_synth = pd.DataFrame(X_synth_df)
    df_synth[target] = y_synth

    # Generate synthetic doc_ids starting after the max real doc_id
    if "doc_id" in df.columns:
        max_doc_id = df["doc_id"].max()
        df_synth["doc_id"] = range(int(max_doc_id) + 1, int(max_doc_id) + n + 1)

    # Restore non-numeric columns with mode
    for col in X_orig.columns:
        if col not in numeric_cols and col != "doc_id":
            if not df[col].empty:
                mode_val = (
                    df[col].mode()[0] if len(df[col].mode()) > 0 else df[col].iloc[0]
                )
                df_synth[col] = mode_val

    # Add sample type and weights
    df_orig = df.copy()
    df_orig["sample_type"] = "Real"
    df_orig["sample_weight"] = 3.0

    df_synth["sample_type"] = "Synthetic"
    df_synth["sample_weight"] = 1.0

    if n_anomalies > 0:
        # Get the indices in df_synth that correspond to the anomaly_idx
        synth_anomaly_indices = df_synth.index[anomaly_idx]
        df_synth.loc[synth_anomaly_indices, "sample_type"] = "Synthetic Anomaly"

    # Combine and shuffle
    df_combined = pd.concat([df_orig, df_synth], ignore_index=True)
    df_combined = df_combined.sample(frac=1, random_state=42).reset_index(drop=True)

    print(
        f"SUCCESS: Augmentation complete: {len(df)} real + {len(df_synth)} synthetic = {len(df_combined)} total samples"
    )
    print(
        f"   Including {n_anomalies} anomalies ({anomaly_frac*100:.1f}% of synthetic data)"
    )

    return df_combined
