# Registro de decisões

Decisões de projeto do Gravidade Social, em ordem cronológica.
Cada decisão traz o contexto, a escolha e as consequências.

| Nº   | Data       | Decisão                          | Status |
| ---- | ---------- | -------------------------------- | ------ |
| D001 | 2026-11-18 | Convenção de nomes das variáveis | Aceita |
| D002 | 2026-11-18 | Escopo da análise por período    | Aceita |

## D001 — Convenção de nomes das variáveis

**Data:** 2026-11-18

**Status:** Aceita

### Contexto

Os microdados do ENEM usam códigos do INEP (ex.: `Q006`, `TP_ESCOLA`)
que nem sempre são autoexplicativos e podem mudar entre os anos.
O projeto precisa de nomes padronizados para as tabelas limpas,
o SQL, os notebooks e o app.

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

### Contexto

A partir de 2024, o INEP divide os microdados do ENEM em duas tabelas:

- `PARTICIPANTES`: perfil, questionário socioeconômico `IN_TREINEIRO` e `TP_ST_CONCLUSAO`;
- `RESULTADOS`: escola, presença, notas, respostas e gabaritos.

`PARTICIPANTES` é identificada por `NU_INSCRICAO`, e `RESULTADOS`
por `NU_SEQUENCIAL`. O dicionário de 2024 afirma que não é possível
usar uma para relacionar as duas bases. Em 2024–2025, portanto,
não há como ligar a nota de um participante ao seu perfil
socioeconômico. As duas tabelas só têm em comum o ano e o município
e a UF da prova.

Ao mesmo tempo, `RESULTADOS` passou a trazer `CO_ESCOLA`
(vindo do Censo Escolar), que não existe em 2020–2023.

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
- **Escolas pequenas ficam de fora do cruzamento com o Censo.** `CO_ESCOLA` vem mascarado quando a escola tem menos de 10 participantes, o que tende a excluir escolas rurais e do interior.
- **`tipo_adm_escola` não substitui `TP_ESCOLA` um para um.** A primeira vem do cadastro da escola e só existe para quem tem escola preenchida; a segunda era declarada pelo participante.
- **Variáveis do questionário mantêm a escala de 2020–2023.** Itens que viraram sim/não em 2024 (freezer, lavadora, micro-ondas) seguem como `qtd_` e são usados em 2024–2025 só para descrição.
- O mapeamento e essas ressalvas ficam registrados em `docs/harmonizacao.csv`.
