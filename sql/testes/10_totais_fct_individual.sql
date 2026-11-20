-- Test 10 (pending-issues check): fct_individual totals per year, after
-- the D007 state cut: 125,357 (2020), 96,355 (2021), 100,405 (2022) and
-- 109,571 (2023).

WITH esperado (ano, qtd_esperado) AS (
    VALUES (2020, 125357), (2021, 96355), (2022, 100405), (2023, 109571)
),

obs AS (
    SELECT ano, count(*) AS qtd
    FROM fct_individual
    GROUP BY ano
)

SELECT coalesce(e.ano, o.ano) AS ano, o.qtd, e.qtd_esperado
FROM esperado AS e
FULL OUTER JOIN obs AS o ON e.ano = o.ano
WHERE o.qtd IS DISTINCT FROM e.qtd_esperado;
