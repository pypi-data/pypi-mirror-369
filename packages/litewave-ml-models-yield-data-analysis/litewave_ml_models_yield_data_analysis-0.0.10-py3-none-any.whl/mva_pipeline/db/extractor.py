from __future__ import annotations

"""Generic raw table extractor that preserves original columns.

Writes one parquet file per table containing *raw* rows (no aggregation).
Only tables that possess one of the configured *link keys* (doc_id, batch_id, …)
are exported - this is crucial so we can later join on batch identifier.
"""

import os
from pathlib import Path
from typing import Dict, List, Sequence

import pandas as pd
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError

from .introspect import introspect_database
from .kubectl_connector import KubectlPostgresConnector


def _has_any_link_key(table_meta: Dict, link_keys: Sequence[str]) -> bool:
    cols = table_meta["columns"].keys()
    return any(link_key in cols for link_key in link_keys)


def export_tables_kubectl(
    link_keys: Sequence[str],
    output_dir: str = "data_raw",
    schemas_exclude: Sequence[str] = ("information_schema", "pg_catalog", "pg_toast"),
    row_limit: int | None = None,
) -> List[str]:
    """Export tables using kubectl connector."""

    connector = KubectlPostgresConnector()
    os.makedirs(output_dir, exist_ok=True)

    # Get all tables
    tables = connector.get_tables()
    saved_paths: List[str] = []

    for table_info in tables:
        schema = table_info["table_schema"]
        table_name = table_info["table_name"]

        if schemas_exclude and schema in schemas_exclude:
            continue

        # Check if table has link keys
        columns = connector.get_columns(schema, table_name)
        column_names = [col["column_name"] for col in columns]

        if not any(link_key in column_names for link_key in link_keys):
            continue

        print(f"  EXTRACTING: Extracting {schema}.{table_name}")

        # Extract data
        query = f'SELECT * FROM "{schema}"."{table_name}"'
        if row_limit:
            query += f" LIMIT {row_limit}"

        try:
            df = connector.read_sql_query(query)
            if df.empty:
                continue

            out_path = Path(output_dir) / f"{schema}.{table_name}.parquet"
            df.to_parquet(out_path, index=False)
            saved_paths.append(str(out_path))
            print(f"    SUCCESS: Saved {len(df)} rows to {out_path}")

        except Exception as e:
            print(f"    ERROR: Error extracting {schema}.{table_name}: {e}")
            continue

    return saved_paths


def export_tables(
    engine: Engine,
    link_keys: Sequence[str],
    output_dir: str = "data_raw",
    schemas_include: Sequence[str] | None = None,
    schemas_exclude: Sequence[str]
    | None = (
        "information_schema",
        "pg_catalog",
        "pg_toast",
    ),
    row_limit: int | None = None,
) -> List[str]:
    """Export every relevant table to Parquet and return list of file paths."""

    try:
        # Try SQLAlchemy first
        meta = introspect_database(engine)
        tables_meta = meta["tables"]
        os.makedirs(output_dir, exist_ok=True)

        saved_paths: List[str] = []
        for fq_name, tmeta in tables_meta.items():
            schema = tmeta["schema"]
            if schemas_include and schema not in schemas_include:
                continue
            if schemas_exclude and schema in schemas_exclude:
                continue
            if not _has_any_link_key(tmeta, link_keys):
                continue

            query = f'SELECT * FROM "{schema}"."{tmeta["table"]}"'
            if row_limit:
                query += f" LIMIT {row_limit}"
            df = pd.read_sql_query(query, engine)
            if df.empty:
                continue
            # Store parquet file named schema.table.parquet
            out_path = Path(output_dir) / f"{schema}.{tmeta['table']}.parquet"
            df.to_parquet(out_path, index=False)
            saved_paths.append(str(out_path))
        return saved_paths

    except OperationalError as e:
        if "could not translate host name" in str(
            e
        ) or "Name or service not known" in str(e):
            print("FALLBACK: SQLAlchemy connection failed, falling back to kubectl...")
            return export_tables_kubectl(
                link_keys=link_keys,
                output_dir=output_dir,
                schemas_exclude=schemas_exclude or (),
                row_limit=row_limit,
            )
        else:
            raise
