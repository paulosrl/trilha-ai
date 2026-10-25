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
Para cada vizinho não vazio, a conferência procura o nome com `re.escape` de dois jeitos. Solto: antes, nem letra, número, `_`, `-` nem `.`; depois, nem letra, número, `_`, `-`, `/` nem um `.` seguido de letra ou número (a extensão de um arquivo, `heimdall.yaml`); o ponto final de frase conta ("o kit trilha-ai."). De fora: o nome logo depois de `/`, `~` ou `:`, mas não de `./`, seguido de `/` ou do `.git` final (a URL, o caminho absoluto, o `~/`, o endereço do repositório). O `../` continua por substring.

*Alternativa:* tirar `trilha-ai` da lista de vizinhos dos projetos. Recusada: o vizinho existe para impedir o `ANDAMENTO.md` de descrever o trabalho do kit, e a troca seria em cada projeto, à mão.

### D2. A versão
O método vai à 2.21: o comum, o `plugin.json` na 2.21.0 e a tag `v2.21`.

## Risks / Trade-offs

- [O nome no começo de um caminho relativo pode ser o vizinho escrito como se estivesse dentro do projeto (`trilha-ai/ferramentas/kit.py`)] → Num projeto, `trilha-ai/` é a pasta do método; o kit ao lado se cita por `../trilha-ai`, que o `../` pega, ou pelo caminho absoluto ou pela URL, que o "de fora" pega.

## Verificação

**Execução manual (tarefa 3.2), em 2026-10-24,** no scratchpad, num clone descartável do Heimdall (`0a3902c`, com o `--vizinho trilha-ai` no `local-012`), com o `trilha-ai/confere_metodo.py` desta change copiado por cima. Com o `ANDAMENTO.md` citando a change `hooks-pela-trilha-ai` e `bash trilha-ai/verifica.sh`, o `scripts/local-012-confere-metodo.sh` terminou com 0; com mais a linha "o kit trilha-ai está na 2.21", terminou com 1, com "FALHA: ANDAMENTO.md cita outro repositório: trilha-ai".

**Depois das respostas ao code review e ao verify, em 2026-10-24,** com o `confere_metodo.py` final, num clone novo do Heimdall: com o `ANDAMENTO.md` citando `hooks-pela-trilha-ai`, `./trilha-ai/verifica.sh` e `heimdall.yaml`, o `local-012` terminou com 0; com mais `https://github.com/paulosrl/trilha-ai.git`, reprovou, com "FALHA: ANDAMENTO.md cita outro repositório: trilha-ai".

## Revisão dos artefatos

Feita antes do apply, em 2026-10-24, pela coerência entre a proposta, o delta, o design e as tarefas, e diante do `conferir_andamento`: sem defeito. Os quatro cenários de então têm teste nomeado (dois entraram depois, nas respostas à revisão); o "Caminho para fora do projeto" descreve o comportamento de hoje, que a change preserva, e o teste dele passa antes do código.

## Respostas à revisão

O `/code-review high 23` (R) e o `/opsx:verify` (V), em 2026-10-24, cada um por um agente sem o contexto da sessão. Nenhum achado crítico.

- **R1 (o nome seguido de barra isentava a URL e o caminho absoluto até o vizinho, que antes reprovavam):** aplicado. Conta o nome logo depois de `/`, `~` ou `:` (D1); os testes da URL, do caminho absoluto e do `~/`.
- **R2 (o requisito não dizia o lado do `.`):** aplicado. O requisito e o D1 dizem os dois lados, e o cenário "Vizinho pelo nome" ganhou o ponto final de frase.
- **R3 (o arquivo com o nome do vizinho e extensão, `heimdall.yaml`, reprovava):** aplicado. O `.` seguido de letra ou número não conta; o ponto final de frase conta.
- **R4 (o `--vizinho ""` reprovava todo texto):** aplicado. O nome vazio é ignorado; cenário "Vizinho vazio".
- **R5 (a busca diferencia maiúsculas):** recusado. Com `re.IGNORECASE`, o `ANDAMENTO.md` do Xavier que fala do produto "Heimdall" reprovaria pelo vizinho `heimdall`; os nomes dos repositórios são em minúsculas.
- **R6 (o carregador do `confere_metodo.py` copiado nos testes):** aplicado. A constante `METODO`, ao lado da `REGRAS`.
- **V1 (o `./trilha-ai/` reprovava pelo "de fora"):** aplicado. O `./` antes do nome não conta como de fora; teste e cenário "Pasta do método".
- **V2 (a URL com o `.git` passava):** aplicado. O "de fora" aceita o `.git` final; teste e cenário.
- **V3 (faltava esta seção):** aplicado.
- **V4 (a execução manual era anterior ao código final):** aplicado. Refeita, em "Verificação".
- **V5, V6 e V7 (a contagem dos cenários na revisão dos artefatos, o risco e a proposta com a regra antiga):** aplicados.
