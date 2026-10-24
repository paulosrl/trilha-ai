# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Cada teste novo ou ajustado é escrito antes do código e falha antes dele.

## 1. A versão

- [x] 1.1 "Versão 2.16, de 2026-10-24." no `modelo/trilha/CLAUDE-comum.md` e `2.16.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar (D4). Os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam
- [x] 1.2 A 1.15.0 no `modelo/.github/workflows/verificacao.yml`, no `.github/workflows/testes.yml` e no `README.md`; o `test_openspec_versao_diferente_da_do_ci_avisa` e o `openspec` falso dos testes passam à 1.15.0 como a versão do CI (`-k test_openspec_versao`)

## 2. O dry-run do OpenSpec

- [x] 2.1 O `_openspec_falso` passa a responder ao `update --dry-run --json` com o JSON dado (um auxiliar monta a lista de `changes`), e os testes do ensaio passam a ele, falhando antes do código: `test_openspec_avisa_as_skills_que_o_update_apagaria` ("Perfil só com comandos e skills no projeto"), `test_openspec_em_dia_nao_avisa` ("Perfil igual aos arquivos do projeto"), `test_openspec_ensaio_nao_toca_o_projeto` ("Projeto intacto depois do aviso"), `test_openspec_ensaio_nao_muda_a_configuracao_da_maquina` ("Configuração da máquina intacta", com o caminho absoluto na lista), `test_openspec_avisa_o_que_criaria_e_trocaria` ("Arquivos que ele criaria ou trocaria"), `test_openspec_aviso_corta_a_lista`, `test_openspec_ensaio_sem_a_rede` e `test_openspec_nome_fora_do_utf8_nao_derruba` (`-k test_openspec`)
- [x] 2.2 Os testes do silêncio: `test_openspec_ausente_nao_avisa` ("Máquina sem o OpenSpec"), `test_openspec_sem_configuracao_global_nao_ensaia` ("Máquina sem a configuração global"), `test_openspec_ensaio_com_erro_nao_avisa` ("Ensaio com erro ou sem resposta no prazo"), o novo `test_openspec_dry_run_com_falhas_nao_avisa` ("Dry-run com falhas ou sem o JSON esperado": `failures` não vazio, saída que não é JSON e JSON sem `changes`), o novo `test_openspec_sem_dry_run_nao_avisa` ("OpenSpec sem o dry-run": a opção recusada com erro, e o aviso da versão presente) e `test_openspec_sem_arquivos_gerados_nao_ensaia` ("Projeto sem arquivos gerados"); os novos falham antes do código (`-k test_openspec`)
- [x] 2.3 O `_aviso_do_update` faz o D1, o D2 e o D3, e as constantes e importações que só o ensaio usava saem; os testes do OpenSpec passam (`-k test_openspec`)

## 3. Integração

- [ ] 3.1 O conjunto dos testes, o ruff e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último, com o OpenSpec 1.15.0 de verdade: num projeto de teste feito pelo `kit.py novo`, com um comando gerado alterado e outro apagado, a conferência do método avisa os dois em "trocaria" e "criaria", e o projeto fica igual; com a configuração global sem o perfil (num `XDG_CONFIG_HOME` à parte), o aviso não a cita e ela fica igual; o resultado vai a "Verificação", no `design.md`

## Workflow follow-up

- O `/opsx:verify` e o `/code-review` do pull request, por um agente sem o contexto da sessão; as respostas vão a "Respostas à revisão", no `design.md`.
- O `/opsx:archive`, os passos do `operations.archive` e o merge com a tag `v2.16`.
