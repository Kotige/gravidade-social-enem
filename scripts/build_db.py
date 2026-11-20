"""Build the DuckDB database (data/enem.duckdb) from the ingestion Parquets.

Implements docs/spec-sql.md:
- the database is recreated from scratch on every run;
- SQL files run in numeric-prefix order: sql/staging, sql/analitica,
  sql/agregada (all logic lives in the .sql files);
- every file in sql/testes is a query that returns zero rows when the
  test passes; all tests run, up to 10 rows of each failure are shown,
  and the script exits with an error and a summary if any test failed.

Usage:
    python scripts/build_db.py
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.db import DB_PATH, conectar  # noqa: E402

SQL_DIR = ROOT / "sql"
LAYERS = ["staging", "analitica", "agregada"]
TESTS_DIR = SQL_DIR / "testes"
MAX_FAILURE_ROWS = 10
TRAILING_SEMICOLON = re.compile(r";(\s*--[^\n]*)*\s*$")


def reset_database() -> None:
    """Delete the database file (and its WAL) so the build starts empty."""
    for path in (DB_PATH, DB_PATH.with_name(DB_PATH.name + ".wal")):
        path.unlink(missing_ok=True)


def sql_files(directory: Path) -> list[Path]:
    return sorted(directory.glob("*.sql")) if directory.exists() else []


def run_layers(con) -> None:
    for layer in LAYERS:
        for path in sql_files(SQL_DIR / layer):
            start = time.perf_counter()
            con.execute(path.read_text(encoding="utf-8"))
            elapsed = time.perf_counter() - start
            print(f"[{layer}] {path.name} ({elapsed:.1f}s)")


def as_subquery(sql: str) -> str:
    """Wrap a test query so it can be counted and limited."""
    # Drop the final ';' and any whitespace or line comments after it.
    body = TRAILING_SEMICOLON.sub("", sql.strip())
    # Newline before ')' so a trailing line comment cannot swallow it.
    return f"(\n{body}\n)"


def run_tests(con) -> list[tuple[str, int]]:
    failures: list[tuple[str, int]] = []
    for path in sql_files(TESTS_DIR):
        query = as_subquery(path.read_text(encoding="utf-8"))
        # fetchall() consumes the result fully (DuckDB 2.0 refuses new work
        # on a connection with a partially fetched result).
        n_rows = con.execute(f"SELECT count(*) FROM {query} AS t").fetchall()[0][0]
        if n_rows == 0:
            print(f"[test] PASS {path.name}")
            continue
        print(f"[test] FAIL {path.name}: {n_rows} row(s)")
        print(con.sql(f"SELECT * FROM {query} AS t LIMIT {MAX_FAILURE_ROWS}"))
        failures.append((path.name, n_rows))
    return failures


def main() -> int:
    reset_database()
    con = conectar()
    try:
        run_layers(con)
        failures = run_tests(con)
    finally:
        con.close()

    n_tests = len(sql_files(TESTS_DIR))
    print(f"\n{n_tests - len(failures)}/{n_tests} tests passed.")
    if failures:
        print("Failed tests:")
        for name, n_rows in failures:
            print(f"  - {name}: {n_rows} row(s)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
