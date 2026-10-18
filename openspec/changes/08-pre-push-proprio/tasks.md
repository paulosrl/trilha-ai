# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. Cada teste novo é escrito antes do código e falha antes dele, salvo os que guardam o que já passa (dito na tarefa). Os testes do envio usam um projeto feito pelo `kit.py novo` e um remoto `git init --bare` numa pasta temporária; enviam com o destino explícito (`git push <remoto> HEAD:refs/heads/main`), para não depender da configuração do git da máquina, e conferem o remoto pelo `git -C <remoto> rev-parse main`.

## 0. A versão

- [x] 0.1 A linha "Versão 2.6, de <data>." no `modelo/trilha/CLAUDE-comum.md` e a `2.6.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar (design, decisão 5); o `test_kit_sem_mudanca_depois_da_tag`, o `test_versao_no_comum` e o teste da versão do plugin passam

## 1. O envio pelo hook próprio

- [x] 1.1 O teste `test_pre_push_repassa_ao_hook_proprio` comprova o cenário "Hook próprio que aprova": o hook próprio grava os argumentos e a entrada num arquivo e sai com 0; o commit chega ao remoto, e o arquivo traz o nome e o endereço do remoto e a linha da referência. Falha antes do código (`-k test_pre_push_repassa_ao_hook_proprio`)
- [x] 1.2 O teste `test_pre_push_recusa_quando_o_hook_proprio_reprova` comprova o cenário "Hook próprio que reprova": o `git push` sai com código diferente de 0, e o remoto fica sem o commit. Falha antes do código (`-k test_pre_push_recusa_quando_o_hook_proprio_reprova`)
- [x] 1.3 O teste `test_pre_push_repassa_o_codigo_e_a_entrada` comprova o cenário "Código de saída e entrada repassados": roda o `trilha/hooks/pre-push` direto, com dois argumentos e uma linha na entrada, e um hook próprio que grava o que recebeu e sai com 3; confere o código 3 e o que o hook próprio recebeu. Falha antes do código (`-k test_pre_push_repassa_o_codigo_e_a_entrada`)
- [x] 1.4 O teste `test_pre_push_sem_hook_proprio_envia` comprova o cenário "Projeto sem hook próprio"; já passa e guarda o que não pode mudar (`-k test_pre_push_sem_hook_proprio_envia`)
- [x] 1.5 O teste `test_pre_push_recusa_o_hook_proprio_nao_executavel` comprova o cenário "Hook próprio não executável": o envio é recusado, e a mensagem cita `.githooks/pre-push` e a permissão de execução. Falha antes do código (`-k test_pre_push_recusa_o_hook_proprio_nao_executavel`)
- [x] 1.6 O teste `test_pre_push_recusa_o_link_quebrado` comprova o cenário "Link simbólico quebrado": o envio é recusado, e a mensagem cita `.githooks/pre-push`. Falha antes do código (`-k test_pre_push_recusa_o_link_quebrado`)
- [x] 1.7 O `modelo/trilha/hooks/pre-push` faz o repasse como o design manda (decisões 1 e 2) e entra no git executável, com `git add`, antes de rodar os testes do grupo: o `kit.py novo` só copia o que o git do kit lista. O `git ls-files -s modelo/trilha/hooks` dá `100755` para ele; os testes do grupo 1 passam, e o `test_copia_da_pasta_trilha_igual_passa` e o `test_copia_reprova_a_permissao_perdida` continuam passando

## 2. A migração sem o aviso do pre-push

- [x] 2.1 O teste `test_migracao_preserva_o_pre_push_sem_aviso` comprova o cenário "Hook de envio do projeto preservado": o `.githooks/pre-push` fica igual, e a saída do `atualizar` não diz que ele não roda mais. Falha antes do código (`-k test_migracao_preserva_o_pre_push_sem_aviso`)
- [x] 2.2 O `test_migracao_preserva_e_avisa_o_hook_proprio` passa a usar um `.githooks/commit-msg` e comprova o cenário "Outro hook do projeto preservado"; já passa e guarda o que não pode mudar (`-k test_migracao_preserva_e_avisa_o_hook_proprio`)
- [x] 2.3 O `test_migra_o_projeto_antigo` e o `test_migracao_parcial_troca_a_importacao` continuam comprovando os cenários "Projeto da versão 1.30 migrado" e "Migração parcial", sem mudança (`-k test_migra_o_projeto_antigo` e `-k test_migracao_parcial_troca_a_importacao`)
- [x] 2.4 O `_migrar` do `ferramentas/kit.py` deixa de avisar sobre o `pre-push` (design, decisão 3); os testes do grupo 2 passam

## 3. O texto do método

- [ ] 3.1 O teste `test_comum_cita_o_hook_de_envio_proprio` confere que o comum cita o `.githooks/pre-push` e o `trilha/hooks/pre-push`; falha antes do texto (`-k test_comum_cita_o_hook_de_envio_proprio`)
- [ ] 3.2 O `modelo/trilha/CLAUDE-comum.md` ganha a meia frase no item "As travas do kit não se contornam"; o teste 3.1 e o `test_comum_cabe_em_metade_do_teto` passam
- [ ] 3.3 O `README.md` cita o `hooks/pre-push` na linha da pasta `trilha/`, ao lado do `hooks/pre-commit`; conferido pela leitura da linha

## 4. A verificação de ponta a ponta

- [ ] 4.1 O conjunto dos testes e o ruff passam, cada um sozinho, com o código de saída 0
- [ ] 4.2 Execução manual: num clone descartável do Heimdall, com um remoto `git init --bare` local, o `kit.py atualizar` da branch não avisa sobre o `.githooks/pre-push`; o `git config core.hooksPath` dá `trilha/hooks`; e um `git push` ao remoto local roda o pre-push do Heimdall (o encoding, o `openspec validate --specs` e os testes pareados), com a saída registrada na seção "Verificação" do `design.md`

## Workflow follow-up

- O `/opsx:verify` e o `/code-review <número do PR>`, numa sessão nova ou num agente sem o contexto desta; cada sugestão, aplicada ou recusada com o motivo, vai à seção "Respostas à revisão" do `design.md`.
- O `/opsx:archive` e os passos do `operations.archive` do `openspec/config.yaml`; o pull request sai do rascunho.
- O merge com a verificação verde e o "sim" do usuário, e a tag `v2.6`.
