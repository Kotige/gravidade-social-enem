# Registro de decisões

Decisões de projeto do Gravidade Social, em ordem cronológica.
Cada decisão traz o contexto, a escolha e as consequências.

| Nº   | Data       | Decisão                          | Status |
| ---- | ---------- | -------------------------------- | ------ |
| D001 | 2026-11-18 | Convenção de nomes das variáveis | Aceita |

## D001 - Convenção de nomes das variáveis

**Data:** 2026-11-18
**Status:** Aceita

### Contexto

Os microdados do ENEM usam códigos do INEP (ex.: `Q006`, `TP_ESCOLA`) que nem sempre são autoexplicativos e podem mudar entre os anos. O projeto precisa de nomes padronizados para a abt (analytical base table), o SQL, os notebooks e o app.

### Decisão

- Idioma dos nomes de variáveis: **português**
- Formato: snake_case, sem acentos e sem espaços
- Prefixos: `nota_` (notas), `presenca_` (presença), `tem_` (variáveis sim/não)
- Categorias levam o prefixo `faixa_` (ex: `faixa_renda`)
- O nome descreve o conceito, e não o ano e nem o código original

### Alternativas consideradas

- **Manter os nomes originais do INEP**: descartado porque os códigos não são legíveis e mudam entre os anos.
- **inglês**: descartado porque o público alvo do projeto são falantes de português.

### Consequências

- O mapeamento nome original → nome padronizado fica em `docs/harmonizacao.csv`
- O código (funções, scripts) e as mensagens de commit seguem em inglês, independente dos nomes das variáveis.
