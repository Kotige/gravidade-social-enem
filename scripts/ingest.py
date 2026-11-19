"""Ingest raw ENEM microdata (2020-2025) into Parquet.

Implements docs/spec-ingestao.md:
- columns and names come from docs/harmonizacao.csv and the item
  harmonization file (rows with usar = sim);
- rows are filtered to Minas Gerais (items: only CN);
- output is zstd Parquet partitioned by ano, one partition per year;
- validations are written to docs/ingestao_log.csv and
  docs/ingestao_nulos.csv.

Usage:
    python scripts/ingest.py               # all years
    python scripts/ingest.py --anos 2023   # selected years
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

import duckdb
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

CONFIG = {
    "raw_dir": ROOT / "data" / "raw",
    "parquet_dir": ROOT / "data" / "parquet",
    "harmonization": ROOT / "docs" / "harmonizacao.csv",
    "harmonization_items": ROOT / "docs" / "harmonizacao_itens.csv",
    "log_file": ROOT / "docs" / "ingestao_log.csv",
    "nulls_file": ROOT / "docs" / "ingestao_nulos.csv",
    "duckdb_temp_dir": ROOT / "data" / ".duckdb_tmp",
    "memory_limit": "3GB",
    "csv_delimiter": ";",
    # Encoding per year (confirmed: all latin-1).
    "encoding": {year: "latin-1" for year in range(2020, 2026)},
    # Input files per year and output table. Paths relative to raw_dir.
    "inputs": {
        **{
            year: {
                "base_unica": f"{year}/DADOS/MICRODADOS_ENEM_{year}.csv",
                "itens": f"{year}/DADOS/ITENS_PROVA_{year}.csv",
            }
            for year in range(2020, 2024)
        },
        **{
            year: {
                "participantes": f"{year}/DADOS/PARTICIPANTES_{year}.csv",
                "resultados": f"{year}/DADOS/RESULTADOS_{year}.csv",
                "itens": f"{year}/DADOS/ITENS_PROVA_{year}.csv",
            }
            for year in range(2024, 2026)
        },
    },
}

# Row filters per table, written on the original INEP column names.
ROW_FILTERS = {
    "base_unica": "SG_UF_PROVA = 'MG' OR SG_UF_ESC = 'MG'",
    "resultados": "SG_UF_PROVA = 'MG' OR SG_UF_ESC = 'MG'",
    "participantes": "SG_UF_PROVA = 'MG'",
    "itens": "SG_AREA = 'CN'",
}

# Identifier (possibly composite) that must be unique per table (validation 4).
UNIQUE_KEYS = {
    "base_unica": ["numero_inscricao"],
    "participantes": ["numero_inscricao"],
    "resultados": ["numero_sequencial"],
    "itens": ["codigo_prova", "posicao_item"],
}

DOUBLE_PREFIXES = ("nota_", "param_")
SOURCE_FILE_COLUMN = "fonte_arquivo"
SCORE_MIN, SCORE_MAX = 0, 1000


# ---------------------------------------------------------------------------
# Harmonization
# ---------------------------------------------------------------------------


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def read_harmonization_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        fail(f"harmonization file not found: {path}")
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    df = df.apply(lambda col: col.str.strip())
    return df[df["usar"] == "sim"]


def column_mapping(year: int, table: str) -> list[tuple[str, str | None]]:
    """Return (concept, inep_column) pairs for a year and table.

    inep_column is None for `ano` in the items table, which is filled
    from the year being processed.
    """
    if table == "itens":
        df = read_harmonization_csv(CONFIG["harmonization_items"])
        pairs = list(zip(df["conceito"], df["coluna_inep"]))
        return [("ano", None)] + pairs

    df = read_harmonization_csv(CONFIG["harmonization"])
    year_col = str(year)
    pairs = []
    for _, row in df.iterrows():
        inep = row[year_col]
        if not inep:
            continue  # concept does not exist this year
        if year >= 2024:
            target = row["tabela_2024_2025"]
            if target not in ("participantes", "resultados", "ambas"):
                fail(
                    f"concept '{row['conceito']}' has column '{inep}' in {year} "
                    f"but invalid tabela_2024_2025 = '{target}' in harmonization"
                )
            if target not in (table, "ambas"):
                continue
        pairs.append((row["conceito"], inep))
    return pairs


def output_type(concept: str) -> str:
    if concept == "ano":
        return "SMALLINT"
    if concept.startswith(DOUBLE_PREFIXES):
        return "DOUBLE"
    return "VARCHAR"


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------


def sql_str(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def csv_source(path: Path, year: int) -> str:
    return (
        f"read_csv({sql_str(str(path))}, delim={sql_str(CONFIG['csv_delimiter'])}, "
        f"header=true, all_varchar=true, encoding={sql_str(CONFIG['encoding'][year])})"
    )


def ingest_table(con: duckdb.DuckDBPyConnection, year: int, table: str) -> dict:
    csv_path = CONFIG["raw_dir"] / CONFIG["inputs"][year][table]
    if not csv_path.exists():
        fail(f"input file not found: {csv_path}")
    source = csv_source(csv_path, year)
    file_name = csv_path.name

    # Validation 1: every expected column exists in the source CSV.
    mapping = column_mapping(year, table)
    available = {r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {source}").fetchall()}
    for concept, inep in mapping:
        if inep is not None and inep not in available:
            fail(
                f"year {year}, file {file_name}: concept '{concept}' expects column "
                f"'{inep}', which is missing. Fix the harmonization before continuing."
            )
    row_filter = ROW_FILTERS[table]

    select_items = []
    for concept, inep in mapping:
        expr = str(year) if inep is None else quote_ident(inep)
        select_items.append(f"CAST({expr} AS {output_type(concept)}) AS {quote_ident(concept)}")
    select_items.append(f"{sql_str(file_name)} AS {SOURCE_FILE_COLUMN}")

    print(f"[{year}/{table}] counting rows in {file_name} ...", flush=True)
    rows_read = con.execute(f"SELECT count(*) FROM {source}").fetchone()[0]

    # Overwrite only this year's partition.
    table_dir = CONFIG["parquet_dir"] / table
    partition_dir = table_dir / f"ano={year}"
    if partition_dir.exists():
        shutil.rmtree(partition_dir)
    table_dir.mkdir(parents=True, exist_ok=True)

    print(f"[{year}/{table}] writing Parquet ...", flush=True)
    con.execute(
        f"""
        COPY (
            SELECT {", ".join(select_items)}
            FROM {source}
            WHERE {row_filter}
        ) TO {sql_str(str(table_dir))} (
            FORMAT parquet,
            COMPRESSION zstd,
            PARTITION_BY (ano),
            WRITE_PARTITION_COLUMNS true,
            OVERWRITE_OR_IGNORE true
        )
        """
    )

    return validate(con, year, table, file_name, rows_read, partition_dir)


# ---------------------------------------------------------------------------
# Validations
# ---------------------------------------------------------------------------


def validate(
    con: duckdb.DuckDBPyConnection,
    year: int,
    table: str,
    file_name: str,
    rows_read: int,
    partition_dir: Path,
) -> dict:
    parquet = f"read_parquet({sql_str(str(partition_dir / '*.parquet'))})"
    columns = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {parquet}").fetchall()]
    rows_written = con.execute(f"SELECT count(*) FROM {parquet}").fetchone()[0]

    # Validation 3: scores within [0, 1000] or NULL.
    score_cols = [c for c in columns if c.startswith("nota_")]
    scores_out = 0
    for col in score_cols:
        q = quote_ident(col)
        n = con.execute(
            f"SELECT count(*) FROM {parquet} "
            f"WHERE {q} IS NOT NULL AND ({q} < {SCORE_MIN} OR {q} > {SCORE_MAX})"
        ).fetchone()[0]
        if n:
            print(f"WARNING [{year}/{table}]: {n} values of {col} outside "
                  f"[{SCORE_MIN}, {SCORE_MAX}]")
        scores_out += n

    # Validation 4: unique identifier.
    key = ", ".join(quote_ident(c) for c in UNIQUE_KEYS[table])
    duplicates = con.execute(
        f"SELECT coalesce(sum(n - 1), 0) FROM "
        f"(SELECT count(*) AS n FROM {parquet} GROUP BY {key} HAVING count(*) > 1)"
    ).fetchone()[0]
    if duplicates:
        print(f"WARNING [{year}/{table}]: {duplicates} duplicate rows on "
              f"({', '.join(UNIQUE_KEYS[table])})")

    # Validation 5: percentage of nulls per column.
    null_exprs = ", ".join(
        f"100.0 * count_if({quote_ident(c)} IS NULL) / nullif(count(*), 0)" for c in columns
    )
    null_pcts = con.execute(f"SELECT {null_exprs} FROM {parquet}").fetchone()
    nulls = pd.DataFrame(
        {
            "ano": year,
            "tabela": table,
            "coluna": columns,
            "percentual_nulos": [None if p is None else round(p, 4) for p in null_pcts],
        }
    )

    log_row = {
        "ano": year,
        "tabela": table,
        "fonte_arquivo": file_name,
        "linhas_lidas": rows_read,
        "linhas_gravadas": rows_written,
        "v1_colunas": "ok",  # the script stops before writing if it fails
        "v3_notas_fora_intervalo": scores_out,
        "v3_notas": "ok" if scores_out == 0 else "falhou",
        "v4_chave": "+".join(UNIQUE_KEYS[table]),
        "v4_duplicatas": duplicates,
        "v4_unicidade": "ok" if duplicates == 0 else "falhou",
        "processado_em": datetime.now().isoformat(timespec="seconds"),
    }
    return {"log": log_row, "nulls": nulls}


def upsert_csv(path: Path, new: pd.DataFrame, sort_cols: list[str]) -> None:
    """Replace rows with the same (ano, tabela) and keep the rest."""
    if path.exists():
        old = pd.read_csv(path, dtype={"ano": int})
        keys = set(zip(new["ano"], new["tabela"]))
        keep = ~pd.Series(list(zip(old["ano"], old["tabela"])), index=old.index).isin(keys)
        new = pd.concat([old[keep], new], ignore_index=True)
    new = new.sort_values(sort_cols, kind="stable")
    new.to_csv(path, index=False)


def print_summary(log_row: dict) -> None:
    r = log_row
    print(
        f"[{r['ano']}/{r['tabela']}] read={r['linhas_lidas']:,} "
        f"written={r['linhas_gravadas']:,} | v1={r['v1_colunas']} "
        f"v3={r['v3_notas']} ({r['v3_notas_fora_intervalo']}) "
        f"v4={r['v4_unicidade']} ({r['v4_duplicatas']})",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    years_available = sorted(CONFIG["inputs"])
    parser = argparse.ArgumentParser(description="Ingest ENEM microdata into Parquet.")
    parser.add_argument("--anos", type=int, nargs="+", choices=years_available,
                        default=years_available, help="years to process (default: all)")
    args = parser.parse_args()

    CONFIG["duckdb_temp_dir"].mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(f"SET memory_limit = {sql_str(CONFIG['memory_limit'])}")
    con.execute(f"SET temp_directory = {sql_str(str(CONFIG['duckdb_temp_dir']))}")
    con.execute("SET preserve_insertion_order = false")

    for year in sorted(set(args.anos)):
        log_rows, null_frames = [], []
        for table in CONFIG["inputs"][year]:
            result = ingest_table(con, year, table)
            print_summary(result["log"])
            log_rows.append(result["log"])
            null_frames.append(result["nulls"])
        upsert_csv(CONFIG["log_file"], pd.DataFrame(log_rows), ["ano", "tabela"])
        upsert_csv(CONFIG["nulls_file"], pd.concat(null_frames, ignore_index=True),
                   ["ano", "tabela"])

    con.close()


if __name__ == "__main__":
    main()
