# Guia de Commits Semânticos

> Padrão de mensagens de commit baseado no **Conventional Commits 1.0.0**, adaptado para projetos de **Ciência de Dados** e **Desenvolvimento Web** (apps e sites).
> Todas as mensagens de commit são escritas em **inglês**.

---

## Sumário

1. [Por que usar commits semânticos](#1-por-que-usar-commits-semânticos)
2. [Estrutura de uma mensagem](#2-estrutura-de-uma-mensagem)
3. [Tipos (types)](#3-tipos-types)
4. [Escopos (scopes)](#4-escopos-scopes)
5. [Regras de escrita](#5-regras-de-escrita)
6. [Corpo e rodapé](#6-corpo-e-rodapé)
7. [Breaking changes](#7-breaking-changes)
8. [O primeiro commit](#8-o-primeiro-commit)
9. [Exemplos — Ciência de Dados](#9-exemplos--ciência-de-dados)
10. [Exemplos — Desenvolvimento Web](#10-exemplos--desenvolvimento-web)
11. [Exemplos — Situações gerais](#11-exemplos--situações-gerais)
12. [Boas práticas e anti-padrões](#12-boas-práticas-e-anti-padrões)
13. [Ferramentas de apoio](#13-ferramentas-de-apoio)
14. [Cola rápida](#14-cola-rápida)

---

## 1. Por que usar commits semânticos

- **Histórico legível**: qualquer pessoa entende o que mudou só lendo o `git log`.
- **Changelogs automáticos**: ferramentas geram notas de versão a partir dos commits.
- **Versionamento semântico (SemVer)**: `feat` → versão *minor*, `fix` → *patch*, breaking change → *major*.
- **Revisão de código mais fácil**: commits pequenos e bem nomeados são mais simples de revisar e reverter.
- **Portfólio profissional**: recrutadores e colegas que olham seu GitHub percebem organização e maturidade.

---

## 2. Estrutura de uma mensagem

```
<type>(<scope>): <subject>

[optional body]

[optional footer(s)]
```

| Parte     | Obrigatória | Descrição                                                      |
|-----------|-------------|----------------------------------------------------------------|
| `type`    | Sim         | Categoria da mudança (`feat`, `fix`, `docs`...).               |
| `scope`   | Não         | Parte do projeto afetada (`api`, `navbar`, `etl`...).          |
| `subject` | Sim         | Resumo curto e imperativo do que o commit faz.                 |
| `body`    | Não         | Explicação do **porquê** e do **como**, quando necessário.     |
| `footer`  | Não         | Referências a issues, breaking changes, coautores.             |

**Exemplo completo:**

```
feat(dashboard): add monthly revenue chart

Add a line chart showing revenue aggregated by month using Recharts.
Data is fetched from the /api/revenue endpoint and cached for 5 minutes.

Closes #42
```

---

## 3. Tipos (types)

### 3.1 Tipos padrão

| Tipo       | Quando usar                                                                 | Exemplo                                          |
|------------|-----------------------------------------------------------------------------|--------------------------------------------------|
| `feat`     | Nova funcionalidade para o usuário/projeto.                                 | `feat: add dark mode toggle`                     |
| `fix`      | Correção de bug.                                                            | `fix: prevent crash when dataset is empty`       |
| `docs`     | Apenas documentação (README, docstrings, comentários).                      | `docs: add setup instructions to README`         |
| `style`    | Formatação que **não altera** a lógica (espaços, ponto e vírgula, lint).    | `style: format code with black`                  |
| `refactor` | Reestruturação de código sem mudar comportamento nem corrigir bug.          | `refactor: extract data loading into function`   |
| `perf`     | Melhoria de desempenho.                                                     | `perf: vectorize feature computation with numpy` |
| `test`     | Adição ou correção de testes.                                               | `test: add unit tests for cleaning functions`    |
| `build`    | Sistema de build ou dependências (npm, pip, Vite, Docker).                  | `build: upgrade vite to v6`                      |
| `ci`       | Configuração de integração contínua (GitHub Actions etc.).                  | `ci: add workflow to run pytest on push`         |
| `chore`    | Tarefas de manutenção que não afetam código-fonte nem testes.               | `chore: update .gitignore`                       |
| `revert`   | Reverte um commit anterior.                                                 | `revert: feat: add dark mode toggle`             |

### 3.2 Tipos extras úteis para Ciência de Dados

O Conventional Commits permite tipos personalizados. Estes são opcionais, mas deixam o histórico de projetos de dados mais expressivo. **Escolha um conjunto e mantenha a consistência no projeto.**

| Tipo       | Quando usar                                                          | Exemplo                                             |
|------------|----------------------------------------------------------------------|-----------------------------------------------------|
| `data`     | Adição, atualização ou remoção de datasets (ou de seus metadados).   | `data: add 2025 student performance dataset`        |
| `eda`      | Análise exploratória (notebooks, gráficos exploratórios).            | `eda: explore grade distribution by class`          |
| `model`    | Treino, ajuste ou troca de modelos.                                  | `model: train random forest baseline`               |
| `exp`      | Experimentos (testes de hipóteses, comparações de modelos).          | `exp: compare XGBoost vs LightGBM on validation`    |
| `report`   | Relatórios, visualizações finais, apresentações de resultados.       | `report: add final analysis summary notebook`       |

> 💡 **Alternativa conservadora:** se preferir ficar só nos tipos padrão, use `feat` com escopo — ex.: `feat(model): train random forest baseline`, `feat(eda): explore grade distribution`.

---

## 4. Escopos (scopes)

O escopo indica **onde** a mudança aconteceu. Use substantivos curtos, em minúsculas, sem espaços (use `-` se precisar).

### Sugestões para projetos de dados

`data`, `etl`, `cleaning`, `features`, `eda`, `model`, `training`, `evaluation`, `viz`, `notebook`, `pipeline`, `config`, `api`, `deps`

### Sugestões para projetos web

`ui`, `layout`, `navbar`, `footer`, `hero`, `auth`, `api`, `router`, `hooks`, `store`, `theme`, `styles`, `seo`, `a11y`, `i18n`, `assets`, `deps`, `config`

### Dica

- Defina os escopos do projeto no README ou em um `CONTRIBUTING.md`.
- Se a mudança afeta várias partes sem um foco claro, **omita o escopo**.

---

## 5. Regras de escrita

1. **Use o modo imperativo**: escreva como se completasse a frase *"If applied, this commit will..."*
   - ✅ `add login form` · ❌ `added login form` · ❌ `adds login form`
2. **Primeira letra minúscula** no subject (convenção mais comum): `feat: add search bar`.
3. **Sem ponto final** no subject.
4. **Até ~50 caracteres** no subject (máximo 72).
5. **Linha em branco** entre subject e body.
6. **Body com quebra de linha em ~72 caracteres.**
7. **Um commit = uma mudança lógica.** Se precisou de "and" no subject, talvez sejam dois commits.
8. **Seja específico**: `fix: handle null values in age column` é melhor que `fix: bug fix`.

### Verbos úteis em inglês

| Verbo        | Uso                                        |
|--------------|--------------------------------------------|
| `add`        | Adicionar algo novo                        |
| `remove`     | Remover algo                               |
| `update`     | Atualizar algo existente                   |
| `fix`        | Corrigir                                   |
| `rename`     | Renomear                                   |
| `move`       | Mover arquivos/código                      |
| `replace`    | Substituir uma coisa por outra             |
| `extract`    | Extrair código para função/módulo          |
| `implement`  | Implementar uma lógica/funcionalidade      |
| `improve`    | Melhorar algo existente                    |
| `simplify`   | Simplificar                                |
| `handle`     | Tratar um caso (erros, valores nulos...)   |
| `prevent`    | Evitar um problema                         |
| `bump`       | Subir versão de dependência                |
| `configure`  | Configurar                                 |
| `integrate`  | Integrar com serviço/biblioteca            |
| `optimize`   | Otimizar                                   |
| `document`   | Documentar                                 |

---

## 6. Corpo e rodapé

### Quando escrever um body

- A mudança não é óbvia pelo subject.
- Você quer explicar **por que** escolheu uma abordagem.
- Há efeitos colaterais, limitações ou decisões técnicas relevantes.

### Rodapés comuns

| Rodapé                 | Significado                                    |
|------------------------|------------------------------------------------|
| `Closes #12`           | Fecha a issue #12 ao fazer merge.              |
| `Fixes #12`            | Igual ao anterior, para bugs.                  |
| `Refs #12`             | Referencia a issue sem fechá-la.               |
| `BREAKING CHANGE: ...` | Descreve mudança incompatível.                 |
| `Co-authored-by: Nome <email>` | Credita coautores.                     |

**Exemplo:**

```
fix(cleaning): handle missing values in attendance column

Students transferred mid-year had empty attendance records, which
caused the average calculation to return NaN for the whole class.
Missing values are now filled with 0 and flagged in a new
`is_transferred` column.

Fixes #18
```

---

## 7. Breaking changes

Uma *breaking change* é uma mudança que quebra compatibilidade (ex.: renomear uma coluna que outros scripts usam, mudar a assinatura de uma função, alterar uma rota de API).

Duas formas de sinalizar:

**a) Com `!` depois do tipo/escopo:**

```
feat(api)!: change /students endpoint response format
```

**b) Com rodapé `BREAKING CHANGE:`:**

```
refactor(data): rename grade columns to snake_case

BREAKING CHANGE: columns `NotaFinal` and `Freq` were renamed to
`final_grade` and `attendance`. Update any downstream scripts.
```

Você pode usar as duas ao mesmo tempo para máxima clareza.

---

## 8. O primeiro commit

O primeiro commit deve ser feito **logo após organizar a estrutura do repositório** (pastas, README, `.gitignore`, licença, arquivos de configuração), **antes** de começar a escrever código de verdade.

### 8.1 Texto padrão (recomendado)

```
chore: initial project setup

Set up the base repository structure, including:
- README with project overview
- .gitignore for the project stack
- LICENSE file
- initial folder structure
- dependency/configuration files
```

### 8.2 Versão curta

```
chore: initial commit
```

### 8.3 Versão para projeto de Ciência de Dados

```
chore: initial project setup

Organize the repository following a standard data science layout:
- data/ (raw, interim, processed) with .gitkeep files
- notebooks/ for exploratory analysis
- src/ for reusable Python modules
- reports/figures/ for generated visualizations
- models/ for serialized models
- requirements.txt with base dependencies
- .gitignore excluding data files, virtualenvs and checkpoints
- README with project goals and setup instructions
- LICENSE (MIT)
```

Estrutura de pastas correspondente:

```
project-name/
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
├── notebooks/
├── src/
│   └── __init__.py
├── models/
├── reports/
│   └── figures/
├── tests/
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

### 8.4 Versão para projeto Web (React + Tailwind)

```
chore: initial project setup

Bootstrap the project with Vite, React and Tailwind CSS:
- configure Tailwind and PostCSS
- set up ESLint and Prettier
- create base folder structure (components, pages, hooks, assets)
- add .gitignore for Node projects
- add README with setup and scripts
- add LICENSE (MIT)
```

Estrutura de pastas correspondente:

```
project-name/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .gitignore
├── .prettierrc
├── eslint.config.js
├── index.html
├── LICENSE
├── package.json
├── README.md
├── tailwind.config.js
└── vite.config.js
```

### 8.5 Comandos para o primeiro commit

```bash
git init
git add .
git commit -m "chore: initial project setup" -m "Set up the base repository structure, including README, .gitignore, LICENSE and initial folder structure."
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
```

> 💡 Cada `-m` cria um parágrafo: o primeiro é o subject, o segundo vira o body. Para mensagens longas, rode só `git commit` e escreva no editor.

---

## 9. Exemplos — Ciência de Dados

### 9.1 Dados

```
data: add raw student grades dataset for 2025
data: update attendance data with Q3 records
data: remove duplicated rows from raw export
docs(data): add data dictionary for grades dataset
chore(data): track large CSV files with Git LFS
```

### 9.2 Limpeza e ETL

```
feat(etl): add script to load grades from CSV
feat(cleaning): normalize student names and remove accents
fix(cleaning): handle missing values in attendance column
fix(etl): parse dates with day-first format
refactor(etl): split pipeline into extract, transform and load steps
perf(etl): read CSV in chunks to reduce memory usage
```

### 9.3 Análise exploratória (EDA)

```
eda: explore grade distribution by class
eda: analyze correlation between attendance and final grade
eda: add outlier detection with IQR method
feat(viz): add boxplot of grades by subject
style(notebook): clear outputs and reorder cells
docs(notebook): add markdown explanations to EDA notebook
```

### 9.4 Feature engineering

```
feat(features): add rolling average of grades per student
feat(features): encode categorical variables with one-hot encoding
fix(features): avoid data leakage in target encoding
refactor(features): move feature functions to src/features.py
```

### 9.5 Modelagem

```
model: train logistic regression baseline
model: add random forest classifier for dropout prediction
model: tune hyperparameters with GridSearchCV
exp: compare XGBoost and LightGBM on validation set
fix(model): set random_state for reproducible results
feat(evaluation): add confusion matrix and classification report
feat(model): save trained model with joblib
```

Com body explicando o resultado:

```
model: replace random forest with gradient boosting

Gradient boosting improved validation F1-score from 0.71 to 0.78
with similar training time. Random forest is kept in
notebooks/experiments for reference.

Refs #25
```

### 9.6 Relatórios e visualizações

```
report: add final analysis notebook with key findings
feat(viz): add interactive dashboard with Plotly
fix(viz): correct axis labels on attendance chart
style(viz): apply consistent color palette to all figures
docs: add results summary to README
```

### 9.7 Ambiente e dependências

```
build(deps): add pandas, numpy and scikit-learn
build(deps): pin scikit-learn to 1.5.2
build: add environment.yml for conda
chore: add .ipynb_checkpoints to .gitignore
ci: run pytest and flake8 on pull requests
test: add tests for data cleaning functions
```

---

## 10. Exemplos — Desenvolvimento Web

### 10.1 Interface e componentes

```
feat(navbar): add responsive mobile menu
feat(hero): add hero section with call-to-action button
feat(ui): create reusable Button component
feat(projects): add project cards grid
fix(navbar): close mobile menu after link click
fix(ui): prevent layout shift when images load
refactor(ui): convert Card component to use props spread
```

### 10.2 Estilos (Tailwind/CSS)

```
style: format files with prettier
feat(theme): add dark mode support
feat(theme): define custom color palette in tailwind config
fix(styles): fix text overflow on small screens
refactor(styles): replace custom CSS with Tailwind utilities
```

> ⚠️ **Atenção:** `style` é para formatação de código, **não** para mudanças visuais. Mudou a aparência do site? Use `feat` (novo visual) ou `fix` (visual quebrado).

### 10.3 Rotas, estado e lógica

```
feat(router): add routes for about and projects pages
feat(store): add global state for user preferences
feat(hooks): add useFetch custom hook
fix(router): redirect unknown routes to 404 page
refactor(hooks): simplify useLocalStorage logic
```

### 10.4 API e integrações

```
feat(api): fetch projects from GitHub API
feat(contact): integrate contact form with EmailJS
fix(api): handle rate limit errors from GitHub API
perf(api): cache API responses in localStorage
```

### 10.5 SEO, acessibilidade e performance

```
feat(seo): add meta tags and Open Graph images
feat(a11y): add aria-labels to icon buttons
fix(a11y): improve color contrast on footer links
perf: lazy load project images
perf(build): split vendor bundle to reduce initial load
```

### 10.6 Conteúdo e assets

```
feat(content): add new project to portfolio
docs(content): update about me section
chore(assets): compress images to webp
chore(assets): add favicon and app icons
```

### 10.7 Build, deploy e CI

```
build: configure vite base path for GitHub Pages
build(deps): bump react to 19.1.0
ci: add GitHub Actions workflow to deploy on push to main
ci: run lint and build checks on pull requests
chore: add .env.example file
```

---

## 11. Exemplos — Situações gerais

### Documentação

```
docs: add installation steps to README
docs: add badges for license and tech stack
docs: fix typos in contributing guide
docs: add screenshots to README
```

### Manutenção

```
chore: update .gitignore
chore: remove unused files
chore: rename project folder structure
chore: add editorconfig
```

### Revertendo um commit

```bash
git revert <hash>
```

Mensagem gerada (ajuste se quiser):

```
revert: feat(theme): add dark mode support

This reverts commit 3f2a1bc.
Dark mode caused contrast issues on charts; will be reimplemented later.
```

### Trabalho em andamento (evite no `main`)

```
wip: start implementing login flow
```

> Use `wip` apenas em branches pessoais e reescreva antes do merge (`git rebase -i` ou squash).

### Merge

```
Merge branch 'feat/dark-mode' into main
```

(Mensagens de merge geradas automaticamente geralmente são mantidas como estão.)

### Commit com coautor

```
feat(eda): add analysis of attendance by weekday

Co-authored-by: Jane Doe <jane@example.com>
```

### Hotfix urgente

```
fix!: correct wrong grade calculation formula

The final grade was using simple average instead of weighted
average, affecting all published reports.

BREAKING CHANGE: previously generated reports must be regenerated.
```

### Versão/release

```
chore(release): v1.0.0
```

---

## 12. Boas práticas e anti-padrões

### ✅ Faça

- Commits **pequenos e frequentes**, cada um com uma mudança lógica.
- Revise o que vai commitar com `git diff --staged` antes.
- Use `git add -p` para separar mudanças diferentes em commits diferentes.
- Mantenha **consistência** de tipos e escopos no projeto.
- Em notebooks, **limpe as saídas** antes de commitar (ou use `nbstripout`).
- Nomeie branches no mesmo espírito: `feat/dark-mode`, `fix/nan-attendance`, `docs/readme`.

### ❌ Evite

| Ruim                         | Melhor                                               |
|------------------------------|------------------------------------------------------|
| `update`                     | `docs: update README with deploy instructions`       |
| `fix bug`                    | `fix(etl): handle empty rows in CSV import`          |
| `changes`                    | `refactor(ui): extract Header into its own component`|
| `final version`              | `chore(release): v1.0.0`                             |
| `asdfgh`                     | (qualquer coisa descritiva 😅)                       |
| `feat: Added new feature.`   | `feat: add search filter to projects page`           |
| `fix: fix navbar and add footer and update colors` | Três commits separados         |

### ⚠️ Nunca commite

- Senhas, tokens, chaves de API (`.env`).
- Datasets grandes ou sensíveis (dados pessoais de alunos, por exemplo!).
- `node_modules/`, `venv/`, `__pycache__/`, `.ipynb_checkpoints/`.

---

## 13. Ferramentas de apoio

| Ferramenta                 | Para quê                                                         |
|----------------------------|------------------------------------------------------------------|
| **Commitizen** (`cz`)      | Assistente interativo que monta a mensagem no padrão.            |
| **commitlint**             | Valida mensagens de commit automaticamente.                      |
| **Husky**                  | Executa hooks do Git (ex.: rodar commitlint antes do commit).    |
| **pre-commit** (Python)    | Hooks para projetos Python (black, flake8, nbstripout etc.).     |
| **semantic-release**       | Gera versão e changelog automaticamente a partir dos commits.    |
| **Conventional Commits** (extensão VS Code) | Monta mensagens pelo editor.                    |

### Template de mensagem no Git

Crie um arquivo `~/.gitmessage`:

```
# <type>(<scope>): <subject>   (max 50 chars, imperative, no period)
#
# Body: explain WHAT and WHY (wrap at 72 chars)
#
# Footer: Closes #, Refs #, BREAKING CHANGE:
#
# Types: feat fix docs style refactor perf test build ci chore revert
#        data eda model exp report
```

E configure:

```bash
git config --global commit.template ~/.gitmessage
```

Agora, ao rodar `git commit` (sem `-m`), o editor abre com esse lembrete.

---

## 14. Cola rápida

```
feat:      nova funcionalidade
fix:       correção de bug
docs:      documentação
style:     formatação (sem mudar lógica)
refactor:  reestruturação sem mudar comportamento
perf:      desempenho
test:      testes
build:     build e dependências
ci:        integração contínua
chore:     manutenção geral
revert:    reverter commit

# extras para dados
data:      datasets
eda:       análise exploratória
model:     modelos
exp:       experimentos
report:    relatórios e resultados
```

**Fórmula:** `type(scope): imperative verb + what changed`

**Primeiro commit:** `chore: initial project setup`

---

*Referência: [conventionalcommits.org](https://www.conventionalcommits.org/)*
