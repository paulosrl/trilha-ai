# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. A versão

- [x] 1.1 "Versão 2.11, de 2026-10-21." no `modelo/trilha/CLAUDE-comum.md` e `2.11.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar (D3). Os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam

## 2. A raiz antiga sem permissão

- [x] 2.1 O teste `test_tempo_pasta_antiga_sem_permissao` comprova o cenário "Pasta antiga sem permissão": tira a permissão da pasta acima da raiz antiga (e a devolve no fim), e se pula como root; falha antes do código (`-k test_tempo_pasta_antiga_sem_permissao`)
- [x] 2.2 O `_ainda_repositorio` faz o D1; os testes do `tempo.py` passam (`-k test_tempo`)

## 3. O aviso do resumo antigo que não se lê

- [x] 3.1 O `test_tempo_resumo_antigo_que_nao_se_le` passa a conferir o "corrija-o ou mova-o" do cenário "Resumo antigo que não se lê"; falha antes do código (`-k test_tempo_resumo_antigo_que_nao_se_le`)
- [x] 3.2 O aviso faz o D2; os testes do `tempo.py` passam (`-k test_tempo`)

## 4. Integração

- [x] 4.1 O conjunto dos testes e o ruff passam
- [x] 4.2 A execução manual, por último: numa pasta de dados à parte, com o resumo de uma raiz antiga sob uma pasta sem permissão, o comando roda num repositório de teste, termina com 0 e deixa o resumo antigo com o nome de antes; o resultado vai a "Verificação", no `design.md`

## 5. As respostas ao verify e ao code review

Do `/opsx:verify` e do `/code-review 13`, de 2026-10-21; a decisão de cada ponto fica em "Respostas à revisão", no `design.md`.

- [x] 5.1 O `test_tempo_pasta_antiga_sem_permissao` passa a conferir o aviso de que não deu para conferir em duas execuções, e os testes `test_tempo_raiz_antiga_com_caminho_invalido` e `test_tempo_subpasta_sem_permissao` comprovam os cenários "Raiz antiga com caminho inválido" e "Subpasta sem permissão"; os três falham antes do código, e os de permissão se pulam como root ou sem o `os.geteuid` (`-k sem_permissao`, `-k caminho_invalido`)
- [x] 5.2 O `tempo.py` com o `_tem_git` nos dois lugares e o aviso próprio (D1); os testes e o ruff passam
