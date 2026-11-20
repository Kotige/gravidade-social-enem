-- stg_itens: 2020-2025 CN test items (CN filter from ingestion).
-- Keeps all ingestion columns; in 2021 NULL item_adaptado becomes '0'
-- (not adapted), and adds item_valido (item not dropped at scoring).
-- Applies D005.

CREATE OR REPLACE VIEW stg_itens AS
SELECT
    * REPLACE (
        CASE
            WHEN ano = 2021 AND item_adaptado IS NULL THEN '0'
            ELSE item_adaptado
        END AS item_adaptado
    ),
    item_abandonado = '0' AS item_valido
-- ano is stored as SMALLINT in the files; hive partitioning would
-- override it with BIGINT.
FROM read_parquet('data/parquet/itens/*/*.parquet', hive_partitioning = false);
