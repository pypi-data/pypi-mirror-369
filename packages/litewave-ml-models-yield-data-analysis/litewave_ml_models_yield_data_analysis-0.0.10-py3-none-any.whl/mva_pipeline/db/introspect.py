from __future__ import annotations

"""Database schema introspection utilities.

All functionality relies solely on SQLAlchemy's reflection / Inspector so it
works across most SQL backends (Postgres, MySQL, SQLite, etc.).
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy import inspect
from sqlalchemy.engine import Engine

_SCHEMA_CACHE_FILE = "schema_cache.json"


def _write_cache(meta: Dict) -> None:
    Path(_SCHEMA_CACHE_FILE).write_text(json.dumps(meta, indent=2))


def _read_cache() -> Optional[Dict]:
    path = Path(_SCHEMA_CACHE_FILE)
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return None
    return None


def introspect_database(engine: Engine, use_cache: bool = True) -> Dict:
    """Return lightweight description of all tables / columns / PK / FK.

    The output dictionary structure::

        {
            "tables": {
                "schema.table": {
                    "schema": "public",
                    "table": "temperature_log",
                    "columns": {
                        "col_name": {"type": "INTEGER", "nullable": False}
                    },
                    "pk": ["id"],
                    "fks": {"doc_id": "public.doc(doc_id)"}
                }
            }
        }
    """

    if use_cache:
        cache = _read_cache()
        if cache:
            return cache

    inspector = inspect(engine)
    metadata: Dict[str, Dict] = {"tables": {}}

    for schema in inspector.get_schema_names():
        if schema in {"information_schema", "pg_catalog", "pg_toast"}:
            continue
        for table_name in inspector.get_table_names(schema=schema):
            fq_name = f"{schema}.{table_name}"
            columns_info = {}
            for col in inspector.get_columns(table_name, schema=schema):
                columns_info[col["name"]] = {
                    "type": str(col["type"]),
                    "nullable": col.get("nullable", True),
                }
            pk_cols = inspector.get_pk_constraint(table_name, schema=schema).get(
                "constrained_columns", []
            )
            fk_map = {}
            for fk in inspector.get_foreign_keys(table_name, schema=schema):
                if not fk.get("constrained_columns"):
                    continue
                fk_map[fk["constrained_columns"][0]] = fk["referred_table"]
            metadata["tables"][fq_name] = {
                "schema": schema,
                "table": table_name,
                "columns": columns_info,
                "pk": pk_cols,
                "fks": fk_map,
            }
    _write_cache(metadata)
    return metadata
