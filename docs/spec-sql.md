# Especificação do modelo SQL

Script: `scripts/build_db.py`
Etapa do plano: 02 - Limpeza e modelagem em SQL
Relacionado: D001 a D007 em `docs/decisoes.md`, `docs/spec-ingestao.md`

## 1. Objetivo

Construir, a partir dos Parquets da ingestão, um banco DuckDB com uma camada de dados limpa, recodificada e documentada. Todas as análises das Etapas 3 a 5 e os dados do app partem dessas tabelas.

A camada aplica as decisões D004 a D007 (recodificação, nulos, escolas mascaradas, UF e presença) e as populações da D002. Nenhuma análise estatística é feita aqui.

## 2. Entradas

Parquets gerados pela ingestão (`data/parquet/`):

| Pasta            | Anos      |
| ---------------- | --------- |
| `base_unica/`    | 2020–2023 |
| `participantes/` | 2024–2025 |
| `resultados/`    | 2024–2025 |
| `itens/`         | 2020–2025 |

## 3. Saída

Um único arquivo `data/enem.duckdb` (já ignorado pelo Git), com três camadas:

| Camada    | Prefixo | Materialização | Papel                                     |
| --------- | ------- | -------------- | ----------------------------------------- |
| staging   | `stg_`  | view           | tipos, recodificações e colunas derivadas |
| analítica | `fct_`  | tabela         | populações de análise definidas na D002   |
| agregada  | `agg_`  | tabela         | resumos por município, rede e escola      |

O banco é recriado do zero a cada execução (idempotente).

As views de staging leem os Parquets por caminho relativo à raiz do projeto (`data/parquet/...`). Para que funcionem de qualquer diretório, o banco é sempre aberto pela função `conectar()` de `src/db.py`, que abre `data/enem.duckdb` e define a raiz do projeto como `file_search_path`. Notebooks e scripts usam essa função.

## 4. Organização dos arquivos

```
sql/
├── staging/
│   ├── 00_macros.sql
│   ├── 01_stg_base_unica.sql
│   ├── 02_stg_resultados.sql
│   ├── 03_stg_participantes.sql
│   └── 04_stg_itens.sql
├── analitica/
│   ├── 11_fct_individual.sql
│   └── 12_fct_agregada.sql
├── agregada/
│   ├── 20_macros.sql
│   ├── 21_agg_municipio_ano.sql
│   ├── 22_agg_rede_ano.sql
│   └── 23_agg_escola_ano.sql
└── testes/
    └── *.sql
```

- Um arquivo por tabela ou view, com um comentário no topo dizendo o que ela contém e quais decisões aplica (ex.: `-- aplica D005, D006`).
- O prefixo numérico define a ordem de execução.
- `00_macros.sql` define macros escalares do DuckDB com as regras de recodificação compartilhadas pelas views: escola e presença (5.1) e questionário (5.2). Cada macro tem o nome da coluna derivada que produz e recebe as colunas originais como argumentos. As views só aplicam as macros, sem repetir as regras.
- `20_macros.sql` define, do mesmo modo, macros de agregação com as métricas comuns às tabelas `agg_` (seção 7). Cada macro tem o nome da métrica que produz.
- As views leem os Parquets com `hive_partitioning = false`, porque `ano` já está gravado nos arquivos como `SMALLINT`, e a partição hive o sobrescreveria com `BIGINT`.
- `scripts/build_db.py` só executa os arquivos em ordem e roda os testes; toda a lógica fica nos `.sql`.

## 5. Camada staging

Todas as views de staging mantêm as colunas originais da ingestão e acrescentam as colunas derivadas abaixo. Os códigos das categorias devem ser conferidos no dicionário de cada ano antes da implementação.

Tipos: `qtd_moradores` é convertida para `INTEGER` na própria coluna. Os códigos de categoria (`presenca_*`, `situacao_conclusao`, `tipo_adm_escola` etc.) continuam `VARCHAR`.

### 5.1 Colunas derivadas comuns (`stg_base_unica` e `stg_resultados`)

| Coluna             | Regra                                                                     | Decisão |
| ------------------ | ------------------------------------------------------------------------- | ------- |
| `tem_escola`       | `sigla_estado_escola IS NOT NULL`                                         | D002    |
| `escola_mg`        | `sigla_estado_escola = 'MG'`; `false` quando não há escola                | D004    |
| `escola_mascarada` | `codigo_escola` começa com `6`; nulo se não há escola; nulo em 2020–2023  | D004    |
| `rede`             | `federal` (1), `estadual_municipal` (2, 3), `privada` (4)                 | D006    |
| `localizacao`      | `urbana` (1), `rural` (2)                                                 | —       |
| `presente_dia1`    | `presenca_lc` ou `presenca_ch` em (`'1'`, `'2'`): presente ou eliminado   | D007    |
| `presente_cn`      | `presenca_cn` em (`'1'`, `'2'`): compareceu ao 2º dia (usar na abstenção) | D007    |
| `tem_nota_cn`      | `presenca_cn = '1' AND nota_cn > 0`: tem nota em CN (usar nas análises de nota) | D007, D008 |
| `cartao_em_branco` | `presenca_cn = '1' AND nota_cn = 0`: presente com cartão-resposta em branco | D008    |

Em `stg_base_unica`, `codigo_escola` não existe; a coluna é criada como nula para que as duas views tenham a mesma estrutura.

### 5.2 Colunas derivadas do questionário (`stg_base_unica`, `stg_participantes`)

| Coluna                   | Regra                                                                                                        | Decisão    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------ | ---------- |
| `concluinte_ano`         | `situacao_conclusao = '2' AND treineiro = '0'`                                                               | D002       |
| `tem_questionario`       | `faixa_renda IS NOT NULL`                                                                                    | D005       |
| `tipo_escola_rec`        | `publica` (2), `privada` (3); `1` (não respondeu) e `4` (exterior, só em 2020) viram nulo                    | D006       |
| `escolaridade_pai_cat`   | `fund_incompleto` (A–C), `fund_completo` (D), `medio_completo` (E), `superior_completo` (F–G), `nao_sei` (H) | D005, D006 |
| `escolaridade_mae_cat`   | idem                                                                                                         | D005, D006 |
| `escolaridade_pai_nivel` | 1 a 4 conforme a categoria; nulo para `nao_sei`                                                              | D006       |
| `escolaridade_mae_nivel` | idem                                                                                                         | D006       |
| `escolaridade_max_pais_cat`   | categoria do maior nível entre pai e mãe; usa o conhecido se só um for; `nao_sei` se ambos; nulo sem questionário | D006 |
| `escolaridade_max_pais_nivel` | maior nível (1 a 4) entre pai e mãe; usa o conhecido se só um for; nulo para `nao_sei` e sem questionário        | D006 |
| `ocupacao_pai_cat`       | `grupo_a` … `grupo_e` (A–E), `nao_sei` (F); categoria nominal                                                | D005, D006 |
| `ocupacao_mae_cat`       | idem                                                                                                         | D005, D006 |
| `renda_ponto_medio_sm`   | ponto médio da faixa conforme a tabela da D006                                                               | D006       |
| `renda_per_capita_sm`    | `renda_ponto_medio_sm / qtd_moradores`                                                                       | D006       |
| `faixa_renda_per_capita` | `ate_meio_sm` (<= 0,5), `meio_a_1_sm` (0,5; 1], `1_a_2_sm` (1; 2], `acima_2_sm` (> 2); renda 0 em `ate_meio_sm` | D006       |

Em 2024–2025, a renda vem da `Q007` (já renomeada para `faixa_renda` na ingestão), com as mesmas faixas; conferir no dicionário.

Em `stg_participantes`, `tipo_escola` não existe; `tipo_escola_rec` é criada como nula.

### 5.3 `stg_itens`

| Coluna          | Regra                   | Decisão |
| --------------- | ----------------------- | ------- |
| `item_adaptado` | nulo vira `'0'` em 2021 | D005    |
| `item_valido`   | `item_abandonado = '0'` | —       |

## 6. Camada analítica

### 6.1 `fct_individual` (2020–2023)

Contém todas as colunas de `stg_base_unica`. Os concluintes sem questionário permanecem na tabela, marcados por `tem_questionario = false`, e são excluídos apenas nas análises que usam o questionário (D005).

População da análise individual (D002):

- `concluinte_ano = true`;
- UF da escola = MG quando a escola existir; senão, UF da prova = MG (D007).

### 6.2 `fct_agregada` (2020–2025)

População das análises agregadas (D002): participantes com `tem_escola = true` e `escola_mg = true`. União de `stg_base_unica` (2020–2023) e `stg_resultados` (2024–2025), com as colunas:

- identificação: `ano`, `periodo`, `numero_inscricao` (nulo em 2024–2025), `numero_sequencial` (nulo em 2020–2023);
- escola: `codigo_escola`, `codigo_municipio_escola`, `nome_municipio_escola`, `sigla_estado_escola`, `tipo_adm_escola`, `tipo_localizacao_escola`, `tem_escola`, `escola_mg`, `escola_mascarada`, `rede`, `localizacao`;
- presença: `presenca_cn`, `presenca_ch`, `presenca_lc`, `presente_dia1`, `presente_cn`, `tem_nota_cn`, `cartao_em_branco`;
- prova: `codigo_prova_cn`, `nota_cn`, `vetor_respostas_cn`, `vetor_gabarito_cn`.

A coluna `periodo` vale `'2020-2023'` ou `'2024-2025'`, para lembrar a quebra de série registrada na D002.

## 7. Camada agregada

Todas as tabelas guardam o `n` de cada grupo. A supressão de grupos pequenos (menos de 10) é aplicada só na exportação para o app, e não aqui.

Todas as tabelas têm `ano` e `periodo` (vindo da `fct_agregada`), seguidos das colunas do grupo e das métricas abaixo, comuns às três tabelas:

| Coluna                  | Regra                                                                                     |
| ----------------------- | ----------------------------------------------------------------------------------------- |
| `qtd_inscritos`         | `count(*)`                                                                                |
| `qtd_presentes_dia1`    | participantes com `presente_dia1`                                                         |
| `qtd_presentes_cn`      | participantes com `presente_cn`                                                           |
| `taxa_ausencia_dia2`    | `count(presente_dia1 AND NOT presente_cn) / count(presente_dia1)`; proporção de 0 a 1, nula quando não há presentes no 1º dia |
| `qtd_com_nota_cn`       | participantes com `tem_nota_cn`                                                           |
| `media_nota_cn`         | média de `nota_cn`                                                                        |
| `desvio_padrao_nota_cn` | desvio-padrão amostral (`stddev_samp`) de `nota_cn`                                       |
| `p25_nota_cn`, `p50_nota_cn`, `p75_nota_cn` | percentis de `nota_cn` com `quantile_cont`                            |

Média, desvio-padrão e percentis são calculados só sobre `tem_nota_cn = true`.

### 7.1 `agg_municipio_ano`

Por `ano` e `codigo_municipio_escola`, levando `nome_municipio_escola` (a partir de `fct_agregada`): inscritos, presentes no 1º dia (`presente_dia1`), presentes no 2º dia (`presente_cn`), taxa de ausência no 2º dia entre os presentes no 1º, participantes com nota (`tem_nota_cn`) e média, desvio-padrão e percentis 25, 50 e 75 de `nota_cn`.

### 7.2 `agg_rede_ano`

As mesmas métricas, por `ano` e `rede`.

### 7.3 `agg_escola_ano` (2024–2025)

As mesmas métricas, por `ano` e `codigo_escola`, só para escolas que atendem à D004: mineiras, não mascaradas e com pelo menos 10 participantes com nota em CN (`tem_nota_cn`). Inclui o município (`codigo_municipio_escola`, `nome_municipio_escola`), a `rede` e a `localizacao` da escola.

## 8. Testes

Cada arquivo em `sql/testes/` é uma consulta que retorna **zero linhas quando o teste passa**. O `build_db.py` executa todos ao final, mostra até 10 linhas de cada teste que falhar e, depois de rodar todos, falha com um resumo se algum tiver retornado linhas.

**Integridade**

1. `numero_inscricao` único em `fct_individual`.
2. Todas as colunas recodificadas só contêm os valores previstos (ex.: `rede` ∈ {`federal`, `estadual_municipal`, `privada`}).
3. `renda_per_capita_sm >= 0` quando não nula.
4. `escola_mascarada` sempre nula em 2020–2023.
5. `escolaridade_*_nivel` nulo se, e somente se, a categoria for `nao_sei` ou nula.
   **Conferência com as investigações das pendências**

Os testes 6 e 8 usam a população **antes** do recorte de UF da D007 (concluintes de `stg_base_unica`, com `concluinte_ano = true`). O teste 10 usa a população **depois** do recorte (`fct_individual`).

6. Concluintes de 2020 em `stg_base_unica`: 125.998, dos quais 1.548 sem questionário.
7. Escolas mascaradas mineiras distintas (`count(DISTINCT codigo_escola)`) em `fct_agregada`: 565 em 2024 e 489 em 2025.
8. Média de `nota_cn` dos concluintes de 2020 em `stg_base_unica`, com questionário e com nota em CN (`tem_nota_cn`): 505,23, com tolerância de 0,01.
9. `item_adaptado` sem nulos em todos os anos.
10. Totais de `fct_individual` por ano: 125.357 (2020), 96.355 (2021), 100.405 (2022) e 109.571 (2023).
    Os testes 6 a 8 e 10 usam números obtidos em `notebooks/00_pendencias.ipynb` e garantem que a camada SQL reproduz o que foi verificado à mão.

**Integridade do recorte de UF**

11. `sigla_estado_prova` nunca nula em `stg_base_unica`, `stg_resultados` e `stg_participantes`, para que o filtro de UF da `fct_individual` não descarte ninguém em silêncio.

**Integridade dos cartões em branco**

12. Nenhuma linha com `tem_nota_cn = true` e `nota_cn = 0` em `stg_base_unica`, `stg_resultados`, `fct_individual` e `fct_agregada` (D008).

## 9. Fora do escopo

- Índice de bens (Etapa 4)
- Modelos estatísticos (Etapa 4)
- Decodificação das respostas por questão e raio-X dos itens (Etapa 5)
- Cruzamento com o Censo Escolar (Etapa 4)
- Exportação de JSONs para o app (Etapa 6)
- Arredondamento das métricas para exportação (Etapa 6): a soma em paralelo do DuckDB gera diferenças na 12ª casa decimal entre builds.
- Conferência das 38 linhas de `agg_municipio_ano` com `taxa_ausencia_dia2` nula contra a regra de supressão do app (Etapa 6).

## 10. Decisões tomadas na D007

1. **UF da análise individual:** UF da escola quando existir; senão, UF da prova.
2. **Eliminados:** contam como presentes na abstenção (`presente_dia1`, `presente_cn`) e ficam fora das análises de nota (`tem_nota_cn`).
3. **Presente no 1º dia:** presente ou eliminado em LC **ou** em CH.

## 11. Requisitos técnicos

- DuckDB; os arquivos `.sql` não dependem de Python.
- Limite de memória de 3 GB, como na ingestão.
- Conexão ao banco sempre por `conectar()` em `src/db.py` (ver seção 3).
- Código e comentários em inglês; nomes de colunas em português (D001).
- Valores das categorias recodificadas em minúsculas, sem acentos (ex.: `estadual_municipal`, `nao_sei`).
