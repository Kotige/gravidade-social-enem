-- Test 11 (integrity): sigla_estado_prova is never NULL in the staging
-- views, so the state filter of fct_individual (test state when there is
-- no school, D007) cannot drop anyone silently.

SELECT 'stg_base_unica' AS tabela, ano, count(*) AS qtd_nulos
FROM stg_base_unica
WHERE sigla_estado_prova IS NULL
GROUP BY ano

UNION ALL

SELECT 'stg_resultados', ano, count(*)
FROM stg_resultados
WHERE sigla_estado_prova IS NULL
GROUP BY ano

UNION ALL

SELECT 'stg_participantes', ano, count(*)
FROM stg_participantes
WHERE sigla_estado_prova IS NULL
GROUP BY ano;
