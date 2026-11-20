# Perguntas do projeto

# Perguntas do projeto

**Pergunta central:** quanto da nota de Ciências da Natureza de um
estudante mineiro é explicado pela sua origem (renda, escolaridade
dos pais, rede de ensino e município)? E em quais conteúdos essa
diferença pesa mais?

Cada pergunta indica a população e a tabela que usa. As populações
estão definidas na D002 e na D007.

| Pergunta | Tema                   | Período   | Tabela principal            | Etapa |
| -------- | ---------------------- | --------- | --------------------------- | ----- |
| Q1       | O tamanho da diferença | 2020–2025 | `fct_individual`, `agg_*`   | 3     |
| Q2       | O mapa                 | 2020–2025 | `agg_municipio_ano`         | 3, 4  |
| Q3       | O que pesa mais        | 2020–2023 | `fct_individual`            | 4     |
| Q4       | Quem nem chega à prova | 2020–2023 | `fct_individual`            | 4     |
| Q5       | Raio-X das questões    | 2020–2025 | `fct_agregada`, `stg_itens` | 5     |
| Q6       | A TRI na prática       | 2020–2025 | `stg_itens`                 | 5     |

## Q1 — O tamanho da diferença

Qual é a diferença de nota em CN entre redes de ensino, faixas de
renda per capita e níveis de escolaridade dos pais? Ela mudou ao
longo do tempo?

- **Por renda e escolaridade dos pais:** só 2020–2023
  (`fct_individual`), porque em 2024–2025 a nota não se liga ao
  questionário (D002).
- **Por rede:** 2020–2025 (`agg_rede_ano`), com atenção à quebra de
  série entre 2023 e 2024 (D002).

## Q2 — O mapa

Como a nota média em CN varia entre os municípios mineiros? Quais
ficam acima ou abaixo do esperado para o perfil dos seus alunos?
Onde fica Juiz de Fora?

- **Médias por município:** 2020–2025 (`agg_municipio_ano`), com o
  número de alunos sempre visível e cuidado com municípios pequenos.
- **"Acima ou abaixo do esperado":** depende de um modelo com o perfil
  dos alunos, então só 2020–2023 (`fct_individual`), na Etapa 4.

## Q3 — O que pesa mais

Quanto da variação da nota em CN cada fator explica (renda per capita,
escolaridade dos pais, ocupação dos pais, rede, localização)? A rede
importa depois de considerar a renda?

- 2020–2023 (`fct_individual`), concluintes com nota e com
  questionário (D005, D007).

## Q4 — Quem nem chega à prova

A ausência no 2º dia, entre quem esteve no 1º, depende do perfil
socioeconômico? Que viés isso introduz nas médias de nota?

- **Por perfil:** 2020–2023 (`fct_individual`).
- **Por rede e município:** 2020–2025 (`agg_*`).
- Presença e eliminação seguem a D007.

## Q5 — Raio-X das questões

Quais questões e habilidades de CN têm a maior diferença de acerto
entre os grupos? A Física é a área mais desigual?

- 2020–2025: respostas e gabaritos em `fct_agregada`, itens em
  `stg_itens`. Os grupos possíveis são rede, município e localização;
  renda e escolaridade dos pais só em 2020–2023.
- Requer a rotulagem dos itens por disciplina (Física, Química,
  Biologia), feita pelo autor.

## Q6 — A TRI na prática

Como os parâmetros da TRI dos itens de CN ajudam a entender a nota?
Por que dois participantes com o mesmo número de acertos podem ter
notas diferentes?

- 2020–2025 (`stg_itens`), com os parâmetros `param_a`, `param_b`
  e `param_c`.

## Extensão possível

**Q7 — Escola e infraestrutura:** a infraestrutura da escola
(laboratório de ciências, internet) se relaciona com a nota em CN?
Só 2024–2025, via `codigo_escola` e Censo Escolar (D002, D004).
Depende de baixar e preparar o Censo Escolar.
