# Registro de decisões

Decisões de projeto do Gravidade Social, em ordem cronológica.
Cada decisão traz o contexto, a escolha e as consequências.

| Nº   | Data       | Decisão                          | Status |
| ---- | ---------- | -------------------------------- | ------ |
| D001 | 2026-11-18 | Convenção de nomes das variáveis | Aceita |

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

- Condições do participante que são indicadoras sim/não no INEP (`IN_`)
  usam só o nome da condição, sem prefixo (ex.: `treineiro`).
- Variáveis de contexto sem categoria natural mantêm o nome do conceito
  (ex.: `ano`, `sexo`, `cor_raca`, `numero_inscricao`).

### Alternativas consideradas

- **Manter os nomes originais do INEP:** descartado porque os códigos
  não são legíveis e mudam entre os anos.
- **Nomes em inglês:** descartado porque [seu motivo].
- **Nomes de área por extenso** (ex.: `nota_ciencias_natureza`):
  descartado porque deixava as consultas SQL longas demais; as siglas
  do INEP já são conhecidas por quem trabalha com o ENEM.

### Consequências

- O mapeamento nome original → nome padronizado fica em
  `docs/harmonizacao.csv`, e só as variáveis com `usar = sim`
  entram na ingestão.
- O código (funções, scripts) e as mensagens de commit seguem em inglês;
  apenas os nomes das variáveis estão em português.
- Novas variáveis devem seguir esta tabela de prefixos. Um prefixo novo
  exige atualizar esta decisão.
