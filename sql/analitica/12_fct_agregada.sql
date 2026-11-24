-- fct_agregada: population of the aggregate analyses (2020-2025).
-- Participants with a school in MG (tem_escola AND escola_mg), from
-- stg_base_unica (2020-2023) and stg_resultados (2024-2025).
-- periodo flags the series break between 2023 and 2024 (D002).
-- numero_inscricao is NULL in 2024-2025 and numero_sequencial is NULL in
-- 2020-2023: the two periods use different row identifiers.
-- Applies D002, D004, D007, D008.

CREATE OR REPLACE TABLE fct_agregada AS
SELECT
    -- identification
    ano,
    '2020-2023' AS periodo,
    numero_inscricao,
    CAST(NULL AS VARCHAR) AS numero_sequencial,
    -- school
    codigo_escola,
    codigo_municipio_escola,
    nome_municipio_escola,
    sigla_estado_escola,
    tipo_adm_escola,
    tipo_localizacao_escola,
    tem_escola,
    escola_mg,
    escola_mascarada,
    rede,
    localizacao,
    -- presence
    presenca_cn,
    presenca_ch,
    presenca_lc,
    presente_dia1,
    presente_cn,
    tem_nota_cn,
    cartao_em_branco,
    -- test
    codigo_prova_cn,
    nota_cn,
    vetor_respostas_cn,
    vetor_gabarito_cn
FROM stg_base_unica
WHERE tem_escola AND escola_mg

UNION ALL

SELECT
    ano,
    '2024-2025' AS periodo,
    CAST(NULL AS VARCHAR) AS numero_inscricao,
    numero_sequencial,
    codigo_escola,
    codigo_municipio_escola,
    nome_municipio_escola,
    sigla_estado_escola,
    tipo_adm_escola,
    tipo_localizacao_escola,
    tem_escola,
    escola_mg,
    escola_mascarada,
    rede,
    localizacao,
    presenca_cn,
    presenca_ch,
    presenca_lc,
    presente_dia1,
    presente_cn,
    tem_nota_cn,
    cartao_em_branco,
    codigo_prova_cn,
    nota_cn,
    vetor_respostas_cn,
    vetor_gabarito_cn
FROM stg_resultados
WHERE tem_escola AND escola_mg;
