-- Test 1 (integrity): numero_inscricao is unique and never NULL in
-- fct_individual. Returns the duplicated or missing identifiers.

SELECT numero_inscricao, count(*) AS qtd
FROM fct_individual
GROUP BY numero_inscricao
HAVING count(*) > 1 OR numero_inscricao IS NULL;
