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

**1. A leitura do comando.** O `shlex` passa a não ter comentário (`commenters = ""`): o `#` é palavra, como no `bash` dentro de uma palavra, e o comentário de fim de linha vira palavras do comando dele, sem engolir a linha seguinte. A crase entra nos separadores. Antes da leitura, a linha continuada (`\` no fim) se junta à seguinte, e o corpo de cada heredoc sai, salvo quando quem o recebe é um shell (`bash <<EOF`): ele é dado, não comando (revisto depois da revisão de código, pontos 1 e 4). Com aspa sem par, a leitura se repete com as aspas trocadas por espaço, em vez do `split()` cru, e mantém os separadores. Alternativa descartada: ler as palavras cruas atrás de `git`, `push` e uma força em qualquer lugar, que barraria `git push && rm -f x`.

**2. A posição do comando.** Antes da primeira palavra saem, além dos prefixos de hoje e das atribuições, também as com aspas (`X="a b"`, revisão, ponto 2), as palavras do shell (`if`, `then`, `else`, `elif`, `do`, `while`, `until`, `!`, `{`) e os comandos que envolvem outro (`timeout`, `nice`, `ionice`, `stdbuf`, `xargs`, `eval`, `watch`, `setsid`, `chronic`, `unbuffer`, `builtin`), com as opções deles e, nos que pedem, o valor (a duração do `timeout`, o `-n` do `nice`, o `-I` e o `-n` do `xargs`). O `git` como argumento (`echo git push -f`) continua fora da posição de comando.

**3. Shell dentro do comando.** O texto com espaço que vem depois de um `-c` ou de um grupo curto com `c` (`-lc`, `-xc`) de um shell que está no comando, ou depois do `<<<`, é lido de novo como comando, à parte: as palavras seguintes continuam no comando de fora (revisão, ponto 3).

**4. O subcomando do git.** As opções globais do git são puladas (as que levam valor: `-C`, `-c`, `--git-dir`, `--work-tree`, `--namespace`, `--exec-path`, `--config-env`, separadas ou com `=`); o subcomando é a primeira palavra depois delas. Durante esse salto, um `-c` (ou `-c` colado, ou `--config-env`) com a chave `core.hooksPath` (sem diferença de maiúscula) e valor diferente de `trilha/hooks` barra. No subcomando `config`, a chave `core.hooksPath` seguida de outro valor, ou com `--unset`, `--unset-all` ou `unset`, barra; sem valor, é leitura e passa.

**5. A força no push.** Barra o grupo curto com `f`, o `+` no começo de um refspec, toda opção longa que começa com `--force` (menos o `--force-if-includes` sozinho, que o git ignora sem outra força) e toda abreviação de `--mirror` com pelo menos quatro caracteres (`--mi`, que o git aceita por ser única).

**6. O `--no-verify` abreviado.** Toda palavra `p` com `p.startswith("--no-veri")` e `"--no-verify".startswith(p)` barra, em qualquer comando, como hoje barra o `--no-verify` inteiro.

**7. O `gh pr merge`.** O merge vale com `--merge` ou com o `m` num grupo curto; o `--squash`, o `--rebase` ou o `s` e o `r` num grupo barram. As opções que levam valor (`-R`/`--repo`, `-b`/`--body`, `-t`/`--subject`, `-F`/`--body-file`, `-A`/`--author-email`, `--match-head-commit`) consomem a palavra seguinte; o alvo é a primeira palavra que sobra. O `gh pr checks` recebe o alvo e o `--repo` (ou o `GH_REPO=` do comando, revisão, ponto 6) e roda com `timeout=30`; o prazo estourado barra, com a mensagem de que a verificação não respondeu.

**8. A falha da trava.** O `main` trata a entrada que não é objeto, ou sem `tool_input.command` em texto, como comando vazio (passa) e envolve a leitura numa captura geral: uma exceção inesperada imprime o motivo e sai com 2.

**9. O `atualizar` confere antes de mudar.** Logo depois das recusas de hoje, e antes da migração: `git -C <kit> rev-parse --is-shallow-repository` e `--show-toplevel` (falha, ou a raiz de outro repositório: o kit não é um repositório git, revisão, ponto 5; `true`: clone raso) e a comparação numérica da versão do projeto com a do kit (projeto mais novo: recusa, com o `git pull`).

**10. O aviso da stack em dois tempos.** A tabela `STACK_DO_MODELO` continua com os cinco lugares; o `scripts/check.sh` e o `.github/workflows/verificacao.yml` só entram no aviso quando existe um `openspec/specs/*/spec.md`. A mensagem diz que o Dependabot, o `.gitignore` e o contexto vêm no gate 2, e o `check.sh` e o CI, na change 01.

## Risks / Trade-offs

- [Falso positivo novo: `eval`, `xargs` ou `timeout` seguidos de um `git push -f` que o usuário queria mesmo] → é o que o método proíbe; a trava que barra algo legítimo volta ao usuário, como o comum manda.
- [Opção de um comando que envolve outro e não está na lista, deslocando a posição do `git`] → o `git` deixa de ser achado, como hoje; a lista cobre os casos provados na auditoria.
- [Prazo de 30 s pouco para um `gh pr checks` lento] → o prazo padrão do hook do Claude Code é maior que esse; barrar e pedir de novo é o lado seguro.
- [O clone raso recusado num CI que só atualiza projetos] → nenhum CI roda o `atualizar`; ele é manual.

## Migration Plan

Nenhuma: a trava e a conferência novas chegam aos projetos com a cópia da 2.5, pelo `kit.py atualizar`, sob ordem do usuário.

## Verificação

Cada cenário com o teste que o comprova (`python3 -m unittest discover -s testes -k <teste>`), todos com `OK` em 2026-10-16; o conjunto (194 testes), o ruff (check e format) e o `openspec validate --all --no-interactive` sem erro.

| Cenário | Teste |
|---|---|
| Hooks desligados por -c; Hooks trocados por git config | `test_trava_barra_o_hookspath_desligado` |
| Leitura e valor do método | `test_trava_deixa_ler_e_gravar_o_hookspath_do_metodo` |
| Opção abreviada | `test_trava_barra_o_no_verify_abreviado` |
| Comando que envolve outro | `test_trava_barra_o_push_forcado_atras_de_outro_comando` |
| Palavras do shell | `test_trava_barra_o_push_forcado_nas_palavras_do_shell` |
| Shell dentro do comando | `test_trava_barra_o_push_forcado_em_shell_aninhado` |
| Cerquilha e aspa sem par | `test_trava_barra_o_push_forcado_com_cerquilha_ou_aspa_sem_par` |
| Opções abreviadas e espelho | `test_trava_barra_a_forca_abreviada_e_o_espelho` |
| O git como argumento | `test_trava_deixa_o_git_como_argumento` |
| Palavra no argumento de outro subcomando; Opções globais antes do subcomando | `test_trava_le_o_subcomando_depois_das_opcoes_globais` |
| Merge com -m | `test_trava_aceita_o_merge_com_m` |
| Repositório indicado | `test_trava_confere_o_pr_no_repositorio_indicado` |
| Verificação que não responde | `test_trava_barra_a_verificacao_que_nao_responde` |
| Entrada sem comando | `test_trava_deixa_passar_a_entrada_sem_comando` |
| Linha continuada e atribuição com aspas | `test_trava_barra_a_linha_continuada_e_a_atribuicao_com_aspas` |
| O -c do git | `test_trava_le_o_c_so_do_shell` |
| Heredoc que é texto; Heredoc que um shell roda | `test_trava_nao_le_o_corpo_do_heredoc` |
| Repositório pelo ambiente | `test_trava_confere_o_pr_do_gh_repo` |
| Erro da própria trava | `test_trava_que_falha_barra` |
| Kit extraído dentro de outro repositório | `test_atualizar_recusa_o_kit_dentro_de_outro_repositorio` |
| Projeto mais novo que o kit | `test_atualizar_recusa_o_kit_atras_do_projeto` |
| Kit sem o git | `test_atualizar_recusa_o_kit_sem_git` |
| Kit clonado raso | `test_atualizar_recusa_o_kit_raso` |
| TDD com a stack do modelo | `test_tdd_com_a_stack_do_modelo_avisa` |
| Change 01 arquivada com a stack do modelo | `test_change_01_arquivada_avisa_os_cinco` |
| Stack preenchida | `test_stack_preenchida_nao_avisa` |
| Stack preenchida como o modelo pede | `test_stack_preenchida_como_o_modelo_pede_nao_avisa` |
| Projeto sem TDD | `test_projeto_sem_tdd_nao_avisa_a_stack` |

Antes do código falharam os testes que mudam o comportamento: 12 da trava, os 3 do `atualizar` e o do aviso da stack no gate 2. Os que guardam o que não pode mudar já passavam (a leitura do `core.hooksPath`, o git como argumento, a change 01 arquivada, a stack preenchida, o projeto sem TDD). No apply, o cenário "Projeto mais novo que o kit" mudou: o kit da 2.4 não tem a proteção, que nasce na 2.5, e o teste usa o kit atual com o projeto na 9.9. A abreviação `--forc` entrou na força (decisão 5), conservadora: o git provavelmente a recusa como ambígua.

Execução manual (tarefa 7.1), num projeto novo descartável: a trava barrou, com saída 2, `git -c core.hooksPath=/dev/null commit -m x`, `git commit --no-veri -m y`, `timeout 10 git push -f`, `if true; then git push -f; fi`, `bash -lc "git push -f"`, `git push --force-w` e `echo a#b; git push -f`, e deixou passar `git log --grep commit -n 3` e `echo git push -f`. Com o comum do projeto posto na 9.9 (num commit com `--no-verify`, só para montar o cenário, fora da trava), o `kit.py atualizar` recusou ("o projeto está na 9.9 e o kit na 2.5, atrás dele…"), com saída 1 e o `git status` limpo. A pasta foi apagada.

## Respostas à revisão

O `/opsx:verify` não achou crítico nem aviso e fez uma sugestão. A revisão de código, num agente sem o contexto da sessão, achou 6 pontos (1 alto, 5 médios), e rodou a trava sobre os comandos reais das sessões do usuário. O usuário delegou as escolhas ("sempre a melhor escolha"); a decisão de cada um:

1. **Aplicado.** A linha continuada com `\` escapava (`git push \` e `--force` na linha de baixo; também o `commit -n`). A trava junta as linhas antes de ler; teste `test_trava_barra_a_linha_continuada_e_a_atribuicao_com_aspas`.
2. **Aplicado.** A atribuição com aspas antes do comando (`GIT_SSH_COMMAND="ssh -v" git push -f`) tirava o `git` da posição de comando; o mesmo teste.
3. **Aplicado.** O `-c` de qualquer comando com valor que tem espaço era lido como shell e engolia o resto da linha (`git -c "user.name=Claude Bot" commit -n` passava). Só o shell; e o texto aninhado fica à parte; teste `test_trava_le_o_c_so_do_shell`.
4. **Aplicado.** A crase como separador barrava Markdown escrito por heredoc que citava um comando proibido. A trava não lê o corpo do heredoc, salvo o que um shell recebe; com isso também sai o falso positivo do heredoc que a proposta aceitava; teste `test_trava_nao_le_o_corpo_do_heredoc`.
5. **Aplicado.** O kit em ZIP extraído dentro de outro repositório respondia pelo repositório de cima e passava. A raiz do repositório tem de ser o kit; teste `test_atualizar_recusa_o_kit_dentro_de_outro_repositorio`.
6. **Aplicado em parte.** O `GH_REPO=` do comando vai ao `gh pr checks`; teste `test_trava_confere_o_pr_do_gh_repo`. O `cd ../outro && gh pr merge` fica fora, como a proposta já dizia.

Sugestão do verify, **aplicada**: o teste `test_trava_que_falha_barra` prova que um erro da trava barra.

Medida sobre os 15.720 comandos Bash reais das sessões do usuário, a trava da main contra a nova: nenhuma exceção; a nova deixou de barrar 8 falsos positivos (mensagens de commit em heredoc que citavam o `--no-verify`) e passou a barrar 7, todos acertos: 3 `git -c core.hooksPath=/dev/null`, 3 laços com `pgrep -f` e 1 `git push --force-with-lease` depois de uma linha continuada.
