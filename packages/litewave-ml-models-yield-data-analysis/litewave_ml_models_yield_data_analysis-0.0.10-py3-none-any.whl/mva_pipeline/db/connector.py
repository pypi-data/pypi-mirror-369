from __future__ import annotations

"""Database connection helper using SQLAlchemy.

This module purposefully **does not** import any dialect directly, so users are
free to choose which driver string to supply in ``config.yaml`` (e.g. psycopg2,
asyncpg, mysqlclient, pymysql, sqlite, etc.).
"""

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

_DEFAULT_ECHO = False  # set to True for verbose SQL


def get_engine(db_url: str, **kwargs: Any) -> Engine:
    """Return a SQLAlchemy Engine.

    Parameters
    ----------
    db_url: str
        A SQLAlchemy-compatible database URL.
    **kwargs: Any
        Extra kwargs forwarded to :func:`sqlalchemy.create_engine`.
    """
    params = {"echo": _DEFAULT_ECHO, **kwargs}
    engine: Engine = create_engine(db_url, **params)  # type: ignore[arg-type]
    return engine
