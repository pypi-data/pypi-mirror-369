from __future__ import annotations

"""Database schema introspection utilities.

All functionality relies solely on SQLAlchemy's reflection / Inspector so it
works across most SQL backends (Postgres, MySQL, SQLite, etc.).
"""

import hashlib
import json
from typing import Dict, Optional

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from ..redis_manager import get_redis_manager, is_redis_enabled


def _get_db_id(engine: Engine) -> str:
    """Generate a stable identifier for the target database from the URL (password hidden)."""
    # URL.render_as_string is stable and hides password when requested
    url_string = engine.url.render_as_string(hide_password=True)
    return hashlib.sha1(url_string.encode("utf-8")).hexdigest()


def _compute_schema_fingerprint(engine: Engine) -> Optional[str]:
    """Compute a lightweight fingerprint of the current DB schema.

    - For PostgreSQL, uses information_schema to compute a stable hash across
      columns, PKs, and FKs for all non-system schemas.
    - For other dialects, returns None (cache will be bypassed).
    """
    dialect_name = engine.dialect.name if engine and engine.dialect else ""

    if dialect_name != "postgresql":
        return None

    try:
        hasher = hashlib.sha1()
        with engine.connect() as conn:
            # Columns
            cols_query = """
            SELECT table_schema, table_name, column_name, data_type, is_nullable,
                   character_maximum_length, numeric_precision, numeric_scale, ordinal_position
            FROM information_schema.columns
            WHERE table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
            ORDER BY table_schema, table_name, ordinal_position
            """
            for row in conn.execute(text(cols_query)):
                (
                    table_schema,
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    char_max,
                    num_prec,
                    num_scale,
                    _ordinal_position,
                ) = row
                hasher.update(
                    f"C|{table_schema}.{table_name}.{column_name}|{data_type}|{is_nullable}|{char_max}|{num_prec}|{num_scale}".encode(
                        "utf-8"
                    )
                )

            # Primary Keys
            pk_query = """
            SELECT tc.table_schema, tc.table_name, kcu.column_name, kcu.ordinal_position
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
             AND tc.table_name = kcu.table_name
            WHERE tc.constraint_type = 'PRIMARY KEY'
              AND tc.table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
            ORDER BY tc.table_schema, tc.table_name, kcu.ordinal_position
            """
            for row in conn.execute(text(pk_query)):
                table_schema, table_name, column_name, ordinal_position = row
                hasher.update(
                    f"P|{table_schema}.{table_name}|{column_name}|{ordinal_position}".encode(
                        "utf-8"
                    )
                )

            # Foreign Keys
            fk_query = """
            SELECT tc.table_schema, tc.table_name, kcu.column_name,
                   ccu.table_schema AS referenced_table_schema,
                   ccu.table_name AS referenced_table_name,
                   ccu.column_name AS referenced_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_schema = kcu.table_schema
            JOIN information_schema.referential_constraints AS rc
              ON tc.constraint_name = rc.constraint_name
             AND tc.table_schema = rc.constraint_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = rc.unique_constraint_name
             AND ccu.constraint_schema = rc.unique_constraint_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema NOT IN ('information_schema','pg_catalog','pg_toast')
            ORDER BY tc.table_schema, tc.table_name, kcu.ordinal_position
            """
            for row in conn.execute(text(fk_query)):
                (
                    table_schema,
                    table_name,
                    column_name,
                    ref_schema,
                    ref_table,
                    ref_column,
                ) = row
                hasher.update(
                    f"F|{table_schema}.{table_name}.{column_name}->{ref_schema}.{ref_table}.{ref_column}".encode(
                        "utf-8"
                    )
                )

        return hasher.hexdigest()
    except Exception:
        return None


def _read_cache_from_redis(engine: Engine, live_fingerprint: str) -> Optional[Dict]:
    """Return cached schema metadata if fingerprint matches live fingerprint."""
    try:
        if not is_redis_enabled():
            return None
        manager = get_redis_manager()
        db_id = _get_db_id(engine)
        key = f"{manager.key_prefix}:schema_cache:{db_id}"
        data_str, fp_str = manager.redis_client.hmget(key, "data", "fingerprint")
        if not data_str or not fp_str:
            return None
        if fp_str != live_fingerprint:
            return None
        return json.loads(data_str)
    except Exception:
        return None


def _write_cache_to_redis(engine: Engine, live_fingerprint: str, meta: Dict) -> None:
    """Persist schema metadata and its fingerprint to Redis."""
    try:
        if not is_redis_enabled():
            return
        manager = get_redis_manager()
        db_id = _get_db_id(engine)
        key = f"{manager.key_prefix}:schema_cache:{db_id}"
        manager.redis_client.hset(
            key,
            mapping={
                "data": json.dumps(meta, default=str),
                "fingerprint": live_fingerprint,
            },
        )
    except Exception:
        pass


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

    live_fingerprint: Optional[str] = None
    if is_redis_enabled():
        live_fingerprint = _compute_schema_fingerprint(engine)

    if use_cache and live_fingerprint:
        cached = _read_cache_from_redis(engine, live_fingerprint)
        if cached is not None:
            return cached

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

    if live_fingerprint:
        _write_cache_to_redis(engine, live_fingerprint, metadata)

    return metadata
