-- agg_escola_ano: attendance and CN score summary by year and school
-- (2024-2025, the only years with codigo_escola), from fct_agregada.
-- Only schools meeting D004: in MG, not masked, and with at least 10
-- participants with a CN score (tem_nota_cn). Includes the school's
-- municipality, network and location. Metrics come from the macros in
-- 20_macros.sql.
-- Applies D002, D004, D006, D007.

CREATE OR REPLACE TABLE agg_escola_ano AS
SELECT
    ano,
    periodo,
    codigo_escola,
    codigo_municipio_escola,
    nome_municipio_escola,
    rede,
    localizacao,
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
WHERE codigo_escola IS NOT NULL
    AND escola_mg
    AND NOT escola_mascarada
GROUP BY ano, periodo, codigo_escola, codigo_municipio_escola, nome_municipio_escola, rede, localizacao
HAVING qtd_com_nota_cn(tem_nota_cn) >= 10
ORDER BY ano, codigo_escola;
