"""Build the simplified MG municipal mesh used by the choropleth maps.

Input:  data/geo/MG_Municipios_2025.zip (IBGE Malha Municipal 2025, SIRGAS 2000)
Output: data/geo/mg_municipios_2025.geojson
        columns codigo_municipio (7-digit IBGE code), nome_municipio

The original shapefile has ~2.8 million vertices, far more than a
state-wide map needs. Each polygon is simplified with
ST_SimplifyPreserveTopology (tolerance in degrees, default 0.002, about
200 m). Shared borders are simplified per polygon, so tiny slivers may
appear between neighbors; they are not visible at state scale.

Usage:
    python scripts/geo_mg.py [--tolerancia 0.002]
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
GEO_DIR = ROOT / "data" / "geo"
ORIGEM = GEO_DIR / "MG_Municipios_2025.zip"
DESTINO = GEO_DIR / "mg_municipios_2025.geojson"
SHAPEFILE = "MG_Municipios_2025.shp"
N_MUNICIPIOS_MG = 853


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tolerancia", type=float, default=0.002)
    args = parser.parse_args()

    if not ORIGEM.exists():
        raise SystemExit(f"missing {ORIGEM.relative_to(ROOT)}; see docs/fontes.md")

    con = duckdb.connect()
    con.sql("INSTALL spatial; LOAD spatial")
    # GeoJSON is longitude, latitude; keep GDAL from swapping axes on write.
    con.sql("SET geometry_always_xy = true")
    con.sql(
        f"""
        CREATE TABLE malha AS
        SELECT
            CAST(CD_MUN AS INTEGER) AS codigo_municipio,
            NM_MUN AS nome_municipio,
            ST_SimplifyPreserveTopology(geom, {args.tolerancia}) AS geom,
            ST_NPoints(geom) AS pontos_original
        FROM ST_Read('/vsizip/{ORIGEM.as_posix()}/{SHAPEFILE}')
        """
    )

    n, vazios, antes, depois = con.sql(
        """
        SELECT count(*), count(*) FILTER (WHERE ST_IsEmpty(geom)),
               sum(pontos_original), sum(ST_NPoints(geom))
        FROM malha
        """
    ).fetchall()[0]
    if n != N_MUNICIPIOS_MG:
        raise SystemExit(f"expected {N_MUNICIPIOS_MG} municipalities, got {n}")
    if vazios:
        raise SystemExit(f"{vazios} geometries became empty; lower --tolerancia")

    DESTINO.unlink(missing_ok=True)
    con.sql(
        f"""
        COPY (SELECT codigo_municipio, nome_municipio, geom FROM malha
              ORDER BY codigo_municipio)
        TO '{DESTINO.as_posix()}'
        WITH (FORMAT GDAL, DRIVER 'GeoJSON',
              LAYER_CREATION_OPTIONS 'COORDINATE_PRECISION=5')
        """
    )
    tamanho = DESTINO.stat().st_size / 1e6
    print(
        f"{n} municipalities, {antes:,} -> {depois:,} vertices, "
        f"{DESTINO.relative_to(ROOT)} ({tamanho:.1f} MB)"
    )


if __name__ == "__main__":
    main()
