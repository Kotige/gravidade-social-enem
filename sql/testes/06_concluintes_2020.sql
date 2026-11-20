-- Test 6 (pending-issues check): graduates of 2020 in stg_base_unica,
-- before the D007 state cut: 125,998, of which 1,548 without
-- questionnaire (notebooks/00_pendencias.ipynb).

WITH obs AS (
    SELECT
        count(*) AS concluintes,
        count(*) FILTER (NOT tem_questionario) AS sem_questionario
    FROM stg_base_unica
    WHERE ano = 2020 AND concluinte_ano
)

SELECT *, 125998 AS concluintes_esperado, 1548 AS sem_questionario_esperado
FROM obs
WHERE concluintes <> 125998 OR sem_questionario <> 1548;
