# Fonte dos dados

Todos os dados brutos deste projeto são públicos e não ficam versionados no repositório (ver `README.md`). Este arquivo registra de onde cada arquivo veio e quando foi baixado.

A integridade dos arquivos pode ser conferida com

```bash
sha256sum -c docs/checksums.txt
```

## Microdados do ENEM (INEP)

**Página oficial:**
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem

| Ano  | Arquivo                  | Baixado em | Formato                              |
| ---- | ------------------------ | ---------- | ------------------------------------ |
| 2020 | microdados_enem_2020.zip | 2026-11-18 | base única                           |
| 2021 | microdados_enem_2021.zip | 2026-11-18 | base única                           |
| 2022 | microdados_enem_2022.zip | 2026-11-18 | base única                           |
| 2023 | microdados_enem_2023.zip | 2026-11-18 | base única                           |
| 2024 | microdados_enem_2024.zip | 2026-11-18 | PARTICIPANTES e RESULTADOS separadas |
| 2025 | microdados_enem_2025.zip | 2026-11-18 | PARTICIPANTES e RESULTADOS separadas |

**Conteúdo de cada ZIP:**

- microdados dos participantes (`DADOS/`)
- itens da prova (`ITENS_PROVA_<ano>.csv`)
- dicionário de dados (cópia em `docs/dicionarios/`)

**Observações**

- Desde 2020 os microdados seguem o modelo adaptado da LGPD, sem o código da escola do participante.
- Em 2024 e 2025 as tabelas dos participantes e de resultados não podem ser ligadas entre si (ver D002 em `docs/decisoes.md`).
- O INEP pode republicar os arquivos com correções. Se um checksum não bater, baixe de novo e registre a nova data aqui.

## Malha municipal de MG (IBGE)

**Página oficial:**
https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html

**Arquivo:**
https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/MG/MG_Municipios_2025.zip

| Versão              | Arquivo                | Baixado em | Publicado no servidor | Formato                          |
| ------------------- | ---------------------- | ---------- | --------------------- | -------------------------------- |
| Malha Municipal 2025 | MG_Municipios_2025.zip | 2026-11-27 | 2026-02-26            | shapefile, SIRGAS 2000 (EPSG:4674) |

Salvo em `data/geo/` (fora do Git).

**Conteúdo do ZIP:** shapefile com os 853 municípios de MG (`CD_MUN`, código IBGE de 7 dígitos, e `NM_MUN`, entre outras colunas) e `LEIA-ME.txt`, que remete à nota metodológica da Malha Municipal na página oficial.

**Versão simplificada:** o IBGE publica a malha de 2025 só em resolução completa (cerca de 2,8 milhões de vértices). `scripts/geo_mg.py` gera `data/geo/mg_municipios_2025.geojson` (cerca de 95 mil vértices, 2,6 MB) com `ST_SimplifyPreserveTopology` do DuckDB, tolerância de 0,002 grau, e as colunas `codigo_municipio` e `nome_municipio`. É esse arquivo que `src/graficos.py` lê. A API de malhas do IBGE (`servicodados.ibge.gov.br/api/v3/malhas`), que já entrega versões simplificadas, só tem malhas até 2022.

**Observações**

- O checksum em `docs/checksums.txt` é o do ZIP original. O GeoJSON é derivado e pode ser refeito com `python scripts/geo_mg.py`.

## Fontes a incluir nas próximas etapas

| Fonte                | Uso                        | Etapa |
| -------------------- | -------------------------- | ----- |
| Censo Escolar (INEP) | infraestrutura das escolas | 04    |
