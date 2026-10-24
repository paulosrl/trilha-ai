# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha-ai/ ferramentas/` e com o mesmo `format --check`. Os testes vêm antes do código, e os novos falham antes dele.

## 1. Os testes

- [ ] 1.1 Os testes novos da ferramenta, que falham antes do código: `test_migracao_cria_o_link_com_citacao` ("Projeto que ainda cita a pasta antiga"), `test_migracao_sem_citacao_nao_cria_o_link` ("Projeto que não cita mais a pasta antiga"), `test_atualizar_mantem_o_link_com_citacao` ("Link que fica"), `test_atualizar_tira_o_link_sem_citacao` ("Link que sai") e, no `test_migracao_avisa_as_citacoes_da_trilha`, as citações por variável do shell e pelo nome entre aspas (D2) (`python3 -m unittest discover -s testes -k link -k test_migracao_avisa_as_citacoes`)
- [ ] 1.2 Os testes novos da conferência das regras, que falham antes do código: `test_regras_avisam_o_link_de_transicao` ("Projeto com o link de transição"), `test_regras_sem_link_na_pasta_trilha_propria` ("Pasta trilha própria do projeto"), `test_regras_trava_ligada_pelo_link` ("Trava do commit pelo link de transição") e `test_regras_trava_antiga_sem_link_desligada` ("Trava do commit na pasta antiga sem o link") (`python3 -m unittest discover -s testes -k test_regras_avisam_o_link -k test_regras_sem_link -k test_regras_trava`)

## 2. O código e o texto

- [ ] 2.1 No `kit.py`: a busca mais larga (D2), o link reconhecido (D3), criado na migração com citação (D1) e mantido ou tirado no atualizar seguinte (D4); a recusa do link continua para o que não aponta para a `trilha-ai/`. Os testes da tarefa 1.1, o `test_migracao_recusa_a_trilha_que_e_link` e o `test_migra_a_pasta_trilha_da_2_18` passam (`python3 -m unittest discover -s testes -k link -k test_migra`)
- [ ] 2.2 No `confere_regras.py`, os avisos do link e da trava ligada pelo link (D5), com a docstring; os testes da tarefa 1.2 e o `test_regras_aprovam_o_projeto_com_a_pasta_trilha` passam (`python3 -m unittest discover -s testes -k test_regras`)
- [ ] 2.3 A versão 2.20 no `modelo/trilha-ai/CLAUDE-comum.md` e o `plugins/sdd/.claude-plugin/plugin.json` na 2.20.0 (D6), e o `ferramentas/validar-projeto.md` com o link de transição, que não é migração pela metade; o teste da versão do plugin passa (`python3 -m unittest discover -s testes -k plugin`)

## 3. Integração

- [ ] 3.1 O conjunto dos testes, o ruff (`check` e `format --check`) e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último, só no scratchpad: um clone descartável do Heimdall (2.15), com o `core.hooksPath` em `trilha/hooks`, levado pelo `kit.py atualizar --openspec` do kit desta change; a saída diz que criou o link; com a cópia commitada no clone, o `bash scripts/check.sh` e o `.githooks/pre-push` do Heimdall terminam com 0, e a trava do commit roda; o resultado vai a "Verificação", no `design.md`

## Os cenários e os testes

| Capacidade | Requisito | Cenário | Teste |
| --- | --- | --- | --- |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Projeto da versão 2.18 migrado | `test_migra_a_pasta_trilha_da_2_18` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Arquivo a mais na pasta trilha do método | `test_migracao_avisa_o_arquivo_a_mais_da_trilha` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Pasta trilha que não é do método | `test_atualizar_deixa_a_pasta_trilha_do_projeto` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Arquivo do projeto que ainda cita a pasta trilha | `test_migracao_avisa_as_citacoes_da_trilha` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Importação com espaço no fim | `test_migracao_troca_a_importacao_com_espaco` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Arquivo ignorado na pasta trilha do método | `test_migracao_recusa_o_ignorado_na_trilha` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Pasta trilha do método que é um link simbólico | `test_migracao_recusa_a_trilha_que_e_link` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Caminho do projeto que cita trilha | `test_migracao_nao_troca_o_caminho_do_projeto` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Versão de antes lida pelo nome novo | `test_migracao_le_as_versoes_da_pasta_trilha` |
| ferramenta-do-kit | Link de transição criado na migração | Projeto que ainda cita a pasta antiga | `test_migracao_cria_o_link_com_citacao` |
| ferramenta-do-kit | Link de transição criado na migração | Projeto que não cita mais a pasta antiga | `test_migracao_sem_citacao_nao_cria_o_link` |
| ferramenta-do-kit | Link de transição no atualizar seguinte | Link que fica | `test_atualizar_mantem_o_link_com_citacao` |
| ferramenta-do-kit | Link de transição no atualizar seguinte | Link que sai | `test_atualizar_tira_o_link_sem_citacao` |
| conferencias | Travas desligadas pela configuração | Hooks desligados pela configuração local | `test_disable_all_hooks_local_avisa` |
| conferencias | Travas desligadas pela configuração | Hooks desligados pelo projeto | `test_disable_all_hooks_do_projeto_avisa` |
| conferencias | Travas desligadas pela configuração | Configuração local religa os hooks | `test_disable_all_hooks_religado_pelo_local_nao_avisa` |
| conferencias | Travas desligadas pela configuração | Travas ligadas no projeto novo | `test_regras_aprovam_o_projeto_com_a_pasta_trilha` |
| conferencias | Travas desligadas pela configuração | Trava do commit pelo link de transição | `test_regras_trava_ligada_pelo_link` |
| conferencias | Travas desligadas pela configuração | Trava do commit na pasta antiga sem o link | `test_regras_trava_antiga_sem_link_desligada` |
| conferencias | Aviso do link de transição no projeto | Projeto com o link de transição | `test_regras_avisam_o_link_de_transicao` |
| conferencias | Aviso do link de transição no projeto | Pasta trilha própria do projeto | `test_regras_sem_link_na_pasta_trilha_propria` |
