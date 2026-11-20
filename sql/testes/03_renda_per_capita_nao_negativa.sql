-- Test 3 (integrity): renda_per_capita_sm >= 0 when not NULL.
-- Returns the offending rows per view and year.

SELECT 'stg_base_unica' AS tabela, ano, count(*) AS qtd
FROM stg_base_unica
WHERE renda_per_capita_sm < 0
GROUP BY ano

UNION ALL

SELECT 'stg_participantes' AS tabela, ano, count(*) AS qtd
FROM stg_participantes
WHERE renda_per_capita_sm < 0
GROUP BY ano;
