# Design

## Context

A trava (`modelo/trilha/guarda.py`) quebra o comando em comandos simples com o `shlex` (separadores `;&|()<>` e a quebra de linha), tira prefixos fixos (`sudo`, `env`, `command`, `time`, `nohup`, `exec` e as atribuições `X=y`), olha se a primeira palavra é `git`, `gh`, `pkill` ou `pgrep` e procura o subcomando (`push`, `commit`, `pr merge`) em qualquer posição depois dela. O `#` vira comentário, a aspa sem par cai num `split()` cru, e o texto de um `-c` com espaço é lido de novo como comando. O `gh pr checks` roda sem prazo, e uma exceção sai com 1, que não barra. O `kit.py atualizar` lê a versão do projeto, migra, copia a pasta `trilha/` e só depois consulta o histórico do kit (`git log`); a conferência das regras avisa os cinco lugares da stack assim que existe um TDD.

## Goals / Non-Goals

**Goals:**
- A trava acha o comando proibido onde o shell o executaria, sem passar a barrar os comandos legítimos que os testes de hoje deixam passar.
- Nenhuma falha da trava libera um comando; nenhuma recusa do `atualizar` deixa o projeto pela metade.

**Non-Goals:**
- Um interpretador de shell completo: o que só roda por expansão de variável (`$CMD`) ou por arquivo de script continua fora do alcance da trava; a trava do commit e o CI cobrem o resto.
- Os falsos positivos aceitos na auditoria (o texto de um heredoc que grava `git push --force` num arquivo).

## Decisions

**1. A leitura do comando.** O `shlex` passa a não ter comentário (`commenters = ""`): o `#` é palavra, como no `bash` dentro de uma palavra, e o comentário de fim de linha vira palavras do comando dele, sem engolir a linha seguinte. A crase entra nos separadores. Com aspa sem par, a leitura se repete com as aspas trocadas por espaço, em vez do `split()` cru, e mantém os separadores. Alternativa descartada: ler as palavras cruas atrás de `git`, `push` e uma força em qualquer lugar, que barraria `git push && rm -f x`.

**2. A posição do comando.** Antes da primeira palavra saem, além dos prefixos de hoje, as palavras do shell (`if`, `then`, `else`, `elif`, `do`, `while`, `until`, `!`, `{`) e os comandos que envolvem outro (`timeout`, `nice`, `ionice`, `stdbuf`, `xargs`, `eval`, `watch`, `setsid`, `chronic`, `unbuffer`, `builtin`), com as opções deles e, nos que pedem, o valor (a duração do `timeout`, o `-n` do `nice`, o `-I` e o `-n` do `xargs`). O `git` como argumento (`echo git push -f`) continua fora da posição de comando.

**3. Shell dentro do comando.** O texto com espaço que vem depois de um `-c` ou de um grupo curto com `c` (`-lc`, `-xc`), ou depois do `<<<`, é lido de novo como comando.

**4. O subcomando do git.** As opções globais do git são puladas (as que levam valor: `-C`, `-c`, `--git-dir`, `--work-tree`, `--namespace`, `--exec-path`, `--config-env`, separadas ou com `=`); o subcomando é a primeira palavra depois delas. Durante esse salto, um `-c` (ou `-c` colado, ou `--config-env`) com a chave `core.hooksPath` (sem diferença de maiúscula) e valor diferente de `trilha/hooks` barra. No subcomando `config`, a chave `core.hooksPath` seguida de outro valor, ou com `--unset`, `--unset-all` ou `unset`, barra; sem valor, é leitura e passa.

**5. A força no push.** Barra o grupo curto com `f`, o `+` no começo de um refspec, toda opção longa que começa com `--force` (menos o `--force-if-includes` sozinho, que o git ignora sem outra força) e toda abreviação de `--mirror` com pelo menos quatro caracteres (`--mi`, que o git aceita por ser única).

**6. O `--no-verify` abreviado.** Toda palavra `p` com `p.startswith("--no-veri")` e `"--no-verify".startswith(p)` barra, em qualquer comando, como hoje barra o `--no-verify` inteiro.

**7. O `gh pr merge`.** O merge vale com `--merge` ou com o `m` num grupo curto; o `--squash`, o `--rebase` ou o `s` e o `r` num grupo barram. As opções que levam valor (`-R`/`--repo`, `-b`/`--body`, `-t`/`--subject`, `-F`/`--body-file`, `-A`/`--author-email`, `--match-head-commit`) consomem a palavra seguinte; o alvo é a primeira palavra que sobra. O `gh pr checks` recebe o alvo e o `--repo` e roda com `timeout=30`; o prazo estourado barra, com a mensagem de que a verificação não respondeu.

**8. A falha da trava.** O `main` trata a entrada que não é objeto, ou sem `tool_input.command` em texto, como comando vazio (passa) e envolve a leitura numa captura geral: uma exceção inesperada imprime o motivo e sai com 2.

**9. O `atualizar` confere antes de mudar.** Logo depois das recusas de hoje, e antes da migração: `git -C <kit> rev-parse --is-shallow-repository` (falha: o kit não é um repositório git; `true`: clone raso) e a comparação numérica da versão do projeto com a do kit (projeto mais novo: recusa, com o `git pull`).

**10. O aviso da stack em dois tempos.** A tabela `STACK_DO_MODELO` continua com os cinco lugares; o `scripts/check.sh` e o `.github/workflows/verificacao.yml` só entram no aviso quando existe um `openspec/specs/*/spec.md`. A mensagem diz que o Dependabot, o `.gitignore` e o contexto vêm no gate 2, e o `check.sh` e o CI, na change 01.

## Risks / Trade-offs

- [Falso positivo novo: `eval`, `xargs` ou `timeout` seguidos de um `git push -f` que o usuário queria mesmo] → é o que o método proíbe; a trava que barra algo legítimo volta ao usuário, como o comum manda.
- [Opção de um comando que envolve outro e não está na lista, deslocando a posição do `git`] → o `git` deixa de ser achado, como hoje; a lista cobre os casos provados na auditoria.
- [Prazo de 30 s pouco para um `gh pr checks` lento] → o prazo padrão do hook do Claude Code é maior que esse; barrar e pedir de novo é o lado seguro.
- [O clone raso recusado num CI que só atualiza projetos] → nenhum CI roda o `atualizar`; ele é manual.

## Migration Plan

Nenhuma: a trava e a conferência novas chegam aos projetos com a cópia da 2.5, pelo `kit.py atualizar`, sob ordem do usuário.

## Verificação

A preencher no apply, com a evidência de cada cenário.

## Respostas à revisão

A preencher depois do `/opsx:verify` e da revisão de código.
