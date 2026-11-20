-- Test 7 (pending-issues check): distinct masked MG schools in
-- fct_agregada: 565 in 2024 and 489 in 2025 (D002, D004).

WITH esperado (ano, qtd_esperado) AS (
    VALUES (2024, 565), (2025, 489)
),

obs AS (
    SELECT ano, count(DISTINCT codigo_escola) AS qtd
    FROM fct_agregada
    WHERE escola_mg AND escola_mascarada
    GROUP BY ano
)

SELECT coalesce(e.ano, o.ano) AS ano, o.qtd, e.qtd_esperado
FROM esperado AS e
FULL OUTER JOIN obs AS o ON e.ano = o.ano
WHERE o.qtd IS DISTINCT FROM e.qtd_esperado;
