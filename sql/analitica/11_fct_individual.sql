-- fct_individual: population of the individual analysis (2020-2023).
-- All stg_base_unica columns for graduates of the year (concluinte_ano):
-- school state = MG when the school exists; otherwise test state = MG.
-- Graduates without questionnaire stay in the table (tem_questionario =
-- false) and are excluded only in questionnaire analyses (D005).
-- Applies D002, D005, D007.

CREATE OR REPLACE TABLE fct_individual AS
SELECT *
FROM stg_base_unica
WHERE concluinte_ano
    AND CASE
        WHEN tem_escola THEN escola_mg
        ELSE sigla_estado_prova = 'MG'
    END;
