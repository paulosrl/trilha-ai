# Design

## Context

Ver `proposal.md` (Why). Desde a change 22, o `conferir_andamento` procura cada vizinho com duas regex, o "solto" e o "de fora", com lookbehind e lookahead que se cruzam, e o `../` por substring. Os testes cobrem só as formas que a revisão da change 22 levantou.

## Goals / Non-Goals

**Goals:**
- Uma regra só, com as isenções escritas num lugar, em comparações de texto simples.

**Non-Goals:**
- Distinguir o vizinho dentro de crases ou de links: a palavra reprova em qualquer lugar, como hoje.
- Conferir no disco se o caminho citado existe no projeto.

## Decisions

### D1. Por palavra e por parte
A conferência tira do texto as palavras, as sequências de letras, números, `_` e `.~/:@#?=&%+-`: o espaço, a crase, as aspas, os parênteses, a vírgula e o travessão separam. De cada palavra sai o `.`, o `:`, o `?` e o `!` do fim (a pontuação da frase); um `./` do começo sai também e marca o caminho como do próprio projeto. O resto se parte em `/`, `:`, `#` e `?`. Uma parte cita o vizinho quando é o nome, ou o nome seguido de `.` e de uma extensão que começa por `git` ou `wiki` ou que não é só de letras (com `.` entre elas, `heimdall.config.yaml`). O `../` continua por substring.

*Alternativa:* manter as duas regex e acertar os lookarounds. Recusada: foi esse o caminho das quatro rodadas de correção da change 22, e cada isenção nova precisa entrar nos dois padrões.

### D2. A pasta do método pelo lugar do script
A primeira parte de uma palavra não cita o vizinho quando o nome é o da pasta onde o `confere_metodo.py` está (`Path(__file__).resolve().parent.name`, o `trilha-ai`) e a palavra é um caminho: ou começou com `./`, ou tem mais partes depois (`trilha-ai/`, `trilha-ai/verifica.sh`). Fora disso, o nome no começo de um caminho relativo reprova (`heimdall/scripts/check.sh`).

*Alternativas:* escrever `trilha-ai` no código, que repete o nome que o kit já dá à pasta; ou isentar o caminho que existe no projeto, que lê o disco numa função que hoje só lê o texto, e o `ANDAMENTO.md` cita também o que ainda vai ser criado.

### D3. A versão
O método vai à 2.22: o comum, o `plugin.json` na 2.22.0 e a tag `v2.22`.

## Risks / Trade-offs

- [Uma extensão de arquivo com número (`heimdall.mp4`) reprova] → O erro fica do lado seguro: reprova, e quem escreveu troca o texto; o `trilha-ai.v2` que a revisão achou é a mesma forma.
- [O nome no meio de um caminho relativo do próprio projeto (`docs/heimdall/x`) reprova] → Já reprovava desde a change 22, pelo "de fora"; um projeto não tem pasta com o nome do vizinho.
- [Um separador que o D1 não lista, colado ao nome, esconde o vizinho] → A lista inclui o que aparece em caminho e URL; o resto separa, e o nome solto reprova.
