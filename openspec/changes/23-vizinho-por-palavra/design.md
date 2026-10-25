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
A conferência tira do texto as palavras, as sequências de letras, números, `_` e `.~/:@#?=&%+-`: o espaço, a crase, as aspas, os parênteses, a vírgula e o travessão separam. De cada palavra sai o `.`, o `:`, o `?` e o `!` do fim (a pontuação da frase); um `./` do começo sai também e marca o caminho como do próprio projeto. O resto se parte em tudo o que não cabe num nome (letras, números, `_`, `.` e `-`), e cada parte perde o `_` das pontas (o itálico do Markdown). Uma parte cita o vizinho quando é o nome, ou o nome seguido de `.` e de uma extensão que começa por `git` ou `wiki` ou que não é só de letras (com `.` entre elas, `heimdall.config.yaml`); no host de uma URL (a parte depois do `://`), o nome seguido de `.` e de qualquer coisa (`heimdall.vercel.app`). As partes de cada palavra saem uma vez só, para todos os vizinhos. O `../` continua por substring.

*Alternativa:* manter as duas regex e acertar os lookarounds. Recusada: foi esse o caminho das quatro rodadas de correção da change 22, e cada isenção nova precisa entrar nos dois padrões.

### D2. A pasta do método pelo lugar do script
A primeira parte de uma palavra não cita o vizinho quando o nome é o da pasta onde o `confere_metodo.py` está (`Path(__file__).resolve().parent.name`, o `trilha-ai`) e a palavra é um caminho: o nome seguido de `/` (`trilha-ai/`, `trilha-ai/verifica.sh`) ou o `./trilha-ai` inteiro. O `trilha-ai#24`, o `trilha-ai:main` e o `./trilha-ai:x` não são a pasta e reprovam. Fora disso, o nome no começo de um caminho relativo reprova (`heimdall/scripts/check.sh`).

*Alternativas:* escrever `trilha-ai` no código, que repete o nome que o kit já dá à pasta; ou isentar o caminho que existe no projeto, que lê o disco numa função que hoje só lê o texto, e o `ANDAMENTO.md` cita também o que ainda vai ser criado.

### D4. O vizinho só com o nome de um repositório
O `main` recusa, com o uso e o código 2, o `--vizinho` com um caractere que não cabe num nome: as partes nunca têm esse caractere, e o vizinho nunca seria achado.

*Alternativa:* casar o nome com barra (`paulosrl/trilha-ai`) contra a sequência das partes. Recusada: os projetos dão ao vizinho o nome da pasta ao lado, e a recusa avisa o erro em vez de calar.

### D3. A versão
O método vai à 2.22: o comum, o `plugin.json` na 2.22.0 e a tag `v2.22`.

## Risks / Trade-offs

- [Uma extensão de arquivo com número (`heimdall.mp4`) reprova] → O erro fica do lado seguro: reprova, e quem escreveu troca o texto; o `trilha-ai.v2` que a revisão achou é a mesma forma.
- [O nome no meio de um caminho relativo do próprio projeto (`docs/heimdall/x`) reprova] → Já reprovava desde a change 22, pelo "de fora"; um projeto não tem pasta com o nome do vizinho.
- [O domínio do vizinho fora de uma URL (`heimdall.github.io`, `heimdall.com`) passa como arquivo com extensão só de letras] → Sem o `://`, ele não se distingue do `heimdall.config.yaml`; com o `://`, o host reprova.

## Revisão dos artefatos

Feita antes do apply, em 2026-10-25, pela coerência entre a proposta, o delta, o design e as tarefas, e diante do `conferir_andamento`: sem defeito. Os sete cenários têm teste nomeado; o "Caminho para fora do projeto" e o "Vizinho vazio" descrevem o comportamento de hoje, que a change preserva, e os testes deles passam antes do código.

## Verificação

**No apply, em 2026-10-25,** uma sonda à mão achou o `trilha-ai.git/x` isento pela pasta do método, porque a isenção olhava o vizinho e não a primeira parte. A isenção passou a exigir a primeira parte igual ao nome da pasta (D2), e o `trilha-ai.git/x` entrou no `test_andamento_reprova_o_vizinho_pelo_nome`.

**Execução manual (tarefa 3.2), em 2026-10-25,** no scratchpad, num projeto novo criado pelo `python3 ferramentas/kit.py novo`, com o `bash trilha-ai/verifica.sh --vizinho trilha-ai --vizinho heimdall`. Com o `ANDAMENTO.md` citando `./trilha-ai`, `bash trilha-ai/verifica.sh`, a change `hooks-pela-trilha-ai` e o `heimdall.yaml`, terminou com 0 ("ok: decomposição, TDD e ANDAMENTO.md conferidos"). Com a linha "clonar trilha-ai.git ao lado", terminou com 1, com "FALHA: ANDAMENTO.md cita outro repositório: trilha-ai"; com a linha "ajustar heimdall/scripts/check.sh", no lugar dela, terminou com 1, com "FALHA: ANDAMENTO.md cita outro repositório: heimdall".

**Depois das respostas à revisão, em 2026-10-25,** com o `confere_metodo.py` final, num projeto novo do kit no scratchpad, com o `bash trilha-ai/verifica.sh --vizinho trilha-ai --vizinho heimdall`: com o mesmo `ANDAMENTO.md` que passava, terminou com 0; com a linha "clonar trilha-ai.git ao lado", com "ajustar heimdall/scripts/check.sh" e com "ver trilha-ai#24", cada uma no lugar da outra, terminou com 1, citando o vizinho. Com o `--vizinho paulosrl/trilha-ai`, terminou com 2 e mostrou o uso.

## Respostas à revisão

O `/code-review 24` (R) e o `/opsx:verify` (V), em 2026-10-25, cada um por um agente sem o contexto da sessão. Nenhum achado crítico no verify; o review achou três regressões frente à main (R1 a R3). O usuário escolheu aplicar tudo.

- **R1 (o vizinho colado a `@`, `=`, `&`, `%`, `+` ou `~` passava: `trilha-ai@2.21`, `pip install trilha-ai==2.21`, `ssh pl@heimdall`):** aplicado. A palavra se parte em tudo o que não cabe num nome (D1); teste `test_andamento_reprova_o_nome_colado_a_um_sinal` e cenário "Nome colado a um sinal".
- **R2 e V1 (a isenção da pasta do método valia depois de `:`, `#` e `?`: `trilha-ai#24`, `trilha-ai:main`):** aplicado. A isenção pede o `/` logo depois do nome, ou o `./trilha-ai` inteiro (D2); os mesmos teste e cenário.
- **R3 (o `--vizinho` com barra nunca era achado):** aplicado. O `--vizinho` com caractere que não cabe num nome é recusado como erro de uso (D4); teste `test_metodo_recusa_o_vizinho_com_separador` e o requisito "Vizinho só com o nome de um repositório".
- **R4 (o host da URL que começa pelo vizinho passava como arquivo, `https://heimdall.vercel.app`):** aplicado. No host, o nome seguido de `.` reprova (D1); teste `test_andamento_reprova_o_host_da_url` e cenário "Host de uma URL". O domínio sem o `://` fica como risco.
- **R5 (o `_heimdall_` do itálico passava):** aplicado. A parte perde o `_` das pontas (D1); no teste e no cenário do R1.
- **R6 (os testes não cobriam essas formas):** aplicado, com os testes acima, escritos antes do código.
- **R7 (as partes recalculadas para cada vizinho) e R8 (o ramo a mais da pasta):** aplicados. As partes saem uma vez, sem a pasta do método, num conjunto que todos os vizinhos consultam.
- **V2 (a docstring do módulo não citava o `.wiki` nem o final que não é só de letras):** aplicado, com o host e a regra do `--vizinho`.
