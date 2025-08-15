from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd
import yaml

from .db.connector import get_engine
from .db.extractor import export_tables

_DEF_CONFIG = Path(__file__).with_name("config.yaml")


def load_config(config_path: str | Path | None):
    """Load YAML config and return as dict (fallback to default)."""
    path = Path(config_path or _DEF_CONFIG)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg


def cmd_extract(args):
    """Extract raw tables that contain the configured link keys."""
    cfg = load_config(args.config)
    engine = get_engine(cfg["db_url"])

    output_dir = Path(cfg.get("output_dir", "outputs")) / "data_raw"
    output_dir.mkdir(parents=True, exist_ok=True)

    files = export_tables(
        engine,
        cfg.get("link_keys", ["doc_id"]),
        output_dir=str(output_dir),
    )
    print(f"SUCCESS: Extracted {len(files)} tables to {output_dir}")


def cmd_build(args):
    """Build wide batch matrix from raw tables and apply robust-scaling jitter."""
    cfg = load_config(getattr(args, "config", None))

    from .builder import build_batch_matrix, robust_scale_jitter
    from .redis_manager import get_redis_manager, is_redis_enabled

    raw_dir = Path(cfg.get("output_dir", "outputs")) / "data_raw"
    link_key = cfg.get("link_keys", ["doc_id"])[0]

    batch = build_batch_matrix(
        raw_dir,
        link_key=link_key,
        use_llm_filter=args.use_llm_filter,
        config_path=args.config,
    )

    out_dir = Path(cfg.get("output_dir", "outputs"))
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save the unscaled batch matrix
    batch.to_parquet(out_dir / "batch_matrix.parquet", index=False)
    print(
        f"SUCCESS: Built batch-matrix ({batch.shape[0]}×{batch.shape[1]}) to {out_dir}/batch_matrix.parquet"
    )

    # Create and save scaled version
    batch_scaled = robust_scale_jitter(batch)
    batch_scaled.to_parquet(out_dir / "batch_matrix_scaled.parquet", index=False)
    print(f"SUCCESS: Scaled batch-matrix to {out_dir}/batch_matrix_scaled.parquet")

    # Store in Redis (for production use by agents)
    if is_redis_enabled():
        try:
            redis_manager = get_redis_manager()
            redis_manager.store_dataframe("batch_matrix", batch)
            print("SUCCESS: Stored batch matrix in Redis")
        except Exception as e:
            print(f"WARNING: Failed to store batch matrix in Redis: {e}")
    else:
        print("INFO: Redis storage disabled, skipping Redis storage for batch matrix")


def cmd_analyze(args):
    """Run complete analytics pipeline end-to-end."""
    cfg = load_config(getattr(args, "config", None))

    from .analysis import anomaly, pca_yield, root_cause
    from .analysis.unified_importance import compute_unified_importance
    from .synth import augment

    # Load batch matrix
    out_dir = Path(cfg.get("output_dir", "outputs"))
    batch_file = out_dir / "batch_matrix.parquet"

    if not batch_file.exists():
        raise FileNotFoundError(f"Run 'build' first to create {batch_file}")

    df = pd.read_parquet(batch_file)

    # Find available yield columns dynamically
    all_yield_cols = [col for col in df.columns if "yield" in col.lower()]
    print(f"SEARCH: Found yield columns: {all_yield_cols}")

    # Create a unified yield column from available yield data
    yield_col = "yield"

    # Try to find actual yield data from either report source
    potential_yield_cols = [
        col for col in all_yield_cols if "actual_yield" in col.lower()
    ]

    if not potential_yield_cols:
        # Fallback: look for any numeric yield column
        potential_yield_cols = []
        for col in all_yield_cols:
            if df[col].notna().sum() > 0:  # Has some data
                try:
                    # Check if it's numeric
                    pd.to_numeric(df[col].dropna().iloc[0])
                    potential_yield_cols.append(col)
                except:
                    continue

    if not potential_yield_cols:
        raise ValueError(
            f"No usable yield columns found. Available columns with 'yield': {all_yield_cols}"
        )

    print(f"DATA: Using yield columns: {potential_yield_cols}")

    # Combine yields from available sources, prioritizing non-null values
    df[yield_col] = None
    for col in potential_yield_cols:
        df[yield_col] = df[yield_col].fillna(df[col])

    # CRITICAL: Remove original yield columns to prevent data leakage
    yield_cols_to_remove = [
        col for col in df.columns if "yield" in col.lower() and col != yield_col
    ]
    df = df.drop(columns=yield_cols_to_remove)
    print(
        f"CLEANUP: Removed {len(yield_cols_to_remove)} yield-related columns to prevent data leakage: {yield_cols_to_remove[:3]}{'...' if len(yield_cols_to_remove) > 3 else ''}"
    )

    print(f"DATA: Loaded batch-matrix: {df.shape}")
    print(
        f"INFO: Yield column '{yield_col}' has {df[yield_col].notna().sum()}/{len(df)} valid values"
    )
    print(f"   Yield range: {df[yield_col].min():.1f} to {df[yield_col].max():.1f}")

    # Synthetic augmentation (upsample to ~500 rows and inject ~2% anomalies)
    n_need = max(0, 500 - len(df))
    df_aug = augment(df, n=n_need, sigma=5, anomaly_frac=0.02)

    # Run analytics
    print("ANALYSIS: Detecting anomalies...")
    anomaly_result = anomaly.detect(df_aug)

    print("ANALYSIS: Running supervised PCA...")
    pca_result = pca_yield.supervised_pca(df_aug, target_col=yield_col)

    print("ANALYSIS: Root-cause analysis...")
    rca_result = root_cause.run(df_aug, target_col=yield_col, k_features=20)

    # Compute unified importance
    print("ANALYSIS: Computing unified feature importance...")
    unified_result = compute_unified_importance(pca_result, rca_result, top_k=15)

    # Count actual anomalies
    n_anomalies = anomaly_result["anomaly"].sum() if "anomaly" in anomaly_result else 0

    # Summary
    print("SUCCESS: Analytics complete! Check outputs/ for results.")
    print(f"   RESULTS: Anomaly results: {n_anomalies} batches flagged as anomalous")
    print(
        f"   RESULTS: PCA: {pca_result.get('n_components', 0)} components explaining {pca_result.get('variance_explained', 0)*100:.1f}%"
    )
    print(
        f"   RESULTS: Root-cause: {rca_result.get('n_features', len(rca_result.get('feature_importance', [])))} features analyzed"
    )
    print(f"   RESULTS: Unified: Top {len(unified_result)} yield drivers identified")


def cmd_pipeline(args):
    """Run complete pipeline with intelligent caching."""
    from .pipeline import run_pipeline

    level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    result = run_pipeline(
        raw_dir=args.raw_dir,
        config_path=args.config,
        force_rebuild=args.force,
        skip_extraction=args.skip_extraction,
    )

    print(
        f"Pipeline completed: updated={result['updated']}, cache_hit={result.get('cache_hit', False)}"
    )
    print(f"Runtime: {result['runtime_seconds']:.1f}s")

    if "error" in result:
        print(f"Error: {result['error']}")
        return 1

    print(f"Fingerprint: {result['fingerprint'][:16]}...")

    if "artifacts" in result:
        print("Artifacts:")
        for name, path in result["artifacts"].items():
            print(f"  {name}: {path}")

    if "analytics_summary" in result:
        summary = result["analytics_summary"]
        if "anomaly" in summary:
            print(f"Analytics: {summary['anomaly']['n_anomalies']} anomalies detected")
        if "pca" in summary:
            print(f"Analytics: PCA with {summary['pca']['n_components']} components")
        if "rca" in summary:
            print(f"Analytics: RCA analyzed {summary['rca']['n_features']} features")

    return 0


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="MVA Data-Extraction CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_ext = sub.add_parser("extract", help="Extract raw tables to parquet")
    p_ext.add_argument("--config", help="Path to config.yaml")
    p_ext.set_defaults(func=cmd_extract)

    # NEW: build command
    p_build = sub.add_parser("build", help="Build wide batch matrix + robust scaling")
    p_build.add_argument("--config", help="Path to config.yaml")
    p_build.add_argument(
        "--no-llm-filter",
        action="store_false",
        dest="use_llm_filter",
        help="Disable the LLM-based column filter.",
    )
    p_build.set_defaults(func=cmd_build, use_llm_filter=True)

    # NEW: analyze command
    p_ana = sub.add_parser("analyze", help="Run analytics layer end-to-end")
    p_ana.add_argument("--config", help="Path to config.yaml")
    p_ana.set_defaults(func=cmd_analyze)

    # NEW: pipeline command with caching
    p_pipeline = sub.add_parser(
        "pipeline", help="Run complete pipeline with intelligent caching"
    )
    p_pipeline.add_argument("--raw-dir", type=Path, help="Raw data directory")
    p_pipeline.add_argument("--config", help="Path to config.yaml")
    p_pipeline.add_argument(
        "--force", action="store_true", help="Force rebuild ignoring cache"
    )
    p_pipeline.add_argument(
        "--skip-extraction", action="store_true", help="Skip database extraction"
    )
    p_pipeline.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose logging"
    )
    p_pipeline.set_defaults(func=cmd_pipeline)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
