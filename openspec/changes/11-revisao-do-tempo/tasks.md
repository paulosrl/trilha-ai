# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Os testes do `tempo.py` usam a classe `HorasDeTrabalho` de `testes/test_kit.py`, com pastas temporárias e `TZ=UTC`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. A versão

- [ ] 1.1 "Versão 2.9, de 2026-10-21." no `modelo/trilha/CLAUDE-comum.md` e `2.9.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar (D8). Os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam

## 2. Os testes de cada cenário

- [ ] 2.1 O teste `test_tempo_saida_e_volta_no_meio_da_conversa` comprova o cenário "Saída e volta no meio da conversa" (`-k test_tempo_saida_e_volta_no_meio_da_conversa`)
- [ ] 2.2 O teste `test_tempo_clone_dentro_da_raiz` comprova o cenário "Clone dentro da raiz" (`-k test_tempo_clone_dentro_da_raiz`)
- [ ] 2.3 O teste `test_tempo_commit_de_outro_autor` comprova o cenário "Commit de outro autor" (`-k test_tempo_commit_de_outro_autor`)
- [ ] 2.4 O teste `test_tempo_sem_email_configurado` comprova o cenário "Sem e-mail configurado"; ele já passa e guarda o que não pode mudar (`-k test_tempo_sem_email_configurado`)
- [ ] 2.5 O teste `test_tempo_assinatura_na_saida_do_git` comprova o cenário "Assinatura na saída do git", com `log.showSignature` ligado no repositório de teste (`-k test_tempo_assinatura_na_saida_do_git`)
- [ ] 2.6 O teste `test_tempo_data_em_utc_com_z` comprova o cenário "Data em UTC com Z", chamando a leitura dos commits com uma saída do git falsa, porque o git desta máquina escreve `+00:00` (`-k test_tempo_data_em_utc_com_z`)
- [ ] 2.7 O teste `test_tempo_commit_a_meia_noite` comprova o cenário "Commit à meia-noite em ponto" (`-k test_tempo_commit_a_meia_noite`)
- [ ] 2.8 Os testes `test_tempo_dados_uma_vez` e `test_tempo_nome_com_caracteres_especiais` comprovam os cenários "Dados uma vez" e "Nome com caracteres especiais" (`-k test_tempo_dados_uma_vez` e `-k test_tempo_nome_com_caracteres_especiais`)
- [ ] 2.9 O teste `test_tempo_pasta_trocada` comprova o cenário "Pasta trocada" (`-k test_tempo_pasta_trocada`)

## 3. O código

- [ ] 3.1 O `tempo.py` faz o que as decisões D1 a D4, D6 e D7 mandam; os testes do grupo 2 e os de antes passam, e o ruff passa
- [ ] 3.2 O `tempo.py` e o `pagina_tempo_modelo.html` fazem a decisão D5: os marcadores trocados uma vez, o título protegido, o comentário sem os marcadores, o plural, a contagem das semanas e a função `clock` fora. Os testes do item 2.8 passam

## 4. Integração

- [ ] 4.1 O conjunto dos testes e o ruff passam, cada comando sozinho, com o código de saída conferido
- [ ] 4.2 A execução manual, a última tarefa: rodar o `tempo.py` dentro do Xavier, só lendo; conferir o `git status` igual, comparar o total com o da 2.8 e explicar a diferença; abrir a página e conferir o singular, o calendário sem semana a mais e nenhum erro no console. O resultado vai a "Verificação", no `design.md`

## Workflow follow-up

- `/opsx:verify` e o `/code-review <número do PR>`, numa sessão sem o contexto desta, com as respostas no `design.md`.
- `/opsx:archive` e os passos do `operations.archive`; o PR sai do rascunho.
- O merge com a verificação verde e o "sim" do usuário, e a tag `v2.9`.
