-- Test 2 (integrity): every recoded column contains only the expected
-- values (D004-D007). Also fails when an original code is filled but its
-- recoded category is NULL (an unmapped code), except for codes that are
-- NULL by rule (tipo_escola '1' and '4', D006). The *_nivel columns are
-- checked against their categories in test 5.
-- Returns one row per (table, column, original code, recoded value).

WITH esperado (coluna, valor) AS (
    SELECT 'rede', unnest(['federal', 'estadual_municipal', 'privada'])
    UNION ALL SELECT 'localizacao', unnest(['urbana', 'rural'])
    UNION ALL SELECT 'tipo_escola_rec', unnest(['publica', 'privada'])
    UNION ALL SELECT 'escolaridade_cat', unnest(
        ['fund_incompleto', 'fund_completo', 'medio_completo', 'superior_completo', 'nao_sei'])
    UNION ALL SELECT 'escolaridade_nivel', unnest(['1', '2', '3', '4'])
    UNION ALL SELECT 'ocupacao_cat', unnest(
        ['grupo_a', 'grupo_b', 'grupo_c', 'grupo_d', 'grupo_e', 'nao_sei'])
    UNION ALL SELECT 'renda_ponto_medio_sm', CAST(CAST(unnest(
        [0, 0.5, 1.25, 1.75, 2.25, 2.75, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.5, 11, 13.5, 17.5, 25])
        AS DOUBLE) AS VARCHAR)
    UNION ALL SELECT 'faixa_renda_per_capita', unnest(
        ['ate_meio_sm', 'meio_a_1_sm', '1_a_2_sm', 'acima_2_sm'])
    UNION ALL SELECT 'periodo_2020_2023', '2020-2023'
    UNION ALL SELECT 'periodo_2024_2025', '2024-2025'
    UNION ALL SELECT 'item_adaptado', unnest(['0', '1'])
),

-- Long format: (tabela, coluna, regra, original, valor, exige_valor).
-- regra names the expected set; exige_valor = original filled and the
-- recoded value must therefore be filled.
recodificadas AS (
    -- School network and location
    SELECT 'stg_base_unica' AS tabela, 'rede' AS coluna, 'rede' AS regra,
        tipo_adm_escola AS original, rede AS valor, tipo_adm_escola IS NOT NULL AS exige_valor
    FROM stg_base_unica
    UNION ALL
    SELECT 'stg_resultados', 'rede', 'rede', tipo_adm_escola, rede, tipo_adm_escola IS NOT NULL
    FROM stg_resultados
    UNION ALL
    SELECT 'fct_agregada', 'rede', 'rede', tipo_adm_escola, rede, tipo_adm_escola IS NOT NULL
    FROM fct_agregada
    UNION ALL
    SELECT 'stg_base_unica', 'localizacao', 'localizacao',
        tipo_localizacao_escola, localizacao, tipo_localizacao_escola IS NOT NULL
    FROM stg_base_unica
    UNION ALL
    SELECT 'stg_resultados', 'localizacao', 'localizacao',
        tipo_localizacao_escola, localizacao, tipo_localizacao_escola IS NOT NULL
    FROM stg_resultados
    UNION ALL
    SELECT 'fct_agregada', 'localizacao', 'localizacao',
        tipo_localizacao_escola, localizacao, tipo_localizacao_escola IS NOT NULL
    FROM fct_agregada

    -- Declared school type ('1' and '4' are NULL by rule)
    UNION ALL
    SELECT 'stg_base_unica', 'tipo_escola_rec', 'tipo_escola_rec',
        tipo_escola, tipo_escola_rec, tipo_escola IN ('2', '3')
    FROM stg_base_unica
    UNION ALL
    SELECT 'stg_participantes', 'tipo_escola_rec', 'tipo_escola_rec',
        NULL, tipo_escola_rec, false
    FROM stg_participantes

    -- Parents' education, occupation and income (both questionnaire views)
    UNION ALL
    SELECT tabela, coluna, regra, original, valor, original IS NOT NULL
    FROM (
        SELECT 'stg_base_unica' AS tabela, * FROM (
            SELECT
                escolaridade_pai, escolaridade_mae, grupo_ocupacao_pai, grupo_ocupacao_mae,
                faixa_renda,
                escolaridade_pai_cat, escolaridade_mae_cat, escolaridade_max_pais_cat,
                CAST(escolaridade_pai_nivel AS VARCHAR) AS escolaridade_pai_nivel,
                CAST(escolaridade_mae_nivel AS VARCHAR) AS escolaridade_mae_nivel,
                CAST(escolaridade_max_pais_nivel AS VARCHAR) AS escolaridade_max_pais_nivel,
                ocupacao_pai_cat, ocupacao_mae_cat,
                CAST(renda_ponto_medio_sm AS VARCHAR) AS renda_ponto_medio_sm,
                faixa_renda_per_capita
            FROM stg_base_unica
        )
        UNION ALL
        SELECT 'stg_participantes' AS tabela, * FROM (
            SELECT
                escolaridade_pai, escolaridade_mae, grupo_ocupacao_pai, grupo_ocupacao_mae,
                faixa_renda,
                escolaridade_pai_cat, escolaridade_mae_cat, escolaridade_max_pais_cat,
                CAST(escolaridade_pai_nivel AS VARCHAR) AS escolaridade_pai_nivel,
                CAST(escolaridade_mae_nivel AS VARCHAR) AS escolaridade_mae_nivel,
                CAST(escolaridade_max_pais_nivel AS VARCHAR) AS escolaridade_max_pais_nivel,
                ocupacao_pai_cat, ocupacao_mae_cat,
                CAST(renda_ponto_medio_sm AS VARCHAR) AS renda_ponto_medio_sm,
                faixa_renda_per_capita
            FROM stg_participantes
        )
    ) AS q
    CROSS JOIN LATERAL (
        VALUES
            ('escolaridade_pai_cat', 'escolaridade_cat', q.escolaridade_pai, q.escolaridade_pai_cat),
            ('escolaridade_mae_cat', 'escolaridade_cat', q.escolaridade_mae, q.escolaridade_mae_cat),
            ('escolaridade_max_pais_cat', 'escolaridade_cat',
                coalesce(q.escolaridade_pai, q.escolaridade_mae), q.escolaridade_max_pais_cat),
            -- Levels: only the value set is checked here (original NULL).
            ('escolaridade_pai_nivel', 'escolaridade_nivel', NULL, q.escolaridade_pai_nivel),
            ('escolaridade_mae_nivel', 'escolaridade_nivel', NULL, q.escolaridade_mae_nivel),
            ('escolaridade_max_pais_nivel', 'escolaridade_nivel', NULL, q.escolaridade_max_pais_nivel),
            ('ocupacao_pai_cat', 'ocupacao_cat', q.grupo_ocupacao_pai, q.ocupacao_pai_cat),
            ('ocupacao_mae_cat', 'ocupacao_cat', q.grupo_ocupacao_mae, q.ocupacao_mae_cat),
            ('renda_ponto_medio_sm', 'renda_ponto_medio_sm', q.faixa_renda, q.renda_ponto_medio_sm),
            ('faixa_renda_per_capita', 'faixa_renda_per_capita', q.faixa_renda, q.faixa_renda_per_capita)
    ) AS v (coluna, regra, original, valor)

    -- Period of fct_agregada: the expected set depends on the year
    UNION ALL
    SELECT 'fct_agregada', 'periodo',
        CASE WHEN ano <= 2023 THEN 'periodo_2020_2023' ELSE 'periodo_2024_2025' END,
        CAST(ano AS VARCHAR), periodo, true
    FROM (SELECT DISTINCT ano, periodo FROM fct_agregada)

    -- Item adaptation flag after the 2021 fix
    UNION ALL
    SELECT 'stg_itens', 'item_adaptado', 'item_adaptado', NULL, item_adaptado, true
    FROM stg_itens
)

SELECT r.tabela, r.coluna, r.original, r.valor, count(*) AS qtd
FROM recodificadas AS r
LEFT JOIN esperado AS e ON e.coluna = r.regra AND e.valor = r.valor
WHERE (r.valor IS NOT NULL AND e.valor IS NULL)
    OR (r.valor IS NULL AND r.exige_valor)
GROUP BY ALL
ORDER BY ALL;
