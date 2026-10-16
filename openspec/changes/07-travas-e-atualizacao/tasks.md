# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. Cada teste novo é escrito antes do código e falha antes dele, salvo os que guardam o que já passa (dito na tarefa). Os testes da trava usam o `_guarda` de `testes/test_kit.py`, com um `gh` falso.

## 1. A trava do commit e o --no-verify abreviado

- [x] 1.1 O teste `test_trava_barra_o_hookspath_desligado` comprova os cenários "Hooks desligados por -c" e "Hooks trocados por git config"; falha antes do código (`-k test_trava_barra_o_hookspath_desligado`)
- [x] 1.2 O teste `test_trava_deixa_ler_e_gravar_o_hookspath_do_metodo` comprova o cenário "Leitura e valor do método"; já passa e guarda o que não pode mudar (`-k test_trava_deixa_ler_e_gravar_o_hookspath_do_metodo`)
- [x] 1.3 O teste `test_trava_barra_o_no_verify_abreviado` comprova o cenário "Opção abreviada"; falha antes do código (`-k test_trava_barra_o_no_verify_abreviado`)

## 2. O envio forçado em qualquer forma e o subcomando do git

- [x] 2.1 O teste `test_trava_barra_o_push_forcado_atras_de_outro_comando` comprova o cenário "Comando que envolve outro"; falha antes do código (`-k test_trava_barra_o_push_forcado_atras_de_outro_comando`)
- [x] 2.2 O teste `test_trava_barra_o_push_forcado_nas_palavras_do_shell` comprova o cenário "Palavras do shell"; falha antes do código (`-k test_trava_barra_o_push_forcado_nas_palavras_do_shell`)
- [x] 2.3 O teste `test_trava_barra_o_push_forcado_em_shell_aninhado` comprova o cenário "Shell dentro do comando"; falha antes do código (`-k test_trava_barra_o_push_forcado_em_shell_aninhado`)
- [x] 2.4 O teste `test_trava_barra_o_push_forcado_com_cerquilha_ou_aspa_sem_par` comprova o cenário "Cerquilha e aspa sem par"; falha antes do código (`-k test_trava_barra_o_push_forcado_com_cerquilha_ou_aspa_sem_par`)
- [x] 2.5 O teste `test_trava_barra_a_forca_abreviada_e_o_espelho` comprova o cenário "Opções abreviadas e espelho"; falha antes do código (`-k test_trava_barra_a_forca_abreviada_e_o_espelho`)
- [x] 2.6 O teste `test_trava_deixa_o_git_como_argumento` comprova o cenário "O git como argumento"; já passa e guarda o que não pode mudar (`-k test_trava_deixa_o_git_como_argumento`)
- [x] 2.7 O teste `test_trava_le_o_subcomando_depois_das_opcoes_globais` comprova os cenários "Palavra no argumento de outro subcomando" e "Opções globais antes do subcomando"; falha antes do código (`-k test_trava_le_o_subcomando_depois_das_opcoes_globais`)
- [x] 2.8 O `guarda.py` lê o comando como o design manda (decisões 1 a 6): sem comentário, com a crase, a segunda leitura da aspa sem par, a posição do comando, o shell aninhado, o subcomando depois das opções globais, o `core.hooksPath`, a força e o `--no-verify` abreviado; os testes dos grupos 1 e 2 passam, e o `test_trava_do_claude_barra_so_o_que_o_metodo_proibe` e o `test_trava_do_claude_le_as_opcoes_e_nao_o_texto` continuam passando

## 3. O merge e a trava que nunca libera por falha

- [x] 3.1 O teste `test_trava_aceita_o_merge_com_m` comprova o cenário "Merge com -m"; falha antes do código (`-k test_trava_aceita_o_merge_com_m`)
- [x] 3.2 O teste `test_trava_confere_o_pr_no_repositorio_indicado` comprova o cenário "Repositório indicado", com um `gh` falso que grava os argumentos; falha antes do código (`-k test_trava_confere_o_pr_no_repositorio_indicado`)
- [x] 3.3 O teste `test_trava_barra_a_verificacao_que_nao_responde` comprova o cenário "Verificação que não responde", com um `gh` falso que dorme além do prazo, encurtado no teste; falha antes do código (`-k test_trava_barra_a_verificacao_que_nao_responde`)
- [x] 3.4 O teste `test_trava_deixa_passar_a_entrada_sem_comando` comprova o cenário "Entrada sem comando"; falha antes do código (`-k test_trava_deixa_passar_a_entrada_sem_comando`)
- [x] 3.5 O `guarda.py` faz o merge e a falha como o design manda (decisões 7 e 8); os testes do grupo 3 passam

## 4. O atualizar que confere antes de mudar

- [x] 4.1 O teste `test_atualizar_recusa_o_kit_atras_do_projeto` comprova o cenário "Projeto mais novo que o kit", com o kit atual sobre um projeto cujo comum diz "Versão 9.9" (o kit da 2.4 não tem a proteção, que nasce na 2.5); falha antes do código (`-k test_atualizar_recusa_o_kit_atras_do_projeto`)
- [x] 4.2 O teste `test_atualizar_recusa_o_kit_sem_git` comprova o cenário "Kit sem o git", com o kit tirado por `git archive`; falha antes do código (`-k test_atualizar_recusa_o_kit_sem_git`)
- [x] 4.3 O teste `test_atualizar_recusa_o_kit_raso` comprova o cenário "Kit clonado raso", com um `git clone --depth 1`; falha antes do código (`-k test_atualizar_recusa_o_kit_raso`)
- [x] 4.4 O `kit.py atualizar` confere o kit e a versão antes da migração (design, decisão 9); os testes do grupo 4 passam, e os testes do `atualizar` de hoje continuam passando

## 5. O aviso da stack em dois tempos

- [x] 5.1 O `test_tdd_com_a_stack_do_modelo_avisa` passa a conferir só os três lugares do gate 2 e a falta do `check.sh` e do CI (cenário "TDD com a stack do modelo"); falha antes do código (`-k test_tdd_com_a_stack_do_modelo_avisa`)
- [x] 5.2 O teste `test_change_01_arquivada_avisa_os_cinco` comprova o cenário "Change 01 arquivada com a stack do modelo"; já passa e guarda o que não pode mudar (`-k test_change_01_arquivada_avisa_os_cinco`)
- [x] 5.3 O `test_stack_preenchida_como_o_modelo_pede_nao_avisa` passa a conferir o `openspec/config.yaml` no aviso que sobra, no lugar do `scripts/check.sh` (cenário "Stack preenchida como o modelo pede"), e o `test_stack_preenchida_nao_avisa` e o `test_projeto_sem_tdd_nao_avisa_a_stack` continuam comprovando os cenários "Stack preenchida" e "Projeto sem TDD" (`-k test_stack_preenchida`, `-k test_projeto_sem_tdd_nao_avisa_a_stack`)
- [x] 5.4 O `confere_regras.py` avisa o `check.sh` e o CI só com um spec em `openspec/specs/`, com a mensagem dos dois tempos (design, decisão 10); os testes do grupo 5 passam

## 6. O conjunto

- [x] 6.1 O docstring do `guarda.py` e a linha das travas no `CLAUDE-comum.md` (Armadilhas), se ela ficar desatualizada, acompanham; o conjunto de testes, o ruff (check e format), cada um sozinho, e o `openspec validate --all --no-interactive`, sem erro

## 7. Execução manual

- [x] 7.1 Numa pasta descartável do scratchpad: um projeto novo; a trava rodada com os comandos de contorno da auditoria, com a saída mostrada ao usuário; o commit com `git -c core.hooksPath=/dev/null` pedido pela trava e barrado; o `kit.py atualizar` sobre o projeto com o comum numa versão mais nova, recusado sem mudar nada; a pasta apagada

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit; a tag `v2.5` no commit do merge, enviada com o "sim" do usuário (`git push origin main v2.5`).
