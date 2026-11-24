-- Test 12 (integrity): no row has tem_nota_cn = true with nota_cn = 0
-- (blank answer sheets are left out of score analyses, D008).

SELECT 'stg_base_unica' AS tabela, ano, count(*) AS qtd
FROM stg_base_unica
WHERE tem_nota_cn AND nota_cn = 0
GROUP BY ano

UNION ALL

SELECT 'stg_resultados', ano, count(*)
FROM stg_resultados
WHERE tem_nota_cn AND nota_cn = 0
GROUP BY ano

UNION ALL

SELECT 'fct_individual', ano, count(*)
FROM fct_individual
WHERE tem_nota_cn AND nota_cn = 0
GROUP BY ano

UNION ALL

SELECT 'fct_agregada', ano, count(*)
FROM fct_agregada
WHERE tem_nota_cn AND nota_cn = 0
GROUP BY ano;
