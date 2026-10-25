# Design

## Context

Ver `proposal.md` (Why). O `conferir_andamento` do `confere_metodo.py` reprova cada nome de `["../", *vizinhos]` que está no texto (`nome in texto`), por substring.

## Goals / Non-Goals

**Goals:**
- O vizinho só reprova quando é citado como outro repositório: o nome inteiro, sem barra depois.

**Non-Goals:**
- Distinguir o nome do vizinho dentro de crases ou de links: o nome inteiro reprova em qualquer lugar.

## Decisions

### D1. O nome inteiro
Para cada vizinho, a conferência procura o nome com `re.escape` entre duas fronteiras: antes, nem letra, número, `_`, `-` nem `.`; depois, nem letra, número, `_`, `-` nem `/`. O `.` depois continua contando (o fim de uma frase: "o kit trilha-ai."). O `../` continua por substring.

*Alternativa:* tirar `trilha-ai` da lista de vizinhos dos projetos. Recusada: o vizinho existe para impedir o `ANDAMENTO.md` de descrever o trabalho do kit, e a troca seria em cada projeto, à mão.

### D2. A versão
O método vai à 2.21: o comum, o `plugin.json` na 2.21.0 e a tag `v2.21`.

## Risks / Trade-offs

- [O nome seguido de barra pode ser o caminho para o vizinho (`trilha-ai/ferramentas/kit.py` escrito como se fosse o do kit)] → Num projeto, `trilha-ai/` é a pasta do método; o caminho para o kit ao lado é `../trilha-ai`, que o `../` pega.
