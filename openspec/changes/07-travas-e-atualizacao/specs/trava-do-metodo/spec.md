# Spec Delta

## Purpose

Define o que a trava do Claude Code (`trilha/guarda.py`, hook antes de cada comando Bash) barra e deixa passar, para que o agente não pule a verificação, não force um envio e não faça o merge fora do método, nem por um caminho indireto.

## ADDED Requirements

### Requirement: Trava do commit não se desliga
A trava SHALL barrar o comando git que desliga a trava do commit: o `core.hooksPath` com valor diferente de `trilha/hooks` passado num `-c` (separado ou colado) e o `git config` que o grava com outro valor ou o apaga. A leitura do `core.hooksPath` e a gravação de `trilha/hooks` MUST passar.

#### Scenario: Hooks desligados por -c
- **WHEN** o comando é `git -c core.hooksPath=/dev/null commit -m x` ou `git -ccore.hooksPath= commit -m x`
- **THEN** a trava barra

#### Scenario: Hooks trocados por git config
- **WHEN** o comando é `git config core.hooksPath .git/hooks` ou `git config --unset core.hooksPath`
- **THEN** a trava barra

#### Scenario: Leitura e valor do método
- **WHEN** o comando é `git config core.hooksPath` ou `git config core.hooksPath trilha/hooks`
- **THEN** a trava deixa passar

### Requirement: Abreviação do --no-verify
A trava SHALL barrar toda palavra que o git aceita como abreviação do `--no-verify`, da `--no-veri` até a `--no-verify`.

#### Scenario: Opção abreviada
- **WHEN** o comando é `git commit --no-veri -m y`
- **THEN** a trava barra

### Requirement: Envio forçado em qualquer forma
A trava SHALL barrar o `git push` com força quando o `git` vier depois de um comando que envolve outro (`timeout`, `nice`, `xargs`, `eval` e afins) ou de uma palavra do shell, dentro de crase, num `bash -lc` ou `<<<`, com `#` no meio da linha ou aspa sem par, e com as opções `--force…` abreviadas (salvo `--force-if-includes` sozinho) ou o `--mirror`. O `git` como argumento de outro comando MUST passar.

#### Scenario: Comando que envolve outro
- **WHEN** o comando é `timeout 10 git push -f`, `echo main | xargs git push -f origin` ou `eval git push -f`
- **THEN** a trava barra

#### Scenario: Palavras do shell
- **WHEN** o comando é `if true; then git push -f; fi` ou `{ git push -f; }`
- **THEN** a trava barra

#### Scenario: Shell dentro do comando
- **WHEN** o comando é `bash -lc "git push -f"`, `bash <<< "git push -f"` ou `` `git push -f` ``
- **THEN** a trava barra

#### Scenario: Cerquilha e aspa sem par
- **WHEN** o comando é `echo a#b; git push -f`, uma linha com comentário seguida de `git push --force-with-lease`, ou um texto com aspa sem par seguido de `git push --force`
- **THEN** a trava barra

#### Scenario: Opções abreviadas e espelho
- **WHEN** o comando é `git push --force-w` ou `git push --mirror`
- **THEN** a trava barra

#### Scenario: O git como argumento
- **WHEN** o comando é `echo git push -f`, `git push && rm -f x` ou `git push --force-if-includes`
- **THEN** a trava deixa passar

### Requirement: Subcomando do git depois das opções globais
A trava SHALL tomar como subcomando do git a primeira palavra depois das opções globais dele, e MUST NOT tratar como `commit` ou `push` uma dessas palavras que aparece mais adiante, como argumento de outro subcomando.

#### Scenario: Palavra no argumento de outro subcomando
- **WHEN** o comando é `git log --grep commit -n 3` ou `git log -n 3 -- push -f`
- **THEN** a trava deixa passar

#### Scenario: Opções globais antes do subcomando
- **WHEN** o comando é `git -C ../x push -f`
- **THEN** a trava barra

### Requirement: Merge pelo -m no repositório indicado
No `gh pr merge`, a trava SHALL aceitar o `-m` (também num grupo, como `-md`) como o `--merge`, conferir a verificação do PR no repositório que o `-R` ou o `--repo` indicam, e MUST NOT tomar o valor de uma opção como o número do PR.

#### Scenario: Merge com -m
- **WHEN** o comando é `gh pr merge 7 -m -d` e a verificação do PR está verde
- **THEN** a trava deixa passar

#### Scenario: Repositório indicado
- **WHEN** o comando é `gh pr merge -R dono/repo 7 --merge`
- **THEN** a trava confere `gh pr checks 7` no repositório `dono/repo`

### Requirement: A trava nunca libera por falha
A trava SHALL esperar a verificação do PR por no máximo 30 segundos e MUST barrar quando o prazo estourar ou quando ela mesma falhar de um jeito inesperado; a entrada que não traz comando passa.

#### Scenario: Verificação que não responde
- **WHEN** o `gh pr checks` não responde em 30 segundos
- **THEN** a trava barra o merge, dizendo que a verificação não respondeu

#### Scenario: Entrada sem comando
- **WHEN** a entrada é um JSON sem `tool_input` com `command`, como `[]` ou `{"tool_input": "x"}`
- **THEN** a trava deixa passar, sem erro
