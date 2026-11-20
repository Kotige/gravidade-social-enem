-- Test 5 (integrity): escolaridade_*_nivel is NULL if and only if the
-- category is 'nao_sei' or NULL (D005, D006). Covers father, mother and
-- the parents' maximum in both questionnaire views.

WITH pares AS (
    SELECT 'stg_base_unica' AS tabela, 'pai' AS quem,
        escolaridade_pai_cat AS cat, escolaridade_pai_nivel AS nivel
    FROM stg_base_unica
    UNION ALL
    SELECT 'stg_base_unica', 'mae', escolaridade_mae_cat, escolaridade_mae_nivel
    FROM stg_base_unica
    UNION ALL
    SELECT 'stg_base_unica', 'max_pais', escolaridade_max_pais_cat, escolaridade_max_pais_nivel
    FROM stg_base_unica
    UNION ALL
    SELECT 'stg_participantes', 'pai', escolaridade_pai_cat, escolaridade_pai_nivel
    FROM stg_participantes
    UNION ALL
    SELECT 'stg_participantes', 'mae', escolaridade_mae_cat, escolaridade_mae_nivel
    FROM stg_participantes
    UNION ALL
    SELECT 'stg_participantes', 'max_pais', escolaridade_max_pais_cat, escolaridade_max_pais_nivel
    FROM stg_participantes
)

SELECT tabela, quem, cat, nivel, count(*) AS qtd
FROM pares
WHERE (nivel IS NULL) <> (cat IS NULL OR cat = 'nao_sei')
GROUP BY ALL;
