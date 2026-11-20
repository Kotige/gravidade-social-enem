-- Test 8 (pending-issues check): mean nota_cn of 2020 graduates in
-- stg_base_unica (before the D007 state cut), with questionnaire and a
-- CN score: 505.2, tolerance 0.1 (D005).

WITH obs AS (
    SELECT avg(nota_cn) AS media_nota_cn
    FROM stg_base_unica
    WHERE ano = 2020 AND concluinte_ano AND tem_questionario AND tem_nota_cn
)

SELECT media_nota_cn, 505.2 AS esperado
FROM obs
WHERE media_nota_cn IS NULL OR abs(media_nota_cn - 505.2) > 0.1;
