-- Test 9 (pending-issues check): item_adaptado has no NULLs in any year
-- of stg_itens (2021 NULLs converted to '0', D005).

SELECT ano, count(*) AS qtd_nulos
FROM stg_itens
WHERE item_adaptado IS NULL
GROUP BY ano;
