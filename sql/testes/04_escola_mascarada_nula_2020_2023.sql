-- Test 4 (integrity): escola_mascarada is always NULL in 2020-2023
-- (masked codes only exist from 2024 on, D004).

SELECT 'stg_base_unica' AS tabela, ano, count(*) AS qtd
FROM stg_base_unica
WHERE escola_mascarada IS NOT NULL
GROUP BY ano

UNION ALL

SELECT 'fct_agregada' AS tabela, ano, count(*) AS qtd
FROM fct_agregada
WHERE ano BETWEEN 2020 AND 2023 AND escola_mascarada IS NOT NULL
GROUP BY ano;
