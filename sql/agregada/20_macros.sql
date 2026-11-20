-- Aggregate macros with the metrics shared by the agg_ tables (spec-sql 7).
-- Each macro is named after the metric column it produces and takes the
-- fct_agregada columns as arguments; they must be used in a GROUP BY query.
-- Score statistics use only participants with a CN score (tem_nota_cn).
-- Applies D002, D004, D007.

CREATE OR REPLACE MACRO qtd_inscritos() AS
    count(*);

CREATE OR REPLACE MACRO qtd_presentes_dia1(presente_dia1) AS
    count(*) FILTER (presente_dia1);

CREATE OR REPLACE MACRO qtd_presentes_cn(presente_cn) AS
    count(*) FILTER (presente_cn);

-- Share (0 to 1) of day-1 attendees absent on day 2; NULL when no one
-- attended day 1.
CREATE OR REPLACE MACRO taxa_ausencia_dia2(presente_dia1, presente_cn) AS
    count(*) FILTER (presente_dia1 AND NOT presente_cn)
        / nullif(count(*) FILTER (presente_dia1), 0);

CREATE OR REPLACE MACRO qtd_com_nota_cn(tem_nota_cn) AS
    count(*) FILTER (tem_nota_cn);

CREATE OR REPLACE MACRO media_nota_cn(nota_cn, tem_nota_cn) AS
    avg(nota_cn) FILTER (tem_nota_cn);

CREATE OR REPLACE MACRO desvio_padrao_nota_cn(nota_cn, tem_nota_cn) AS
    stddev_samp(nota_cn) FILTER (tem_nota_cn);

CREATE OR REPLACE MACRO p25_nota_cn(nota_cn, tem_nota_cn) AS
    quantile_cont(nota_cn, 0.25) FILTER (tem_nota_cn);

CREATE OR REPLACE MACRO p50_nota_cn(nota_cn, tem_nota_cn) AS
    quantile_cont(nota_cn, 0.50) FILTER (tem_nota_cn);

CREATE OR REPLACE MACRO p75_nota_cn(nota_cn, tem_nota_cn) AS
    quantile_cont(nota_cn, 0.75) FILTER (tem_nota_cn);
