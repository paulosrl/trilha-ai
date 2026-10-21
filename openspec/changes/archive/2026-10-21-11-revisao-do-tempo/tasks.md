# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Os testes do `tempo.py` usam a classe `HorasDeTrabalho` de `testes/test_kit.py`, com pastas temporárias e `TZ=UTC`. Cada teste novo é escrito antes do código e falha antes dele, salvo quando a tarefa diz que ele é guarda.

## 1. A versão

- [x] 1.1 "Versão 2.9, de 2026-10-21." no `modelo/trilha/CLAUDE-comum.md` e `2.9.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar (D7). Os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam

## 2. Os testes de cada cenário

- [x] 2.1 O teste `test_tempo_clone_dentro_da_raiz` comprova o cenário "Clone dentro da raiz" (`-k test_tempo_clone_dentro_da_raiz`)
- [x] 2.2 O teste `test_tempo_worktree_da_raiz` comprova o cenário "Worktree do próprio repositório dentro da raiz", com um `git worktree add` de verdade; é guarda, porque a 2.8 já o conta (`-k test_tempo_worktree_da_raiz`)
- [x] 2.3 O teste `test_tempo_saida_e_volta_no_meio_da_conversa` comprova o cenário "Saída e volta no meio da conversa" (`-k test_tempo_saida_e_volta_no_meio_da_conversa`)
- [x] 2.4 O teste `test_tempo_subagente_noutra_pasta` comprova o cenário "Subagente noutra pasta"; é guarda, porque a 2.8 descarta os eventos de fora (`-k test_tempo_subagente_noutra_pasta`)
- [x] 2.5 O teste `test_tempo_commit_de_outro_autor` comprova o cenário "Commit de outro autor" (`-k test_tempo_commit_de_outro_autor`)
- [x] 2.6 O teste `test_tempo_sem_email_configurado` comprova o cenário "Sem e-mail configurado"; é guarda (`-k test_tempo_sem_email_configurado`)
- [x] 2.7 O teste `test_tempo_commit_a_meia_noite` comprova o cenário "Commit à meia-noite em ponto" (`-k test_tempo_commit_a_meia_noite`)
- [x] 2.8 O teste `test_tempo_commit_assinado` comprova o cenário "Commit assinado com a assinatura na saída do git", com o commit assinado por uma chave do `ssh-keygen` (`gpg.format=ssh`, sem `allowedSignersFile`) e o `log.showSignature` ligado (`-k test_tempo_commit_assinado`)
- [x] 2.9 O teste `test_tempo_data_em_utc_com_z` comprova o cenário "Data em UTC com Z", chamando a função que lê a saída do `git log` com uma linha de data em `Z`; é guarda no Python 3.12 (`-k test_tempo_data_em_utc_com_z`)
- [x] 2.10 Os testes `test_tempo_dados_uma_vez` e `test_tempo_nome_com_caracteres_especiais` comprovam os cenários "Dados uma vez" e "Nome com caracteres especiais" (`-k test_tempo_dados_uma_vez` e `-k test_tempo_nome_com_caracteres_especiais`)
- [x] 2.11 Os testes `test_tempo_pasta_trocada` e `test_tempo_vizinho_de_nome_parecido` comprovam os cenários "Pasta trocada" e "Vizinho de nome parecido"; o segundo é guarda (`-k test_tempo_pasta_trocada` e `-k test_tempo_vizinho_de_nome_parecido`)

## 3. O código

- [x] 3.1 O `tempo.py` faz o que as decisões D1 a D4 e D6 mandam; os testes do grupo 2 e os de antes passam, e o ruff passa
- [x] 3.2 O `tempo.py` e o `pagina_tempo_modelo.html` fazem a decisão D5; os testes do item 2.10 passam

## 5. Os outros e-mails do usuário

Achado na execução manual (4.2): no Xavier, os commits do usuário com o e-mail `paulolima@uepa.br` ficaram fora, porque o `user.email` é outro.

- [x] 5.1 Os testes `test_tempo_email_a_mais` e `test_tempo_avisa_emails_de_fora` comprovam os cenários "E-mail a mais" e "Aviso dos e-mails de fora"; falham antes do código (`-k test_tempo_email_a_mais` e `-k test_tempo_avisa_emails_de_fora`)
- [x] 5.2 O `tempo.py` lê o `trilha.email` (`git config --get-all`) e avisa os e-mails de fora (D3); os testes do grupo 5 e os de antes passam, e o ruff passa
- [x] 5.3 A execução manual de novo no Xavier, com o `trilha.email` dado pelo usuário: os dias de 26/05, 02/06 e 15/10 voltam com os commits dele; o resultado vai a "Verificação"

## 6. As respostas ao verify e ao code review

Do `/opsx:verify` e do `/code-review 11`, de 2026-10-21; a decisão de cada ponto fica em "Respostas à revisão", no `design.md`.

- [x] 6.1 O teste `test_tempo_conversa_retomada_noutro_arquivo` comprova o cenário "Conversa retomada noutro arquivo"; falha antes do código (`-k test_tempo_conversa_retomada_noutro_arquivo`)
- [x] 6.2 O `test_tempo_subagente_noutra_pasta` ganha, no arquivo do subagente, uma linha que cita o repositório, e continua comprovando o cenário "Subagente noutra pasta" (`-k test_tempo_subagente_noutra_pasta`)
- [x] 6.3 Os testes `test_tempo_horas_a_mais_da_2_8` e `test_tempo_conversa_apagada_no_resumo_antigo` comprovam os cenários "Horas a mais da 2.8" e "Conversa já apagada no resumo antigo"; o primeiro falha antes do código, e o segundo é guarda (`-k test_tempo_horas_a_mais_da_2_8` e `-k test_tempo_conversa_apagada_no_resumo_antigo`)
- [x] 6.4 O teste `test_tempo_robo_fora_do_aviso` comprova o cenário "Robô fora do aviso", e o `test_tempo_aviso_com_tres_emails` confere o limite de três; falham antes do código (`-k test_tempo_robo_fora_do_aviso` e `-k test_tempo_aviso_com_tres_emails`)
- [x] 6.5 O teste `test_tempo_nome_que_abre_comentario` comprova o cenário "Nome que abre um comentário"; falha antes do código (`-k test_tempo_nome_que_abre_comentario`)
- [x] 6.6 O teste `test_tempo_email_com_espaco_e_vazio` confere a leitura do e-mail com espaço e do vazio, sem cenário próprio; falha antes do código (`-k test_tempo_email_com_espaco_e_vazio`)
- [x] 6.7 O `tempo.py` com as correções, como as respostas do `design.md` dizem; o `_rodar` dos testes isola o git da máquina em todos; os testes e o ruff passam
- [x] 6.8 A execução manual de novo no Xavier, com uma pasta de dados vazia e também sobre o resumo da 2.8: o mesmo total nas duas; o resultado vai a "Verificação"

## 4. Integração

- [x] 4.1 O conjunto dos testes e o ruff passam, cada comando sozinho, com o código de saída conferido
- [x] 4.2 A execução manual, a última tarefa: rodar o `tempo.py` dentro do Xavier, só lendo, com o `XDG_DATA_HOME` numa pasta vazia, e também a 2.8 do mesmo jeito; conferir o `git status` igual e explicar a diferença dos totais; abrir a página e conferir o singular, o calendário sem semana a mais e nenhum erro no console. O resultado vai a "Verificação", no `design.md`

## Workflow follow-up

- `/opsx:verify` e o `/code-review <número do PR>`, numa sessão sem o contexto desta, com as respostas no `design.md`.
- `/opsx:archive` e os passos do `operations.archive`; o PR sai do rascunho.
- O merge com a verificação verde e o "sim" do usuário, e a tag `v2.9`.
