-- stg_participantes: 2024-2025 PARTICIPANTES table (test taken in MG).
-- Keeps all ingestion columns (qtd_moradores cast to INTEGER) and adds
-- questionnaire derived columns (spec-sql 5.2) using the macros in
-- 00_macros.sql. Income comes from Q007, already renamed to faixa_renda
-- at ingestion, with the same brackets.
-- tipo_escola does not exist in 2024-2025: tipo_escola_rec is NULL.
-- Cannot be linked to stg_resultados (D002).
-- Applies D002, D005, D006.

CREATE OR REPLACE VIEW stg_participantes AS
WITH src AS (
    SELECT * REPLACE (CAST(qtd_moradores AS INTEGER) AS qtd_moradores)
    -- ano is stored as SMALLINT in the files; hive partitioning would
    -- override it with BIGINT.
    FROM read_parquet('data/parquet/participantes/*/*.parquet', hive_partitioning = false)
)

SELECT
    *,
    concluinte_ano(situacao_conclusao, treineiro) AS concluinte_ano,
    tem_questionario(faixa_renda) AS tem_questionario,
    CAST(NULL AS VARCHAR) AS tipo_escola_rec,
    escolaridade_cat(escolaridade_pai) AS escolaridade_pai_cat,
    escolaridade_cat(escolaridade_mae) AS escolaridade_mae_cat,
    escolaridade_nivel(escolaridade_pai) AS escolaridade_pai_nivel,
    escolaridade_nivel(escolaridade_mae) AS escolaridade_mae_nivel,
    escolaridade_max_pais_cat(escolaridade_pai, escolaridade_mae) AS escolaridade_max_pais_cat,
    escolaridade_max_pais_nivel(escolaridade_pai, escolaridade_mae) AS escolaridade_max_pais_nivel,
    ocupacao_cat(grupo_ocupacao_pai) AS ocupacao_pai_cat,
    ocupacao_cat(grupo_ocupacao_mae) AS ocupacao_mae_cat,
    renda_ponto_medio_sm(faixa_renda) AS renda_ponto_medio_sm,
    renda_per_capita_sm(faixa_renda, qtd_moradores) AS renda_per_capita_sm,
    faixa_renda_per_capita(faixa_renda, qtd_moradores) AS faixa_renda_per_capita
FROM src;
