# Dados

Esta pasta não contém dados versionados. Para obtê-los:

```python3
python scripts/download.py
```

- `zips/`: arquivos originais do INEP (ENEM 2020–2025)
- `raw/`: conteúdo extraído, um diretório por ano (somente leitura)
- `parquet/`: dados processados (MG, colunas selecionadas)
- `geo/`: malha municipal de MG do IBGE e versão simplificada (`python scripts/geo_mg.py`)

Fontes e datas de download: ver `docs/fontes.md`.
