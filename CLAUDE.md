# Gravidade Social - Instruções para o Claude Code

## Papéis

- O Claude Code apoia a execução técnica: scripts, SQL, testes, app.
- Perguntas, decisões metodológicas, interpretação e textos são do autor.
  Não escreva conclusões, interpretações de resultados nem textos narrativos (README, relatório, legendas analíticas).
- Implemente a partir das especificações em `docs/`. Se algo não estiver especificado, pergunte em vez de decidir.

## Convenções

- Nomes de variáveis: ver D001 em `docs/decisoes.md`.
- `docs/harmonizacao.csv` é a fonte da verdade das colunas.
- Código e comentários em inglês.
- Commits: Conventional Commits, em inglês.
- Nunca versionar nada dentro de `data/` além de README e .gitkeep.
- Commits: seguir `docs/guia-commits-semanticos.md` (Conventional Commits, em inglês).

## Stack

Python 3 + DuckDB (leitura e escrita de dados), pandas para análise.
