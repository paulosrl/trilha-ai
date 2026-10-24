# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. Os testes

- [x] 1.1 Um `npm` e um `openspec` falsos num PATH só deles (com o `git` e o `claude` falso): o `openspec` responde ao `--version` com a versão gravada num arquivo, ao dry-run com o JSON dado e ao `update` gravando a chamada; o `npm install` grava a versão nova nesse arquivo. Os testes, que falham antes do código: `test_atualizar_openspec_instala_a_versao_do_kit` ("Versão da máquina diferente da do kit"), `test_atualizar_openspec_na_versao_igual_nao_instala` ("Versão da máquina igual à do kit"), `test_atualizar_sem_a_opcao_nao_mexe_no_openspec` ("Sem a opção"), `test_atualizar_openspec_recusa_o_update_que_apagaria` ("Perfil da máquina sem o que o projeto versiona"), `test_atualizar_openspec_sem_npm_falha` ("Máquina sem o npm"), `test_atualizar_openspec_update_com_erro_falha` ("Update com erro"), `test_atualizar_avisa_a_versao_diferente_do_kit` ("Versão diferente sem a opção") e `test_atualizar_versao_igual_sem_aviso_da_opcao` ("Versão igual sem a opção") (`python3 -m unittest discover -s testes -k test_atualizar_openspec -k test_atualizar_sem_a_opcao -k test_atualizar_avisa_a_versao -k test_atualizar_versao_igual`)

## 2. O código e o texto

- [x] 2.1 O `kit.py atualizar` com a opção `--openspec` (D1 a D4) e o aviso sem ela (D5); os testes da tarefa 1.1 e os do `atualizar` passam (`python3 -m unittest discover -s testes -k test_atualizar`)
- [x] 2.2 O uso no docstring do `kit.py` e a atualização de um projeto no `README.md` citam a opção; o `python3 ferramentas/kit.py --help` mostra a opção

## 3. Integração

- [x] 3.1 O conjunto dos testes, o ruff e o `openspec validate --all --no-interactive` passam
- [x] 3.2 A execução manual, por último, com o OpenSpec 1.15.0 de verdade: num projeto de teste feito pelo `kit.py novo` e inicializado com `openspec init --tools claude`, com um comando gerado alterado e commitado, o `kit.py atualizar --openspec` não chama o `npm` (a versão é a do kit), roda o update, e o comando volta ao que o OpenSpec gera; com o `npm` fora do PATH e um `openspec` falso que responde outra versão, a falha cita o `npm install`; o resultado vai a "Verificação", no `design.md`

## 4. As respostas ao verify e ao code review

Do `/opsx:verify` e do `/code-review high 17`, de 2026-10-24; a decisão de cada ponto fica em "Respostas à revisão", no `design.md`.

- [x] 4.1 Os testes dos cenários novos e dos achados, que falharam antes do código: `test_atualizar_openspec_avisa_os_apagados_fora_do_projeto` ("Apagados fora do projeto"), `test_atualizar_openspec_dry_run_com_erro_falha` ("Dry-run com erro"), `test_atualizar_openspec_nao_roda_com_a_migracao_que_falha` ("Migração do check.sh que falha"), `test_atualizar_avisa_o_ci_do_projeto_atras_do_kit` ("CI do projeto na versão anterior"), `test_atualizar_openspec_npm_com_erro_falha` e o `test_atualizar_openspec_recusa_o_update_que_apagaria` ajustado; o `test_atualizar_openspec_com_as_constantes_da_conferencia` protege as cópias (`python3 -m unittest discover -s testes -k test_atualizar_openspec -k test_atualizar_avisa_o_ci`)
- [x] 4.2 O `kit.py` com o `_openspec`, o `_avisar_o_ci_do_projeto`, o `_rodar` sem a entrada do terminal e com o prazo, e as mensagens novas; o conjunto dos testes, o ruff e a execução manual com o OpenSpec real passam, e o resultado vai a "Verificação"

## Workflow follow-up

- O `/opsx:verify` e o `/code-review` do pull request, por um agente sem o contexto da sessão; as respostas vão a "Respostas à revisão", no `design.md`.
- O `/opsx:archive`, os passos do `operations.archive` e o merge.
