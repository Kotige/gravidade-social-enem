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

## Fontes a incluir nas próximas etapas

| Fonte                        | Uso                        | Etapa |
| ---------------------------- | -------------------------- | ----- |
| Malha municipal de MG (IBGE) | mapa coroplético no app    | 06    |
| Censo Escolar (INEP)         | infraestrutura das escolas | 04    |
