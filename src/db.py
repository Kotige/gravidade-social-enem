"""Connection helper for the project DuckDB database (data/enem.duckdb).

Staging views read Parquet files through paths relative to the project
root (data/parquet/...). DuckDB resolves relative paths against
file_search_path, which is a session setting, so every connection must
be opened through conectar() for the views to work from any directory.

Setup (once, inside the virtual environment, from the project root):
    pip install -e .

Usage (from notebooks, scripts or any directory):
    from src.db import conectar
    con = conectar(read_only=True)
"""

from __future__ import annotations

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "enem.duckdb"
TEMP_DIR = ROOT / "data" / ".duckdb_tmp"
MEMORY_LIMIT = "3GB"


def _quote(value: str) -> str:
    """Quote a string literal for a DuckDB SET statement."""
    return "'" + value.replace("'", "''") + "'"


def conectar(read_only: bool = False) -> duckdb.DuckDBPyConnection:
    """Open data/enem.duckdb with the project root as file_search_path."""
    con = duckdb.connect(str(DB_PATH), read_only=read_only)
    con.execute(f"SET file_search_path = {_quote(str(ROOT))}")
    con.execute(f"SET memory_limit = {_quote(MEMORY_LIMIT)}")
    con.execute(f"SET temp_directory = {_quote(str(TEMP_DIR))}")
    return con
