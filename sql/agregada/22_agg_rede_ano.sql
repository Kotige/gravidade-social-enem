-- agg_rede_ano: attendance and CN score summary by year and school network
-- (rede), from fct_agregada (participants with a school in MG).
-- Metrics come from the macros in 20_macros.sql.
-- Applies D002, D006, D007.

CREATE OR REPLACE TABLE agg_rede_ano AS
SELECT
    ano,
    periodo,
    rede,
    qtd_inscritos() AS qtd_inscritos,
    qtd_presentes_dia1(presente_dia1) AS qtd_presentes_dia1,
    qtd_presentes_cn(presente_cn) AS qtd_presentes_cn,
    taxa_ausencia_dia2(presente_dia1, presente_cn) AS taxa_ausencia_dia2,
    qtd_com_nota_cn(tem_nota_cn) AS qtd_com_nota_cn,
    media_nota_cn(nota_cn, tem_nota_cn) AS media_nota_cn,
    desvio_padrao_nota_cn(nota_cn, tem_nota_cn) AS desvio_padrao_nota_cn,
    p25_nota_cn(nota_cn, tem_nota_cn) AS p25_nota_cn,
    p50_nota_cn(nota_cn, tem_nota_cn) AS p50_nota_cn,
    p75_nota_cn(nota_cn, tem_nota_cn) AS p75_nota_cn
FROM fct_agregada
GROUP BY ano, periodo, rede
ORDER BY ano, rede;
