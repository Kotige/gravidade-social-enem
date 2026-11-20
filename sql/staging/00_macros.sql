-- Scalar macros with the recoding rules shared by the staging views
-- (spec-sql 5.1 and 5.2). Each macro is named after the derived column it
-- produces and takes the original ingestion columns as arguments.
-- Applies D002, D004, D005, D006, D007.

-- ---------------------------------------------------------------------------
-- School and presence (stg_base_unica, stg_resultados)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE MACRO tem_escola(sigla_estado_escola) AS
    sigla_estado_escola IS NOT NULL;

-- false when there is no school.
CREATE OR REPLACE MACRO escola_mg(sigla_estado_escola) AS
    coalesce(sigla_estado_escola = 'MG', false);

-- Masked codes have the format 600xxxxx; real codes start with the IBGE
-- state code (D004). NULL when there is no school.
CREATE OR REPLACE MACRO escola_mascarada(sigla_estado_escola, codigo_escola) AS
    CASE
        WHEN sigla_estado_escola IS NOT NULL THEN starts_with(codigo_escola, '6')
    END;

CREATE OR REPLACE MACRO rede(tipo_adm_escola) AS
    CASE tipo_adm_escola
        WHEN '1' THEN 'federal'
        WHEN '2' THEN 'estadual_municipal'
        WHEN '3' THEN 'estadual_municipal'
        WHEN '4' THEN 'privada'
    END;

CREATE OR REPLACE MACRO localizacao(tipo_localizacao_escola) AS
    CASE tipo_localizacao_escola
        WHEN '1' THEN 'urbana'
        WHEN '2' THEN 'rural'
    END;

-- Present ('1') or eliminated ('2') count as attendance (D007).
CREATE OR REPLACE MACRO presente_dia1(presenca_lc, presenca_ch) AS
    presenca_lc IN ('1', '2') OR presenca_ch IN ('1', '2');

CREATE OR REPLACE MACRO presente_cn(presenca_cn) AS
    presenca_cn IN ('1', '2');

-- Only present participants have a CN score (D007).
CREATE OR REPLACE MACRO tem_nota_cn(presenca_cn) AS
    presenca_cn = '1';

-- ---------------------------------------------------------------------------
-- Questionnaire (stg_base_unica, stg_participantes)
-- ---------------------------------------------------------------------------

CREATE OR REPLACE MACRO concluinte_ano(situacao_conclusao, treineiro) AS
    situacao_conclusao = '2' AND treineiro = '0';

CREATE OR REPLACE MACRO tem_questionario(faixa_renda) AS
    faixa_renda IS NOT NULL;

-- '1' (did not answer) and '4' (abroad, 2020 only) become NULL (D006).
CREATE OR REPLACE MACRO tipo_escola_rec(tipo_escola) AS
    CASE tipo_escola
        WHEN '2' THEN 'publica'
        WHEN '3' THEN 'privada'
    END;

-- Parents' education (Q001/Q002): letter -> category; 'H' is "don't know",
-- kept as its own category outside the scale (D005, D006).
CREATE OR REPLACE MACRO escolaridade_cat(escolaridade) AS
    CASE
        WHEN escolaridade IN ('A', 'B', 'C') THEN 'fund_incompleto'
        WHEN escolaridade = 'D' THEN 'fund_completo'
        WHEN escolaridade = 'E' THEN 'medio_completo'
        WHEN escolaridade IN ('F', 'G') THEN 'superior_completo'
        WHEN escolaridade = 'H' THEN 'nao_sei'
    END;

-- Level 1-4; NULL for 'nao_sei' and missing (D006).
CREATE OR REPLACE MACRO escolaridade_nivel(escolaridade) AS
    CASE escolaridade_cat(escolaridade)
        WHEN 'fund_incompleto' THEN 1
        WHEN 'fund_completo' THEN 2
        WHEN 'medio_completo' THEN 3
        WHEN 'superior_completo' THEN 4
    END;

-- Highest known level between father and mother; greatest() ignores NULLs,
-- so the known parent is used when only one is known (D006).
CREATE OR REPLACE MACRO escolaridade_max_pais_nivel(escolaridade_pai, escolaridade_mae) AS
    greatest(escolaridade_nivel(escolaridade_pai), escolaridade_nivel(escolaridade_mae));

-- Category of the highest level; 'nao_sei' when both are unknown;
-- NULL without questionnaire (D006).
CREATE OR REPLACE MACRO escolaridade_max_pais_cat(escolaridade_pai, escolaridade_mae) AS
    CASE
        WHEN escolaridade_cat(escolaridade_pai) IS NULL
            AND escolaridade_cat(escolaridade_mae) IS NULL THEN NULL
        ELSE CASE escolaridade_max_pais_nivel(escolaridade_pai, escolaridade_mae)
            WHEN 1 THEN 'fund_incompleto'
            WHEN 2 THEN 'fund_completo'
            WHEN 3 THEN 'medio_completo'
            WHEN 4 THEN 'superior_completo'
            ELSE 'nao_sei'
        END
    END;

-- Parents' occupation (Q003/Q004): nominal groups A-E; 'F' is "don't know"
-- (D005, D006).
CREATE OR REPLACE MACRO ocupacao_cat(grupo_ocupacao) AS
    CASE
        WHEN grupo_ocupacao IN ('A', 'B', 'C', 'D', 'E') THEN 'grupo_' || lower(grupo_ocupacao)
        WHEN grupo_ocupacao = 'F' THEN 'nao_sei'
    END;

-- Family income bracket midpoint in minimum wages (D006). Same brackets in
-- Q006 (2020-2023) and Q007 (2024-2025).
CREATE OR REPLACE MACRO renda_ponto_medio_sm(faixa_renda) AS
    CAST(
        CASE faixa_renda
            WHEN 'A' THEN 0.0
            WHEN 'B' THEN 0.5
            WHEN 'C' THEN 1.25
            WHEN 'D' THEN 1.75
            WHEN 'E' THEN 2.25
            WHEN 'F' THEN 2.75
            WHEN 'G' THEN 3.5
            WHEN 'H' THEN 4.5
            WHEN 'I' THEN 5.5
            WHEN 'J' THEN 6.5
            WHEN 'K' THEN 7.5
            WHEN 'L' THEN 8.5
            WHEN 'M' THEN 9.5
            WHEN 'N' THEN 11.0
            WHEN 'O' THEN 13.5
            WHEN 'P' THEN 17.5
            WHEN 'Q' THEN 25.0
        END AS DOUBLE
    );

CREATE OR REPLACE MACRO renda_per_capita_sm(faixa_renda, qtd_moradores) AS
    renda_ponto_medio_sm(faixa_renda) / qtd_moradores;

-- Brackets: <= 0.5, (0.5; 1], (1; 2], > 2; zero income in 'ate_meio_sm'.
CREATE OR REPLACE MACRO faixa_renda_per_capita(faixa_renda, qtd_moradores) AS
    CASE
        WHEN renda_per_capita_sm(faixa_renda, qtd_moradores) IS NULL THEN NULL
        WHEN renda_per_capita_sm(faixa_renda, qtd_moradores) <= 0.5 THEN 'ate_meio_sm'
        WHEN renda_per_capita_sm(faixa_renda, qtd_moradores) <= 1 THEN 'meio_a_1_sm'
        WHEN renda_per_capita_sm(faixa_renda, qtd_moradores) <= 2 THEN '1_a_2_sm'
        ELSE 'acima_2_sm'
    END;
