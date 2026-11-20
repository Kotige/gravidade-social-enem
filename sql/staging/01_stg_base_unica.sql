-- stg_base_unica: 2020-2023 single-table microdata (MG filter from ingestion).
-- Keeps all ingestion columns (qtd_moradores cast to INTEGER) and adds
-- school, presence and questionnaire derived columns (spec-sql 5.1, 5.2)
-- using the macros in 00_macros.sql.
-- codigo_escola does not exist in 2020-2023 and is created as NULL.
-- Applies D002, D004, D005, D006, D007.

CREATE OR REPLACE VIEW stg_base_unica AS
WITH src AS (
    SELECT * REPLACE (CAST(qtd_moradores AS INTEGER) AS qtd_moradores)
    -- ano is stored as SMALLINT in the files; hive partitioning would
    -- override it with BIGINT.
    FROM read_parquet('data/parquet/base_unica/*/*.parquet', hive_partitioning = false)
)

SELECT
    *,
    -- School and presence (5.1)
    CAST(NULL AS VARCHAR) AS codigo_escola,
    tem_escola(sigla_estado_escola) AS tem_escola,
    escola_mg(sigla_estado_escola) AS escola_mg,
    -- Masked codes only exist from 2024 on (D004).
    CAST(NULL AS BOOLEAN) AS escola_mascarada,
    rede(tipo_adm_escola) AS rede,
    localizacao(tipo_localizacao_escola) AS localizacao,
    presente_dia1(presenca_lc, presenca_ch) AS presente_dia1,
    presente_cn(presenca_cn) AS presente_cn,
    tem_nota_cn(presenca_cn) AS tem_nota_cn,
    -- Questionnaire (5.2)
    concluinte_ano(situacao_conclusao, treineiro) AS concluinte_ano,
    tem_questionario(faixa_renda) AS tem_questionario,
    tipo_escola_rec(tipo_escola) AS tipo_escola_rec,
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
