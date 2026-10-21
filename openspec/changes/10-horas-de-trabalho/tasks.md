# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e com o mesmo `format --check`.

Cada teste novo é escrito antes do código e falha antes dele, salvo quando a tarefa diz que ele já passa.

Os testes do `tempo.py` rodam o script por subprocesso, com estas condições:
- `CLAUDE_CONFIG_DIR` e `XDG_DATA_HOME` apontam para pastas temporárias;
- `TZ=UTC`;
- um repositório git criado no teste, com commits de data fixada (`GIT_AUTHOR_DATE`);
- conversas de exemplo escritas no teste, no formato descrito no design (Context e D4);
- nada da rede e nada da máquina de quem roda.

## 1. A versão

- [x] 1.1 A linha "Versão 2.8, de <data>." no `modelo/trilha/CLAUDE-comum.md` e a `2.8.0` no `plugins/sdd/.claude-plugin/plugin.json`, aprovadas na descrição da change e feitas antes de qualquer outro arquivo de `modelo/` mudar. Os testes `test_kit_sem_mudanca_depois_da_tag`, `test_versao_no_comum` e o da versão do plugin passam (`python3 -m unittest discover -s testes`)

## 2. O comando, a leitura e o resumo

- [x] 2.1 O teste `test_tempo_sem_gancho_no_modelo` comprova o cenário "Nenhum gancho no modelo": nenhum comando de gancho do `modelo/claude-settings.json` cita `tempo.py`. Já passa e guarda o que não pode mudar (`-k test_tempo_sem_gancho_no_modelo`)
- [x] 2.2 O teste `test_tempo_fora_de_repositorio` comprova o cenário "Fora de um repositório": código diferente de 0, a mensagem e nenhum arquivo na pasta de dados (`-k test_tempo_fora_de_repositorio`)
- [x] 2.3 O teste `test_tempo_ignora_repositorio_vizinho` comprova o cenário "Conversa de outro repositório": a conversa com `cwd` em `<raiz>-antigo` não entra (`-k test_tempo_ignora_repositorio_vizinho`)
- [x] 2.4 O teste `test_tempo_conta_conversa_em_subpasta` comprova o cenário "Conversa numa subpasta", com uma conversa de subagente na mesma sessão (`-k test_tempo_conta_conversa_em_subpasta`)
- [x] 2.5 O teste `test_tempo_usa_claude_config_dir` comprova o cenário "Pasta de configuração trocada" (`-k test_tempo_usa_claude_config_dir`)
- [x] 2.6 O teste `test_tempo_resultado_de_ferramenta_e_da_ia` comprova o cenário "Resultado de ferramenta" (`-k test_tempo_resultado_de_ferramenta_e_da_ia`)
- [x] 2.7 O teste `test_tempo_metadados_nao_sao_pedido` comprova o cenário "Mensagem de metadados" (`-k test_tempo_metadados_nao_sao_pedido`)
- [x] 2.8 O teste `test_tempo_resumo_sem_texto` comprova o cenário "Nenhum texto no resumo": o resumo não contém "frase-que-nao-pode-vazar" (`-k test_tempo_resumo_sem_texto`)
- [x] 2.9 O teste `test_tempo_nao_toca_o_repositorio` comprova o cenário "Repositório intocado": o `git status --porcelain` é igual antes e depois (`-k test_tempo_nao_toca_o_repositorio`)
- [x] 2.10 O teste `test_tempo_usa_xdg_data_home` comprova o cenário "Pasta de dados trocada", com o resumo e a página em `<XDG_DATA_HOME>/trilha-ai/tempo/` (`-k test_tempo_usa_xdg_data_home`)
- [x] 2.11 O teste `test_tempo_conversa_apagada_continua` comprova o cenário "Conversa apagada depois da primeira execução": as horas de cada dia, lidas do resumo, são iguais nas duas execuções (`-k test_tempo_conversa_apagada_continua`)
- [x] 2.12 O teste `test_tempo_conversa_que_cresceu` comprova o cenário "Conversa que cresceu": o intervalo novo aparece uma vez só no resumo (`-k test_tempo_conversa_que_cresceu`)
- [x] 2.13 O `modelo/trilha/tempo.py` faz a raiz, a leitura das conversas, os eventos, os intervalos e o resumo como o design manda (D2, D3, D4, D6 e D9), com o texto de ajuda no início do arquivo, no molde do `gerar_pagina_sdd.py`. Os testes do grupo 2 passam, e o ruff passa

## 3. A apuração por dia

- [x] 3.1 O teste `test_tempo_dois_pedidos_e_duas_respostas` comprova o cenário "Dois pedidos e duas respostas": 31 minutos de total, 7 do usuário e 24 da IA sozinha (`-k test_tempo_dois_pedidos_e_duas_respostas`)
- [x] 3.2 O teste `test_tempo_pausa_longa_nao_conta` comprova o cenário "Pausa longa": 5 minutos de total (`-k test_tempo_pausa_longa_nao_conta`)
- [x] 3.3 O teste `test_tempo_conversas_em_paralelo` comprova o cenário "Duas conversas na mesma hora": 1 hora de total (`-k test_tempo_conversas_em_paralelo`)
- [x] 3.4 O teste `test_tempo_usuario_numa_ia_noutra` comprova o cenário "Usuário numa conversa enquanto a IA trabalha na outra": 30 minutos de total, 10 do usuário e 20 da IA (`-k test_tempo_usuario_numa_ia_noutra`)
- [x] 3.5 O teste `test_tempo_virada_do_dia` comprova o cenário "Intervalo na virada do dia": 10 minutos em cada dia (`-k test_tempo_virada_do_dia`)
- [x] 3.6 O teste `test_tempo_sessoes_de_commits` comprova o cenário "Sessões de commits": 2 horas, fonte "commits" (`-k test_tempo_sessoes_de_commits`)
- [x] 3.7 O teste `test_tempo_dia_com_conversa_usa_conversa` comprova o cenário "Dia com conversa e commits" (`-k test_tempo_dia_com_conversa_usa_conversa`)
- [x] 3.8 O teste `test_tempo_commit_em_duas_branches` comprova o cenário "Commit em duas branches" (`-k test_tempo_commit_em_duas_branches`)
- [x] 3.9 O teste `test_tempo_dia_de_commits_sem_divisao` comprova o cenário "Dia estimado pelos commits": fonte "commits", sem tempo do usuário nem da IA (`-k test_tempo_dia_de_commits_sem_divisao`)
- [x] 3.10 O `tempo.py` faz a união por dia, o corte na meia-noite local e a estimativa pelos commits como o design manda (D5 e D7). Os testes leem as horas dos dados embutidos na página (o JSON de `__DADOS__`), sem depender do visual. Os testes do grupo 3 passam, e o ruff passa

## 4. A página e a saída

- [x] 4.1 O teste `test_tempo_imprime_o_caminho_da_pagina` comprova o cenário "Caminho impresso" (`-k test_tempo_imprime_o_caminho_da_pagina`)
- [x] 4.2 O teste `test_tempo_pagina_sem_rede` comprova o cenário "Nada da rede": nenhum `src=` nem `href=` de folha de estilo, fonte, script ou imagem com `http://` ou `https://`, e nenhum `@import` ou `url(http` no estilo (`-k test_tempo_pagina_sem_rede`)
- [ ] 4.3 O `modelo/trilha/pagina_tempo_modelo.html` desenha, a partir do JSON, as seções da decisão D8 do design, com fontes do sistema, nos temas claro e escuro, sem rolagem lateral na largura de celular. O `tempo.py` grava a página e a saída de três linhas (D10). Os testes do grupo 4 passam
- [x] 4.4 O teste `test_tempo_avisa_guarda_padrao` comprova o cenário "Guarda padrão": o aviso cita `"cleanupPeriodDays": 3650`, e a saída é 0 (`-k test_tempo_avisa_guarda_padrao`)
- [x] 4.5 O teste `test_tempo_guarda_longa_sem_aviso` comprova o cenário "Guarda longa" (`-k test_tempo_guarda_longa_sem_aviso`)
- [x] 4.6 O aviso da guarda no `tempo.py`, como na decisão D9. Os testes 4.4 e 4.5 passam

## 5. O texto do kit

- [ ] 5.1 O passo 1 do `README.md` do kit ganha a guarda das conversas do Claude Code (`"cleanupPeriodDays": 3650` no `~/.claude/settings.json`) e o motivo. A tabela do passo 3 cita o `tempo.py` na linha da pasta `trilha/`. Conferido pela leitura dos dois trechos e por um `grep` de `tempo.py` no repositório inteiro

## 6. Integração

- [ ] 6.1 O conjunto dos testes e o ruff passam (os três comandos do início, cada um sozinho, com o código de saída conferido)
- [ ] 6.2 A execução manual, a última tarefa: rodar o `tempo.py` do kit dentro do Xavier, só lendo, e abrir a página gerada. Conferir que o `git status` do Xavier não mudou, que a página mostra 26/05/2026 como primeiro dia e que os dias com conversa trazem a divisão entre o usuário e a IA. Tirar uma captura de tela, no tamanho de computador e no de celular, e registrar o resultado no `design.md`

## Workflow follow-up

- `/opsx:verify` e o `/code-review <número do PR>`, numa sessão nova ou num agente sem o contexto da sessão, com as respostas na seção "Respostas à revisão" do `design.md`.
- `/opsx:archive`, com os passos do `operations.archive` do `openspec/config.yaml` do kit; o pull request sai do rascunho.
- O merge, com a verificação do GitHub verde e o "sim" do usuário, e a tag `v2.8`.
