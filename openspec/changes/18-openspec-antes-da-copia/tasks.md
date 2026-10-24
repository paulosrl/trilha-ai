# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Cada teste novo, ou ajustado ao comportamento novo, é escrito antes do código e falha antes dele.

## 1. Os testes

- [x] 1.1 O auxiliar `_atualizar_com_openspec` ganha um projeto com a `trilha/` editada e commitada (para mostrar que a cópia não aconteceu) e um jeito de rodar o `atualizar` de novo com outro dry-run. Os testes ajustados à recusa, que falham antes do código: `test_atualizar_openspec_recusa_o_update_que_apagaria` ("Perfil da máquina sem o que o projeto versiona": a recusa cita o arquivo, o `openspec config list` e o `--aceitar-apagados`; o `git status` vazio e a `trilha/` como estava), `test_atualizar_openspec_sem_npm_recusa` ("Máquina sem o npm"), `test_atualizar_openspec_npm_com_erro_recusa` ("Instalação que não muda o openspec do PATH", e o `npm` com erro) e `test_atualizar_openspec_dry_run_com_erro_recusa` ("Dry-run com erro"), que trocam os `..._falha` de hoje (`python3 -m unittest discover -s testes -k test_atualizar_openspec`)
- [x] 1.2 Os testes novos, que falham antes do código: `test_atualizar_openspec_roda_de_novo_depois_da_recusa` ("De novo depois da recusa"), `test_atualizar_openspec_aceita_os_apagados` ("Apagados aceitos"), `test_atualizar_openspec_sem_a_pasta_openspec_recusa` ("Projeto sem a pasta openspec": com a versão da máquina outra, nenhum `npm`, a recusa com o caminho de saída e o `git status` vazio) e `test_aceitar_apagados_sem_openspec_e_erro_de_uso` ("Opção sem o --openspec": o código 2, a frase de que o `--aceitar-apagados` só vale com o `--openspec`, sem "unrecognized arguments", nenhum `npm` nem update, o `git status` vazio) (`python3 -m unittest discover -s testes -k test_atualizar_openspec -k test_aceitar_apagados`)
- [x] 1.3 Os cenários que não mudam de comportamento seguem com os testes de hoje, que passam antes e depois do código: `test_atualizar_openspec_update_com_erro_falha` ("Update com erro"), `test_atualizar_openspec_avisa_os_apagados_fora_do_projeto` ("Apagados fora do projeto") e `test_atualizar_openspec_nao_roda_com_a_migracao_que_falha` ("Migração do check.sh que falha"), mais o novo `test_atualizar_openspec_nao_roda_com_a_chamada_que_sobra` (o mesmo cenário, com o bloco antigo, a chamada antiga uma vez e mais uma chamada aos `scripts/confere_*`: nenhum `npm` nem update), que passa antes do código e protege a previsão da D2 (`python3 -m unittest discover -s testes -k test_atualizar_openspec`)

## 2. O código e o texto

- [x] 2.1 No `kit.py`: a troca do `check.sh` numa função pura, usada pelo `_migrar_check` e pela previsão (D2); a preparação do OpenSpec antes da migração e da cópia, com a pasta `openspec/`, as falhas como `Recusa` e a mensagem dos apagados (D1, D3, D4); e a opção `--aceitar-apagados` no `main`, com o `parser.error` sem o `--openspec`, e o aviso dos apagados aceitos (D5). Os testes das tarefas 1.1 a 1.3 e os do `atualizar` passam (`python3 -m unittest discover -s testes -k test_atualizar -k test_aceitar_apagados`)
- [ ] 2.2 O uso no docstring do `kit.py`, o `help` das opções e a atualização de um projeto no `README.md` citam a opção nova, a recusa antes da cópia e a máquina que muda de versão mesmo com o projeto recusado; o `python3 ferramentas/kit.py --help` mostra as duas opções

## 3. Integração

- [ ] 3.1 O conjunto dos testes, o ruff e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último, com o OpenSpec 1.15.0 de verdade e só num projeto descartável no scratchpad, nunca num projeto real, com o `XDG_CONFIG_HOME` (e o `HOME`, se preciso) apontando para o scratchpad, para não tocar a configuração global: o projeto feito pelo `kit.py novo`, inicializado com `openspec init --tools claude`, com a `trilha/` editada e uma skill fora do perfil (um `SKILL.md` gerado copiado para `.claude/skills/openspec-onboard/`), tudo commitado; o `openspec update --dry-run --json` lista essa skill para apagar. O `kit.py atualizar --openspec` recusa, nomeia a skill e deixa o `git status` vazio; com `--aceitar-apagados`, termina com 0, a skill sai e a `trilha/` volta à do kit. O resultado vai a "Verificação", no `design.md`

## Workflow follow-up

- O `/opsx:verify` e o `/code-review` do pull request, por um agente sem o contexto da sessão; as respostas vão a "Respostas à revisão", no `design.md`.
- O `/opsx:archive`, os passos do `operations.archive` e o merge.
- Depois do merge, fora da change: o plano de migração e o roteiro de validação trocam o caminho à mão pelo `--aceitar-apagados`.
