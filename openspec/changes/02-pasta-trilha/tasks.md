# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`.

## 1. O molde em `modelo/trilha/` e a versão 2.0

- [x] 1.1 Mover com `git mv` o comum, os verificadores, a trava, o gerador e o modelo da página para `modelo/trilha/` e o `pre-commit` para `modelo/trilha/hooks/`; o `check.sh` fica em `modelo/scripts/`; tirar o atalho `CLAUDE-comum.md` da raiz; o CI do kit passa o ruff em `modelo/trilha/`; os testes do kit apontam para os caminhos novos e o `test_modelo_separado_e_inerte_no_kit` confere que a raiz não tem mais o atalho
- [x] 1.2 Subir o comum para "Versão 2.0" e o plugin para `2.0.0`; o `CLAUDE.md` do kit cita `modelo/trilha/CLAUDE-comum.md` e perde a frase do atalho; o `test_versao_do_plugin_igual_a_do_kit` e o `test_kit_sem_mudanca_depois_da_tag` passam

## 2. As conferências na pasta do método

- [x] 2.1 O `confere_regras.py` exige `@trilha/CLAUDE-comum.md` e lê o comum em `trilha/`; o teste `test_regras_aprovam_o_projeto_com_a_pasta_trilha` comprova o cenário "Projeto no layout da pasta do método" e o `test_regras_reprovam_a_importacao_antiga`, o cenário "Importação antiga"
- [x] 2.2 O `--fonte` compara a pasta `trilha/` com a `modelo/trilha/` do kit; o `test_copia_da_pasta_trilha_igual_passa` comprova "Pasta igual à do kit", o `test_copia_reprova_a_trava_editada`, "Trava editada no projeto", e o `test_copia_reprova_arquivo_faltando_ou_a_mais`, "Arquivo faltando ou a mais"
- [x] 2.3 Os avisos das travas desligadas citam `trilha/hooks` e `trilha/guarda.py`; o `confere_metodo.py` lê a versão em `trilha/CLAUDE-comum.md`; o gerador da página e o modelo dela citam `trilha/gerar_pagina_sdd.py`; os testes atuais das conferências e da página passam com os caminhos novos

## 3. A verificação fixa e as travas

- [x] 3.1 Escrever `modelo/trilha/verifica.sh` (as regras com a pasta do kit ou o aviso, o método com os argumentos recebidos e o `openspec validate --all --no-interactive` ou o aviso); o `modelo/scripts/check.sh` chama `bash trilha/verifica.sh` e guarda só o lugar da stack; o teste `test_verifica_aprova_o_projeto_novo` comprova o cenário "Projeto novo" da verificação
- [x] 3.2 O teste `test_verifica_repassa_o_vizinho` comprova o cenário "Vizinho repassado"
- [x] 3.3 O teste `test_verifica_reprova_quando_o_openspec_reprova` comprova o cenário "Spec inválido" (um `openspec` falso que reprova; o real fica para a execução manual)
- [x] 3.4 O teste `test_verifica_sem_openspec_avisa` comprova o cenário "OpenSpec ausente"
- [x] 3.5 O `modelo/trilha/hooks/pre-commit` chama `trilha/confere_regras.py` e `trilha/confere_metodo.py --sem-plugin`; o `modelo/claude-settings.json` liga `trilha/guarda.py`; o modelo do CI perde o passo próprio do `openspec validate`; os testes atuais das travas passam

## 4. A ferramenta: projeto novo, atualização e migração

- [x] 4.1 `SEM_MUDAR` lido de `modelo/trilha/`; o `novo` liga `core.hooksPath` em `trilha/hooks`; o teste `test_novo_cria_a_pasta_trilha_e_liga_as_travas` comprova o cenário "Projeto novo verificado", e o `test_travas_ligadas_no_projeto_novo_e_a_do_commit_funciona`, o cenário "Trava do commit no projeto novo"
- [x] 4.2 O `atualizar` deixa `trilha/` igual à do kit, apagando o que o kit tirou; o teste `test_atualizar_apaga_da_trilha_o_que_o_kit_tirou` comprova o cenário "Arquivo que o kit tirou"
- [x] 4.3 A migração do layout antigo (as cópias, a importação, o `core.hooksPath`, o hook do Claude Code sem duplicar) e `_caminhos` com os três lugares do comum; o teste `test_migra_o_projeto_antigo` comprova o cenário "Projeto da versão 1.30 migrado", num projeto criado pela ferramenta da versão antiga do kit (lida da tag)
- [x] 4.4 O teste `test_migracao_preserva_e_avisa_o_hook_proprio` comprova o cenário "Outro hook do projeto preservado"
- [x] 4.5 A troca da parte fixa do `check.sh` por texto exato, e o aviso da parte fixa aceitando a linha do kit como começo da linha do projeto; o teste `test_migracao_troca_a_parte_fixa_com_vizinhos` comprova o cenário "Parte fixa do kit com vizinhos"
- [x] 4.6 O teste `test_migracao_avisa_a_parte_fixa_alterada` comprova o cenário "Parte fixa alterada pelo projeto"
- [x] 4.7 Os testes atuais da ferramenta (`atualizar` com o settings existente, a sincronização das regras, o aviso da parte fixa, as recusas) passam com os caminhos novos

## 5. Os textos com os caminhos novos

- [x] 5.1 No comum, a dispensa de change passa a "a pasta `trilha/` e o que o `kit.py atualizar` escreve" e os caminhos citados passam aos de `trilha/`; no esqueleto, `@trilha/CLAUDE-comum.md` e o comentário do `check.sh`; o teste `test_dispensa_de_change_pela_pasta_trilha` confere a frase nova e a ausência da lista antiga, e os testes que fixam frases do comum são ajustados às frases novas
- [x] 5.2 No `README.md` do kit, a tabela e os passos com os caminhos de `modelo/trilha/` e o `verifica.sh` (só o mínimo; a reescrita é o item 9); `git grep -n "scripts/confere_\|scripts/guarda\|\.githooks/pre-commit\|@CLAUDE-comum.md"` fora de `openspec/` e dos testes da migração não acha caminho antigo apresentado como atual
- [x] 5.3 O conjunto de testes e o ruff, cada um sozinho, sem erro

## 6. Execução manual

- [ ] 6.1 Com o usuário olhando: migrar um clone descartável do heimdall com o `kit.py atualizar` e conferir o `bash scripts/check.sh` em `ok` (com o `openspec validate` real), um commit passando pela trava do commit, o aviso do `pre-push` próprio, a trava do Claude Code (`trilha/guarda.py`) barrando um `git push --force` e a página do projeto gerada por `python3 trilha/gerar_pagina_sdd.py`

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit, e a regra de versão do `CLAUDE.md` (a tag `v2.0` no merge commit da main, enviada com ele).
- Depois do merge, com a confirmação do usuário: atualizar o plugin da máquina para a 2.0.0 (`claude plugin update sdd@trilha-ai`).
- Cada projeto real migra com o `kit.py atualizar`, só com a ordem do usuário nomeando-o.
