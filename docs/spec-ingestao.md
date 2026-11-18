# Especificação da ingestão

Script: `scripts/ingest.py`

Relacionado: `docs/harmonizacao.csv`, D001, D002

### 1. Objetivo

Converter os microdados brutos do ENEM (2020-2025) em arquivos Parquet com apenas os participantes ligados a Minas Gerais e apenas as colunas marcadas com `usar = sim` na harmonização, já com os nomes padronizados.

A ingestão **não** recodifica as categorias, não agrupa faixas e não aplica os filtros de população da D002. Isso será feito posteriormente em uma outra etapa do projeto (SQL).

### 2. Entradas

| Ano       | Arquivo(s)                                       | Tipo de base   |
| --------- | ------------------------------------------------ | -------------- |
| 2020–2023 | `data/raw/<ano>/DADOS/MICRODADOS_ENEM_<ano>.csv` | base única     |
| 2024–2025 | `data/raw/<ano>/DADOS/PARTICIPANTES_<ano>.csv`   | participantes  |
| 2024–2025 | `data/raw/<ano>/DADOS/RESULTADOS_<ano>.csv`      | resultados     |
| 2020–2025 | `data/raw/<ano>/DADOS/ITENS_PROVA_<ano>.csv`     | itens da prova |

- Separador: `;`
- Codificação: latin-1 (confirmar por ano; se os acentos quebrarem, usar `utf-8`)
- Separador decimal nas notas: confirmar no `DESCRIBE` (`.` ou `,`)

Os caminhos ficam num único lugar no início do script (dicionário de configuração), para facilitar ajustes.

### 3. Seleção e renomeação de colunas

- A lista de colunas **não** é escrita à mão no script: ela é lida de `docs/harmonizacao.csv`, usando as linhas com `usar = sim`.
- Para cada ano, o script usa a coluna daquele ano (`2020`, `2021`, ...) como nome original e conceito como nome final.
- Em 2024-2025, cada conceito vai para a tabela indicada em `tabela_2024_2025` (`participantes`, `resultados` ou `ambas`).
- Conceitos com célula vazia num ano são ignorados naquele ano (ex.: `tipo_escola` em 2024-2025).
- É acrescentada a coluna fonte_arquivo com o nome do CSV de origem.

Motivo para renomear já na ingestão: os códigos do questionário mudam de posição em 2024 (ex.: `Q006` é renda até 2023 e renda própria a partir de 2024). Renomear cedo, a partir da harmonização, evita que o mesmo código signifique coisas diferentes nos Parquets.

### 4. Filtro de linhas (Minas Gerais)

| Base                      | Regra                                                         |
| ------------------------- | ------------------------------------------------------------- |
| base única (2020–2023)    | `SG_UF_PROVA = 'MG'` **ou** `SG_UF_ESC = 'MG'`                |
| resultados (2024–2025)    | `SG_UF_PROVA = 'MG'` **ou** `SG_UF_ESC = 'MG'`                |
| participantes (2024–2025) | `SG_UF_PROVA = 'MG'` (única UF disponível na tabela)          |
| itens da prova            | só itens de Ciências da Natureza (confirmar a coluna de área) |

A ingestão guarda o conjunto mais amplo (prova **ou** escola em MG). Qual das duas UFs define a população de cada análise será decidido em etapas futuras do projeto.

### 5. Tipos

Leitura com todas as colunas como texto (`all_varchar`) e conversão explícita na escrita:

| Tipo final | Colunas                                                   |
| ---------- | --------------------------------------------------------- |
| `SMALLINT` | `ano`                                                     |
| `DOUBLE`   | `nota_*`                                                  |
| `VARCHAR`  | todas as demais (códigos, categorias, vetores, inscrição) |

Códigos e categorias ficam como texto para preservar o valor exatamente como o INEP publicou. Notas vazias viram `NULL`, e não zero.

### 6. Saídas

```
data/parquet/
├── base_unica/ano=2020/ … ano=2023/
├── participantes/ano=2024/ ano=2025/
├── resultados/ano=2024/ ano=2025/
└── itens/ano=2020/ … ano=2025/
```

- Formato Parquet com compressão `zstd`, particionado por `ano`.
- Rodar o script de novo sobrescreve a partição do ano (idempotente).
- Uso: `python scripts/ingest.py` (todos os anos) ou `scripts/ingest.py --anos 2023 2024` (só anos indicados).

### 7. Validações

Ao final de cada ano, o script verifica e imprime:

1. Todas as colunas esperadas pela harmonização existem no CSV de origem.
2. Número de linhas lidas (Brasil) e gravadas (MG).
3. Notas `nota_*` entre 0 e 1000 ou `NULL`.
4. `numero_inscricao` sem duplicatas (base única de participantes).
5. Percentual de nulos de cada coluna gravada.

Os resultados são salvos em `docs/ingestao_log.csv` (uma linha por ano e tabela), que é versionado e serve de registro do que foi processado.

### 8. Comportamento em erro

- Coluna esperada ausente no CSV: **o script para**, com uma mensagem dizendo o ano, o arquivo, o conceito e o nome esperado. A harmonização é a fonte da verdade, então uma divergência precisa ser corrigida nela antes de seguir.
- Arquivo de entrada não encontrado: para, com o caminho esperado.
- Validação 3 ou 4 falhou: avisa e segue, registrando no log.

### 9. Fora do escopo

- Recodificação de categorias e agrupamento de faixas (Etapa 2, ainda a vir).
- Filtros de população: concluíntes, treineiros, escola preenchida (Etapa 2, ainda a vir).
- Decodificação das respostas por questão (Etapa 5)
- Qualquer junção entre participantes e resultados (impossível, ver D002).

### 10. Requisitos técnicos

- Python 3 com `duckdb`; a leitura e a escrita são feitas pelo DuckDB (`read_csv` + `COPY ... TO ... (FORMAT parquet, PARTITION_BY ano)`), sem carregar os CSVs inteiros na memória.
- Limite de memória do DuckDB configurável no topo do script.
- Código e comentários em inglês; nomes das colunas em português (D001).
