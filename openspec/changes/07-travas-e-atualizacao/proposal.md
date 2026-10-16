# Proposal

## Why

A rodada 4 da auditoria (`docs/auditorias/2026-10.md`), aprovada pelo usuário em 2026-10-16, provou que as travas do método se contornam com facilidade: `git -c core.hooksPath=/dev/null commit` e `git commit --no-veri` pulam a trava do commit (R1), e o envio forçado passa escrito de outros jeitos, como `timeout 10 git push -f`, `if …; then git push -f; fi`, `bash -lc "git push -f"` e `git push --force-w` (R2). O `gh pr checks` da trava não tem prazo, e a trava que estoura o prazo do Claude Code não barra o merge (R8). O `kit.py atualizar` rebaixa um projeto quando o kit ao lado está atrás (R3) e, com o kit sem o histórico do git, muda o projeto antes de recusar (R7). E o texto do método da 2.5 passou a parte da stack do `check.sh` e do CI para a change 01 (R4), mas a conferência ainda a cobra logo depois do TDD.

## What Changes

- A trava do Claude Code barra o commit que desliga a trava do commit (o `core.hooksPath` noutro valor num `-c` ou num `git config`) e a abreviação do `--no-verify`.
- A trava acha o `git push` com força atrás de comandos que envolvem outro, de palavras do shell, de crase, de `bash -lc` e `<<<`, com `#` no meio da linha, com aspa sem par, e reconhece as opções `--force…` abreviadas e o `--mirror`.
- A trava lê o subcomando do git depois das opções globais (o `git log --grep commit -n 3` deixa de ser barrado), aceita o `-m` do `gh pr merge` como `--merge` e passa o `-R` ao `gh pr checks`.
- O `gh pr checks` tem prazo de 30 s; estourado, ou com um erro inesperado, a trava barra.
- O `kit.py atualizar` recusa, antes de mudar qualquer arquivo, o projeto numa versão mais nova que a do kit e o kit sem o histórico do git (sem `.git` ou clone raso).
- Com o TDD, a conferência das regras avisa o Dependabot, o `.gitignore` e a linha "Stack" do `config.yaml`; o `check.sh` e o CI, só a partir do primeiro spec em `openspec/specs/`.

**Fora desta change:** os achados aceitos da rodada 4 (os falsos positivos restantes da trava, como o heredoc que grava num arquivo uma linha com `git push --force`; a página com HTML cru; o kit em edição sem versão nova; o commit com o teste vermelho; a hora a leste de UTC; o "Ciclo" sem decomposição; o aviso da ação do Dependabot); o `cd ../outro && gh pr merge`; a migração dos projetos; o texto do método, já mudado na 2.5 fora de change.

## Capabilities

### New Capabilities

- `trava-do-metodo`: o que a trava do Claude Code (`trilha/guarda.py`) barra e deixa passar, e como ela se comporta quando algo falha.

### Modified Capabilities

- `ferramenta-do-kit`: o `atualizar` recusa o kit atrás do projeto e o kit sem o histórico do git.
- `conferencias`: o aviso da stack por preencher depois do TDD separa o que vem no gate 2 do que vem na change 01.

## Impact

- Kit: `modelo/trilha/guarda.py`, `modelo/trilha/confere_regras.py`, `ferramentas/kit.py`, `testes/test_kit.py`; a versão 2.5, já aberta.
- Projetos: recebem a trava e a conferência novas com a cópia da 2.5, pelo `kit.py atualizar`, sob ordem do usuário.
