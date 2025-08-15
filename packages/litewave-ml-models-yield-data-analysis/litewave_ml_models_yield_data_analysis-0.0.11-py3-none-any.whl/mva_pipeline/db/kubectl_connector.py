from __future__ import annotations

"""Kubectl-based database connector for Kubernetes environments.

When the database is only accessible from within the cluster, we use kubectl exec
to run SQL commands directly in the postgres pod.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List

import pandas as pd


class KubectlPostgresConnector:
    """Database connector using kubectl exec for Postgres operations."""

    def __init__(self, pod_name: str = "postgres", namespace: str = "default"):
        self.pod_name = pod_name
        self.namespace = namespace
        self.base_cmd = [
            "kubectl",
            "exec",
            self.pod_name,
            "--",
            "env",
            "PGPASSWORD=Password!234",
            "psql",
            "-U",
            "postgres",
            "-h",
            "postgresql.postgres",
            "document_ai",
        ]

    def execute_query(self, query: str) -> str:
        """Execute SQL query and return output as string."""
        cmd = self.base_cmd + ["-c", query]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"SQL query failed: {result.stderr}")
        return result.stdout

    def read_sql_query(self, query: str) -> pd.DataFrame:
        """Execute query and return as pandas DataFrame."""
        # First get column names
        col_cmd = self.base_cmd + [
            "-t",
            "-c",
            f"SELECT * FROM ({query.rstrip(';')}) AS subq LIMIT 0;",
        ]
        col_result = subprocess.run(col_cmd, capture_output=True, text=True)

        # Get actual data with CSV format
        cmd = self.base_cmd + ["--csv", "-c", query.rstrip(";")]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"SQL query failed: {result.stderr}")

        if not result.stdout.strip():
            return pd.DataFrame()

        # Parse CSV directly from stdout
        from io import StringIO

        return pd.read_csv(StringIO(result.stdout))

    def get_tables(self) -> List[Dict[str, str]]:
        """Get list of all user tables."""
        query = """SELECT table_schema, table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns 
                    WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
                   FROM information_schema.tables t
                   WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                       AND table_type = 'BASE TABLE'
                   ORDER BY table_schema, table_name"""

        df = self.read_sql_query(query)
        return df.to_dict("records")

    def get_columns(self, schema: str, table: str) -> List[Dict[str, str]]:
        """Get columns for a specific table."""
        query = f"""SELECT column_name, data_type, is_nullable
                   FROM information_schema.columns
                   WHERE table_schema = '{schema}' AND table_name = '{table}'
                   ORDER BY ordinal_position"""

        df = self.read_sql_query(query)
        return df.to_dict("records")
