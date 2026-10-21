# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`. Os testes do `tempo.py` usam a classe `HorasDeTrabalho` de `testes/test_kit.py`, com pastas temporárias e `TZ=UTC`. Cada teste novo é escrito antes do código e falha antes dele, salvo quando a tarefa diz que ele é guarda.

## 1. A versão

- [ ] 1.1 "Versão 2.10, de <data do apply>." no `modelo/trilha/CLAUDE-comum.md` e `2.10.0` no `plugins/sdd/.claude-plugin/plugin.json`, antes de qualquer outro arquivo de `modelo/` mudar (D7). Os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam

## 2. A conversa do repositório aninhado no resumo da versão 1

- [ ] 2.1 O teste `test_tempo_aninhado_no_resumo_antigo` comprova o cenário "Conversa do repositório aninhado no resumo antigo"; falha antes do código (`-k test_tempo_aninhado_no_resumo_antigo`)
- [ ] 2.2 O `_eventos` e o `main` fazem o D2; os testes do grupo e os de antes passam (`-k test_tempo`)

## 3. A leitura do arquivo que só cita a raiz

- [ ] 3.1 O teste `test_tempo_arquivo_que_so_cita_a_raiz` confere o D1, sem cenário próprio: um arquivo de outro repositório com uma linha que cita a raiz e muitas linhas com `"cwd"` fora dela é decodificado só na linha que cita a raiz (contando as chamadas do `_evento`, com o módulo carregado como no `test_tempo_email_com_espaco_e_vazio`); falha antes do código (`-k test_tempo_arquivo_que_so_cita_a_raiz`)
- [ ] 3.2 O `_eventos` faz o D1; os testes do grupo e os de antes passam (`-k test_tempo`)

## 4. Os e-mails

- [ ] 4.1 O `_rodar` dos testes tira o `GIT_AUTHOR_EMAIL` herdado da máquina, salvo quando o teste o passa; os testes de antes passam
- [ ] 4.2 Os testes `test_tempo_email_de_autor_do_git` e `test_tempo_email_de_autor_no_ambiente` comprovam os cenários "E-mail de autor do git" e "E-mail de autor no ambiente"; falham antes do código (`-k test_tempo_email_de_autor`)
- [ ] 4.3 O `test_tempo_sem_email_configurado` segue o cenário "Sem e-mail configurado" modificado; é guarda (`-k test_tempo_sem_email_configurado`)
- [ ] 4.4 O teste `test_tempo_colega_fora_do_aviso` comprova o cenário "Colega fora do aviso", com um e-mail com espaço gravado no `trilha.outro` (D4), e o `test_tempo_avisa_emails_de_fora` passa a conferir o `trilha.outro` no aviso, como no cenário "Aviso dos e-mails de fora"; falham antes do código (`-k test_tempo_colega_fora_do_aviso` e `-k test_tempo_avisa_emails_de_fora`)
- [ ] 4.5 O `_commits` e o `_aviso_dos_emails` fazem o D3 e o D4, e o `_ler_commits` passa à assinatura do D6, com o `test_tempo_email_com_espaco_e_vazio` e o `test_tempo_data_em_utc_com_z` ajustados a ela; os testes do grupo e os de antes passam (`-k test_tempo`)

## 5. O resumo de outra pasta

- [ ] 5.1 Os testes `test_tempo_pasta_antiga_que_ja_nao_existe`, `test_tempo_pasta_antiga_juntada_depois`, `test_tempo_pasta_antiga_que_sobrou_sem_repositorio` e `test_tempo_segundo_juntado_com_o_mesmo_nome` comprovam os cenários "Pasta antiga que já não existe", "Pasta antiga juntada depois da primeira execução", "Pasta antiga que sobrou sem o repositório" e "Segundo resumo juntado com o mesmo nome"; falham antes do código. O `test_tempo_pasta_trocada` e o `test_tempo_vizinho_de_nome_parecido` seguem como guarda (`-k test_tempo_pasta`, `-k test_tempo_segundo_juntado`, `-k test_tempo_vizinho_de_nome_parecido`)
- [ ] 5.2 O `tempo.py` faz o D5; os testes do grupo e os de antes passam (`-k test_tempo`)

## 6. A página

- [ ] 6.1 O `pagina_tempo_modelo.html` faz o plural do D6; o `test_tempo_um_dia_no_singular` passa (`-k test_tempo_um_dia_no_singular`), e a página de um dia com um commit, aberta no navegador, diz "1 dia com trabalho" e "1 commit"

## 7. Integração

- [ ] 7.1 O conjunto dos testes e o ruff passam
- [ ] 7.2 A execução manual, por último, no Xavier, só lendo, com uma pasta de dados vazia: o total igual ao da 2.9 (o D1 e as limpezas não mudam as horas), e o `git status --porcelain` igual antes e depois. Depois, numa cópia da pasta de dados, com o resumo renomeado como se a raiz tivesse vindo de outra pasta já apagada: as horas voltam e o antigo vira `.juntado`. O resultado vai a "Verificação", no `design.md`
