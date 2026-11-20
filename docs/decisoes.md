# Registro de decisões

Decisões de projeto do Gravidade Social, em ordem cronológica. Cada decisão traz o contexto, a escolha e as consequências.

| Nº   | Data       | Decisão                                               | Status |
| ---- | ---------- | ----------------------------------------------------- | ------ |
| D001 | 2026-11-18 | Convenção de nomes das variáveis                      | Aceita |
| D002 | 2026-11-18 | Escopo da análise por período                         | Aceita |
| D003 | 2026-11-18 | Renomeação e filtro de MG na ingestão                 | Aceita |
| D004 | 2026-11-19 | Escolas mascaradas e recorte das análises por escola  | Aceita |
| D005 | 2026-11-20 | Tratamento de nulos e não resposta                    | Aceita |
| D006 | 2026-11-20 | Recodificação das variáveis socioeconômicas e da rede | Aceita |
| D007 | 2026-11-20 | Recorte de UF e regras de presença                    | Aceita |

## D001 — Convenção de nomes das variáveis

**Data:** 2026-11-18

**Status:** Aceita

**Atualizações:**

- 2026-11-18: inclusão do prefixo `param_` para os itens da prova (`docs/harmonizacao_itens.csv`).

### Contexto

Os microdados do ENEM usam códigos do INEP (ex.: `Q006`, `TP_ESCOLA`) que nem sempre são autoexplicativos e podem mudar entre os anos. O projeto precisa de nomes padronizados para as tabelas limpas, o SQL, os notebooks e o app.

### Decisão

- Idioma dos nomes de variáveis: **português**
- Formato: snake_case, sem acentos e sem espaços
- O nome descreve o conceito, e não o ano nem o código original

**Prefixos**

| Prefixo     | Uso                                         | Exemplo                                   |
| ----------- | ------------------------------------------- | ----------------------------------------- |
| `nota_`     | notas das provas e da redação               | `nota_cn`, `nota_redacao_c1`              |
| `presenca_` | presença em cada prova                      | `presenca_cn`                             |
| `codigo_`   | códigos numéricos (municípios, UFs, provas) | `codigo_municipio_escola`                 |
| `nome_`     | nomes por extenso                           | `nome_municipio_prova`                    |
| `sigla_`    | siglas                                      | `sigla_estado_escola`                     |
| `tipo_`     | variáveis categóricas de classificação      | `tipo_adm_escola`                         |
| `faixa_`    | categorias ordenadas por intervalo          | `faixa_renda`, `faixa_etaria`             |
| `qtd_`      | quantidades                                 | `qtd_computadores`                        |
| `tem_`      | variáveis sim/não sobre posse ou acesso     | `tem_internet`                            |
| `vetor_`    | cadeias de caracteres questão a questão     | `vetor_respostas_cn`, `vetor_gabarito_cn` |
| `param_`    | parâmetros do modelo da TRI de cada item    | `param_a`, `param_b`, `param_c`           |

**Sufixos de área** (siglas oficiais do INEP)

| Sufixo | Área                 |
| ------ | -------------------- |
| `_cn`  | Ciências da Natureza |
| `_ch`  | Ciências Humanas     |
| `_lc`  | Linguagens e Códigos |
| `_mt`  | Matemática           |

As competências da redação usam `_c1` a `_c5` (ex.: `nota_redacao_c3`).

**Exceções**

- Condições do participante que são indicadoras sim/não no INEP (`IN_`) usam só o nome da condição, sem prefixo (ex. `treineiro`).
- Variáveis de contexto sem categoria natural mantêm o nome do conceito (ex.: `ano`, `sexo`, `cor_raca`, `numero_inscricao`).
- Variáveis categórias cujo conceito já é autoexplicativo mantêm o nome do conceito, sem prefixo (ex.: `escolaridade_mae`, `situacao_conclusao`, `frequencia_empregado_domestico`).

### Alternativas consideradas

- **Manter os nomes originais do INEP:** descartado porque os códigos não são legíveis e mudam entre os anos.
- **Nomes em inglês:** descartado porque o público alvo desse projeto são falantes de português.
- **Nomes de área por extenso** (ex.: `nota_ciencias_natureza`): descartado porque deixava as consultas SQL longas demais; as siglas do INEP já são conhecidas por quem trabalha com o ENEM.

### Consequências

- O mapeamento nome original → nome padronizado fica em `docs/harmonizacao.csv`, e só as variáveis com `usar = sim` entram na ingestão.
- O código (funções, scripts) e as mensagens de commit seguem em inglês; apenas os nomes das variáveis estão em português.
- Novas variáveis devem seguir esta tabela de prefixos. Um prefixo novo exige atualizar esta decisão.

## D002 — Escopo da análise por período

**Data:** 2026-11-18

**Status:** Aceita

**Atualizações:**

- 2026-11-19: o mascaramento de `CO_ESCOLA` foi verificado nos dados. O código não é apagado, e sim substituído por uma máscara, e as demais colunas da escola continuam reais. Ajustados o contexto e a consequência sobre escolas pequenas.

### Contexto

A partir de 2024, o INEP divide os microdados do ENEM em duas tabelas:

- `PARTICIPANTES`: perfil, questionário socioeconômico `IN_TREINEIRO` e `TP_ST_CONCLUSAO`;
- `RESULTADOS`: escola, presença, notas, respostas e gabaritos.

`PARTICIPANTES` é identificada por `NU_INSCRICAO`, e `RESULTADOS` por `NU_SEQUENCIAL`. O dicionário de 2024 afirma que não é possível usar uma para relacionar as duas bases. Em 2024–2025, portanto, não há como ligar a nota de um participante ao seu perfil socioeconômico. As duas tabelas só têm em comum o ano e o município e a UF da prova.

Ao mesmo tempo, `RESULTADOS` passou a trazer `CO_ESCOLA` (vindo do Censo Escolar), que não existe em 2020–2023. Segundo o dicionário de 2024, o código real é substituído por uma máscara quando a escola tem menos de 10 participantes na edição do exame. Nos dados, as máscaras seguem o formato `600xxxxx`, enquanto os códigos reais começam com o código da UF no IBGE (`31` para MG).

| Análise                                   | 2020–2023 | 2024–2025                |
| ----------------------------------------- | --------- | ------------------------ |
| Nota × renda, escolaridade dos pais, bens | sim       | não                      |
| Nota × rede, município e localização      | sim       | sim (via `RESULTADOS`)   |
| Abstenção × perfil socioeconômico         | sim       | não; só rede e município |
| Desempenho por questão e por rede         | sim       | sim                      |
| Nota por escola (`CO_ESCOLA`)             | não       | sim                      |

### Decisão

- **Análise individual** (nota ou abstenção × perfil socioeconômico): só em **2020–2023**. O índice de bens também fica restrito a esse período.
- **Análise agregada** por escola, município e rede (`tipo_adm_escola`): em **2020–2025**, a partir das variáveis de resultado (base única em 2020–2023; `RESULTADOS` em 2024–2025).
- **Nota por escola e cruzamento com o Censo Escolar**: só em **2024–2025**, via `codigo_escola`.
- **População das análises agregadas**: participantes com a escola preenchida. Em 2020–2023, nos quatro anos, escola preenchida só ocorre com `situacao_conclusao = 2` (conclui no ano) e `treineiro = 0`. Aplicando a mesma regra em `RESULTADOS` de 2024–2025, os treineiros ficam de fora sem precisar de `IN_TREINEIRO`. Em 2024–2025 isso não pode ser verificado diretamente, porque as tabelas não se ligam. O dicionário, porém, diz que a escola vem só de matrículas em etapas de prováveis concluintes, o que é consistente com a regra.
- **População da análise individual** (2020–2023): todos os concluintes no ano (`situacao_conclusao = 2` e `treineiro = 0`), com ou sem escola preenchida.
- Sobre essas populações, cada análise aplica seus próprios filtros de presença (ex.: presentes em CN para as notas de CN; presentes no 1º dia para a abstenção).
- Em 2024–2025, `PARTICIPANTES` serve só para descrever o perfil dos inscritos, sem ligação com as notas.

### Alternativas consideradas

- **Análise individual em 2020–2025:** descartada porque as tabelas de 2024–2025 não se ligam.
- **Ligar as tabelas por município e ano da prova:** descartada para análise individual porque só produz relações agregadas. Fica disponível como análise ecológica, interpretada como tal.
- **Descartar 2024–2025:** descartada porque perderia a série por rede e município e o cruzamento por escola com o Censo Escolar.

### Consequências

- **Quebra de série entre 2023 e 2024.** Em 2020–2023, só 65–72% dos concluintes no ano têm escola preenchida; em 2024–2025, cerca de 97% (Brasil: 1,57 de 1,62 milhão em 2024; 1,74 de 1,81 milhão em 2025), porque a escola passou a vir do Censo Escolar pelo CPF. A população "com escola" de 2024–2025 é mais ampla, e os concluintes que antes ficavam sem escola provavelmente não são aleatórios. Comparações entre os dois períodos precisam mencionar essa mudança.
- **Duas populações em 2020–2023.** A análise individual usa todos os concluintes no ano; a agregada, só os 65–72% com escola preenchida. Os números de uma e de outra não batem exatamente nos mesmos anos, e a diferença vem desse recorte.
- **Escolas pequenas ficam de fora das análises por escola.** Escolas com menos de 10 participantes têm o código substituído por uma máscara (`600xxxxx`), que não se liga ao Censo Escolar. Em MG, são 565 escolas em 2024 e 489 em 2025. Os alunos dessas escolas continuam nas análises por município, rede e localização, porque essas colunas não são mascaradas. A perda tende a afetar mais as escolas rurais e do interior.
- **As máscaras não se repetem entre os anos.** Não é possível acompanhar a mesma escola mascarada de 2024 para 2025.
- **`tipo_adm_escola` não substitui `TP_ESCOLA` um para um.** A primeira vem do cadastro da escola e só existe para quem tem escola preenchida; a segunda era declarada pelo participante.
- **Variáveis do questionário mantêm a escala de 2020–2023.** Itens que viraram sim/não em 2024 (freezer, lavadora, micro-ondas) seguem como `qtd_` e são usados em 2024–2025 só para descrição.
- O mapeamento e essas ressalvas ficam registrados em `docs/harmonizacao.csv`.

## D003 — Renomeação e filtro de MG na ingestão

**Data:** 2026-11-18

**Status:** Aceita

### Contexto

A ingestão converte os CSVs brutos do INEP em Parquet (ver `docs/spec-ingestao.md`). Duas escolhas afetam todas as etapas seguintes: em que momento os nomes do INEP viram os nomes padronizados da D001, e quais participantes contam como "de Minas Gerais".

Sobre os nomes: os códigos do questionário mudam de posição em 2024. `Q006`, por exemplo, é a renda familiar até 2023 e a renda própria do participante a partir de 2024. Com os nomes originais, o mesmo código teria significados diferentes conforme o ano.

Sobre o filtro: cada participante tem duas UFs, a da prova (`SG_UF_PROVA`) e a da escola (`SG_UF_ESC`). A da escola só existe para quem tem escola preenchida (ver D002), e a tabela `PARTICIPANTES` de 2024–2025 só tem a da prova.

### Decisão

- **Renomear na ingestão.** Os Parquets já saem com os nomes padronizados da D001.
- **A harmonização é a fonte da verdade.** O script lê `docs/harmonizacao.csv` (linhas com `usar = sim`) para saber quais colunas ler em cada ano e como renomeá-las. Nenhuma lista de colunas fica escrita no código.
- **Filtro de MG amplo:** entram os participantes com a prova **ou** a escola em MG. Na tabela `PARTICIPANTES` de 2024–2025, entra quem fez a prova em MG.
- **Qual UF define cada análise** é decidido na Etapa 2, sobre esse conjunto amplo.

### Alternativas consideradas

- **Manter os nomes do INEP nos Parquets e renomear na Etapa 2:** descartada porque o mesmo código teria significados diferentes em anos diferentes dentro dos arquivos processados.
- **Lista de colunas escrita no script:** descartada porque duplicaria a harmonização, e as duas poderiam divergir.
- **Filtrar só pela UF da prova:** descartada porque perderia estudantes de escolas mineiras que fizeram a prova em outro estado.
- **Filtrar só pela UF da escola:** descartada porque perderia os concluintes sem escola preenchida (28–35% em 2020–2023), que fazem parte da população da análise individual (D002).

### Consequências

- Qualquer mudança de variável (incluir, excluir, corrigir um nome) é feita na `harmonizacao.csv`; depois basta rodar a ingestão de novo.
- Se uma coluna prevista na harmonização não existir no CSV de algum ano, a ingestão para com erro. A divergência precisa ser corrigida na harmonização antes de seguir.
- Os Parquets não guardam os nomes originais do INEP. Para rastrear uma coluna até a fonte, consulta-se a harmonização.
- Os Parquets contêm um conjunto maior que o de qualquer análise isolada, e a Etapa 2 sempre precisa aplicar o recorte de UF.

## D004 — Escolas mascaradas e recorte das análises por escola

**Data:** 2026-11-19

**Status:** Aceita

**Atualizações:**

- 2026-11-20: "presentes em CN" passa a significar "com nota em CN"
  (`tem_nota_cn`), conforme a distinção entre comparecimento e nota
  da D007.

### Contexto

Em 2024-2025, escolas com menos de 10 participantes no exame têm o `CO_ESCOLA` substituído por uma máscara no formato `600xxxxx`, que não se liga ao Censo Escolar (ver D002). As demais colunas da escola continuam reais.

Além disso, a tabela `RESULTADOS` filtrada para MG (D003) contém escolas de outros estados com poucos alunos, aqueles que fizeram a prova em MG. Em 2024, 242 das 263 escolas de fora de MG têm pelo menos 10 participantes na base.

Mesmo entre escolas com código real, o número de presentes em CN pode ser pequeno por causa da abstenção.

### Decisão

- **Coluna `escola_mascarada`** criada na limpeza: verdadeira quando `código_escola` começa com `6`; nula quando não há escola.
- **Análises por escola e cruzamento com o Censo** usam só escolas:
  - Mineiras (`sigla_estado_escola = 'MG'`);
  - não mascaradas (`escola_mascarada = false`);
  - com pelo menos **10 presentes em CN** no ano.
- **Análises por município, rede e localização** mantêm os alunos de escola mascaradas, porque essas colunas não são afetadas.

### Alternativas consideradas

- **Descartar participantes de escolas mascaradas em todas as análises:** descartada porque perderia alunos de escolas pequenas nas análises em que eles podem ser usados.
- **Incluir escolas de fora de MG nas análises por escola:** descartada porque essas escolas aparecem incompletas na base.
- **Nenhum mínimo além da regra do INEP:** descartada porque a regra conta inscritos, e médias calculadas com 5 a 7 notas podem ser instáveis para comparar escolas.
- **Mínimo de 30 presentes em CN**: descartada porque excluiria muitas escolas pequenas, que já são sub-representadas pelo mascaramento.

### Consequências

- O número de escolas analisadas é menor que o total de escolas mineiras na base; o tamanho do corte é registrado na Etapa 2.
- Médias por escola ficam mais estáveis, ao custo de excluir as menores escolas.
- O mínimo de 10 presentes é o mesmo usado para suprimir grupos no app, mantendo um único critério de tamanho mínimo no projeto.

## D005 — Tratamento de nulos e não respostas

**Data:** 2026-11-20

**Status:** Aceita

### Contexto

A ingestão revelou três situações de dados ausentes ou de não resposta, investigadas em `notebooks/00_pendencias.ipynb`:

1. **`item_adaptado` em 2021:** 990 dos 1.305 itens de CN estão nulos. Em 2021 não existe nenhum valor `0`, enquanto nos demais anos a coluna só tem `0` e `1`. Os 315 itens com `1` correspondem a 7 cadernos, a mesma quantidade de 2020, e os 990 nulos, a 22 cadernos.
2. **Questionário socioeconômico em 2020:** 1,5% de nulos em 2020 e nenhum de 2021 em diante. As categorias são as mesmas em todos os anos, então a resposta não virou categoria. Não foi encotnrada nenhuma informação que possibilite afirmar que o questionário passou a ser obrigatório a partir de 2021 nos documentos oficiais do INEP obtidos junto com os dados. Entre os concluíntes de 2020 (`situacao_conclusao = 2`, `treineiro = 0`), 1.548 de 125.998 (1,23%) não responderam. Esse grupo tem presença menor no 2° dia (42,4% contra 61,9%) e média em CN menor (492,7 contra 505,2).
3. **"Não sei" nas perguntas sobre os pais:** a escolaridade (`H`) e a ocupação (`F`) do pai e da mãe têm a opção "Não sei", que não é um nível das escalas. O volume é relevante, sobretudo para o pai (em 2020, 45.022 "Não sei" na escolaridade do pai contra 12.672 no da mãe).

### Decisão

- **`item_adaptado` em 2021**: nulo é convertido em `0` (não adaptado), só nesse ano.
- **Concluíntes de 2020 sem questionário:** excluídos das análises que usam variáveis do questionário. Continuam nas análises que não dependem dele.
- **"Não sei" na escolaridade e ocupação dos pais:** tratado como categoria própria, separada dos níveis da escala. Nos modelos, entra como um grupo à parte, e não como um ponto da escala ordinal.
- **Faixa de renda `A`** ("Nenhuma renda") é um nível válido da escala, e não uma resposta.

### Alternativas consideradas

- **Imputar renda e escolaridade dos concluíntes de 2020 sem questionário:** descartada porque não há informação para uma imputação razoável, e o grupo é pequeno.

- **"Não sei" como ausente (excluir dos modelos)**: descartada porque removeria de 5% a 10% dos participantes no caso do pai, e justamente um grupo que pode ser socialmente diferente e representar uma realidade comum no brasil.
- **Imputar um nível de escolaridade para o "Não sei":** descartada porque não há base para estiver o nível, e a imputação esconderia um possível sinal relevante.

### Consequências

- Excluir os concluíntes de 2020 sem questionário muda a média de CN de 2020 em só 0,1 ponto (505,2 para 505,1).
- A abstenção dos concluíntes de 2020 na análise individual fica levemente subestimada, porque o grupo excluído falta mais.
- Os modelos que usam a escolaridade dos pais terão uma categoria "Não sei" com coeficiente próprio, que precisa ser interpretado separadamente.
- A recodificação das escalas (como agrupar os níveis de escolaridade e as faixas de renda) é uma decisão à parte, registrada em seguida.

## D006 — Recodificação das variáveis socioeconômicas e da rede

**Data: 2026-11-20**

**Status:** Aceita

**Atualizações:**

- 2026-11-20: definidos os limites exatos de `faixa_renda_per_capita`: até 1/2 SM inclusive (`ate_meio_sm`, incluindo renda zero); acima de 1/2 até 1 SM (`meio_a_1_sm`); acima de 1 até 2 SM (`1_a_2_sm`); acima de 2 SM (`acima_2_sm`). O limite "até 1/2 SM inclusive" segue o critério de baixa renda do Cadastro Único.
- 2026-11-20: `escolaridade_max_pais` é representada por duas colunas, como pai e mãe: `escolaridade_max_pais_cat` (texto, com `nao_sei`) e `escolaridade_max_pais_nivel` (1 a 4, nulo para `nao_sei`).
- 2026-11-20: `tipo_escola = '4'` (exterior, presente só no dicionário de 2020) é tratado como nulo; não ocorre nos dados.

### Contexto

As variáveis do questionário e da escola vêm em categorias detalhadas (letras INEP), algumas com poucos participantes e nem todas com uma ordem natural. Para os modelos e para o app, é preciso definir escalas estáveis entre os anos. As categorias de "Não sei" já foram tratadas na D005.

### Decisão

**Escolaridade do pai e da mãe:** quatro níveis ordinais e uma categoria à parte.

| Nível | Letras  | Rótulo                 |
| ----- | ------- | ---------------------- |
| 1     | A, B, C | fundamental incompleto |
| 2     | D       | fundamental completo   |
| 3     | E       | médio completo         |
| 4     | F, G    | superior completo      |
| —     | H       | não sei (D005)         |

**`escolaridade_max_pais`**: a maiore escolaridade entre o pai e a mãe. Quando só um é conhecido, usa-se a dele(a); é "não sei" apenas quando os dois são desconhecidos.

**Ocupação do pai e da mãe**: mantidos os cinco grupos do INEP (A a E) e o "não sei" (F), tratados como **categorias nominais, sem ordem**.

**Renda**: claculada per capita, em salários mínimos (SM).

    renda_per_capita = ponto médio da faixa (em SM) / qtd_moradores

| Letra | Faixa (SM)    | Ponto médio |
| ----- | ------------- | ----------- |
| A     | nenhuma renda | 0           |
| B     | até 1         | 0,5         |
| C     | 1 a 1,5       | 1,25        |
| D     | 1,5 a 2       | 1,75        |
| E     | 2 a 2,5       | 2,25        |
| F     | 2,5 a 3       | 2,75        |
| G     | 3 a 4         | 3,5         |
| H     | 4 a 5         | 4,5         |
| I     | 5 a 6         | 5,5         |
| J     | 6 a 7         | 6,5         |
| K     | 7 a 8         | 7,5         |
| L     | 8 a 9         | 8,5         |
| M     | 9 a 10        | 9,5         |
| N     | 10 a 12       | 11          |
| O     | 12 a 15       | 13,5        |
| P     | 15 a 20       | 17,5        |
| Q     | acima de 20   | 25          |

Para descrição e para o app, `faixa_renda_per_capita` em quatro faixas:

| Faixa | Renda per capita |
| ----- | ---------------- |
| 1     | até 1/2 SM       |
| 2     | de 1/2 a 1 SM    |
| 3     | de 1 a 2 SM      |
| 4     | acima de 2 SM    |

**Rede da escola (`tipo_adm_escola`)**: três grupos.

| Grupo                      | Categorias originais |
| -------------------------- | -------------------- |
| federal                    | federal              |
| pública estadual/municipal | estadual, municipal  |
| privada                    | privada              |

**Tipo de escola declarado (`tipo_escola`):** a categoria `1` ("Não respondeu") é tratada como ausente. Entre os concluíntes do ano, ela quase não ocorre (nenhum caso em 2020 e 2022, 2 em 2021 e 1 em 2023).

### Alternativas consideradas

- **Manter os sete níveis de escolaridade:** descartada porque alguns níveis, como "nunca estudou", têm poucos participantes e médias instáveis, e quatro níveis seguem os marcos do sistema educacional.
- **Ordenar a ocupação por status e criar `ocupacao_max_pais`**: descartada porque a ordenação dos grupos por status social é subjetiva; como categorias nominais, os modelos mostram se há um gradiante sem impô-lo.
- **Usar a renda familiar, sem dividir pelos membros moradores:** descartada porque a mesma renda representa condições muito diferentes conforme o tamanho da família.
- **Corrigir a renda pela inflação em reais:** desnecessário, porque as faixas já são definidas em salários mínimos do ano.
- **Manter a rede municipal separada:** descartada porque a rede municipal oferece pouco ensino médio em MG.
- **Juntar as redes federal à estadual:** descartada porque a rede federal (CEFETs e Institutos Federais) tem perfil muito diferente, e misturá-las esconderia esse contraste.

### Consequências

- O ponto médio da faixa Q (25 SM) é uma convenção. ele afeta poucos participanetes e, por isso, pouco as médias.
- A renda per capta é uma aproximação: usa o ponto médio da faixa e o número de moradores de clarado.
- O corte de 1/2 SM per capita coincide com a referência de baixa renda do Cadastro Único, o que facilita a comunicação dos resultados.
- A escolaridade dos pais pode entrar nos modelos como escala ordinal (níveis de 1 a 4) ou como categorias; a escolha fica para a etapa 4.

## D007 — Recorte de UF e regras de presença

**Data:** 2026-11-20

**Status:** Aceita

### Contexto

A especificação do modelo SQL (`docs/spec-sql.md`) deixou três definições em aberto: qual UF define a população da análise individual (a D003 adiou essa escolha para a Etapa 2), como tratar participantes eliminados e o que conta como presença no 1º dia.

Entre os concluintes do ano (2020–2023), a combinação de UF da escola e UF da prova é:

| Ano  | Escola MG, prova MG | Escola MG, prova fora | Escola fora, prova MG | Sem escola, prova MG |
| ---- | ------------------- | --------------------- | --------------------- | -------------------- |
| 2020 | 70.875              | 739                   | 641                   | 53.743               |
| 2021 | 63.409              | 827                   | 818                   | 32.119               |
| 2022 | 68.046              | 823                   | 623                   | 31.536               |
| 2023 | 66.261              | 711                   | 611                   | 42.599               |

Na presença do 2º dia (CN), os eliminados são poucos: 44 em 2020, 51 em 2021, 50 em 2022 e 76 em 2023. No 1º dia, as presenças em LC e em CH são idênticas para todos os concluintes de 2020–2023 (105.063 faltaram às duas, 328.780 estiveram presentes nas duas e 538 foram eliminados nas duas): a presença é registrada por sessão.

### Decisão

- **UF da análise individual:** vale a UF da escola quando ela existir; senão, a UF da prova. Entram os concluintes de escola mineira (mesmo que tenham feito a prova fora) e os concluintes sem escola que fizeram a prova em MG. Ficam de fora os de escola de outro estado.
- **Eliminados:** contam como presentes no cálculo da abstenção, porque compareceram; ficam fora das análises de nota, porque não têm nota.
- **Presente no 1º dia:** presente ou eliminado em LC **ou** em CH.

### Alternativas consideradas

- **Só a UF da prova:** descartada porque incluiria alunos de escolas de outros estados e excluiria alunos de escolas mineiras que fizeram a prova fora.
- **Prova ou escola em MG:** descartada porque incluiria alunos de escolas de outros estados.
- **Eliminados como ausentes:** descartada porque misturaria dois fenômenos diferentes, não comparecer e ser eliminado, enquanto a Q4 trata do comparecimento.
- **Presença em LC e em CH:** equivalente nos dados, mas a regra com "ou" é mais robusta caso um ano futuro registre as provas separadamente.

### Consequências

- A população da análise individual tem 125.357 concluintes em 2020, 96.355 em 2021, 100.405 em 2022 e 109.571 em 2023.
- O critério é coerente com o da análise agregada, que também usa a escola em MG.
- Os casos de fronteira (escola e prova em UFs diferentes) somam cerca de 1% dos concluintes, então a escolha pouco altera os resultados.
- Para os concluintes sem escola preenchida (31% a 43% conforme o ano), a UF da prova é uma aproximação do local onde estudam.
