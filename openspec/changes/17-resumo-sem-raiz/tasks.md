# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. A versão

- [x] 1.1 "Versão 2.17, de 2026-10-24." no `modelo/trilha/CLAUDE-comum.md` e `2.17.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar; os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam (`python3 -m unittest discover -s testes -k test_kit_sem_mudanca_depois_da_tag -k test_versao -k plugin`)

## 2. O aviso

- [x] 2.1 O `test_tempo_resumo_de_mesmo_nome_sem_raiz` comprova os cenários "Resumo de mesmo nome que não é JSON" (o aviso, o código 0 e o arquivo igual), "Resumo de mesmo nome sem a raiz" (uma lista e um objeto sem a raiz) e "Resumo de outro nome que não é JSON" (sem o aviso); falha antes do código (`python3 -m unittest discover -s testes -k test_tempo_resumo_de_mesmo_nome_sem_raiz`)
- [x] 2.2 O `_outros_resumos` devolve também os resumos de mesmo nome sem a raiz legível, e o `main` os avisa em toda execução; os testes do `tempo.py` passam (`python3 -m unittest discover -s testes -k test_tempo`)

## 3. Integração

- [x] 3.1 O conjunto dos testes, o ruff e o `openspec validate --all --strict --no-interactive` passam
- [x] 3.2 A execução manual, por último: num repositório de teste, com uma pasta dos dados à parte (`XDG_DATA_HOME`) que tem um `<nome>-0123abcd.json` que não é JSON, o `python3 -I trilha/tempo.py` do kit termina com 0, avisa citando o arquivo nas duas execuções seguidas, e o arquivo fica igual; o resultado vai ao `notas.md` da pasta da change

## Workflow follow-up

- O `/opsx:verify` e o `/code-review` do pull request, por um agente sem o contexto da sessão; as respostas vão ao `notas.md` da pasta da change, porque esta change não tem `design.md`.
- O `/opsx:archive`, os passos do `operations.archive`, o merge e a tag `v2.17`.
