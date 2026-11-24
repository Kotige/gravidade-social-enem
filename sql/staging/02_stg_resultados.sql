-- stg_resultados: 2024-2025 RESULTADOS table (MG filter from ingestion).
-- Keeps all ingestion columns and adds school and presence derived
-- columns (spec-sql 5.1) using the macros in 00_macros.sql.
-- Cannot be linked to stg_participantes (D002).
-- Applies D002, D004, D006, D007, D008.

CREATE OR REPLACE VIEW stg_resultados AS
SELECT
    *,
    tem_escola(sigla_estado_escola) AS tem_escola,
    escola_mg(sigla_estado_escola) AS escola_mg,
    escola_mascarada(sigla_estado_escola, codigo_escola) AS escola_mascarada,
    rede(tipo_adm_escola) AS rede,
    localizacao(tipo_localizacao_escola) AS localizacao,
    presente_dia1(presenca_lc, presenca_ch) AS presente_dia1,
    presente_cn(presenca_cn) AS presente_cn,
    tem_nota_cn(presenca_cn, nota_cn) AS tem_nota_cn,
    cartao_em_branco(presenca_cn, nota_cn) AS cartao_em_branco
-- ano is stored as SMALLINT in the files; hive partitioning would
-- override it with BIGINT.
FROM read_parquet('data/parquet/resultados/*/*.parquet', hive_partitioning = false);
