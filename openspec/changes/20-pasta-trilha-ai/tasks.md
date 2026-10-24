# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`, e o conjunto com `python3 -m unittest discover -s testes`. O ruff roda com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha-ai/ ferramentas/` e com o mesmo `format --check`. Os testes vêm antes do código: os novos e os de hoje com o caminho novo falham antes da troca.

## 1. Os testes

- [x] 1.1 Nos testes de hoje, o caminho `trilha/` da pasta do método vira `trilha-ai/` (os auxiliares `_verifica_com_defeito`, `_avisos_da_stack`, `_confere_metodo`, `_aviso_do_plugin`, `_metodo_com_openspec`, `_gera_pagina`, `_guarda`, `_projeto_velho`, `_atualizar_com_openspec`, `_limpo`, `_versao_do_comum`, `_regras`, `_kit_falso`, `_regras_no_kit` e `_verifica`, e os 96 testes que citam a pasta), sem mudar o que eles conferem. São eles que comprovam os cenários MODIFIED, um a um, como na tabela do fim. Antes do código, eles falham (`python3 -m unittest discover -s testes`)
- [x] 1.2 Um auxiliar `_projeto_da_tag`, que faz o projeto com o `kit.py` de uma tag (o `_projeto_da_1_30` passa a usá-lo), e os testes novos da migração, que falham antes do código: `test_migra_a_pasta_trilha_da_2_18` ("Projeto da versão 2.18 migrado"), `test_migracao_avisa_o_arquivo_a_mais_da_trilha` ("Arquivo a mais na pasta trilha do método"), `test_atualizar_deixa_a_pasta_trilha_do_projeto` ("Pasta trilha que não é do método"), `test_migracao_avisa_as_citacoes_da_trilha` ("Arquivo do projeto que ainda cita a pasta trilha"), `test_migracao_nao_troca_o_caminho_do_projeto` ("Caminho do projeto que cita trilha"), `test_migracao_le_as_versoes_da_pasta_trilha` ("Versão de antes lida pelo nome novo") e `test_projeto_da_2_18_confere_com_o_kit_novo` ("Projeto da 2.18 com o kit novo ao lado", do link) (`python3 -m unittest discover -s testes -k test_migra -k test_atualizar_deixa_a_pasta_trilha -k test_projeto_da_2_18`)

## 2. O código e o texto

- [x] 2.1 O `git mv modelo/trilha modelo/trilha-ai` e os caminhos nos arquivos de `modelo/` (os verificadores, as travas, o `verifica.sh`, o comum, com a versão 2.19, o esqueleto, o `scripts/check.sh` e o `claude-settings.json`) e de `plugins/sdd/` (o `plugin.json` na 2.19.0 e o README) (D1, D9), e o link de transição `modelo/trilha` → `trilha-ai` (D8)
- [x] 2.2 No `kit.py`: os caminhos (D1), as versões antigas (D2), a migração da pasta (D3), a versão de antes (D4), a importação, o `check.sh`, a trava e o hooksPath (D5), as citações (D6) e a recusa (D7); no `confere_regras.py`, a tag lida pelas duas pastas (D2). Os testes das tarefas 1.1 e 1.2 passam (`python3 -m unittest discover -s testes`)
- [x] 2.3 Os textos do kit com o caminho novo: o `README.md`, o `CLAUDE.md` (com o link de transição), o `ferramentas/validar-projeto.md`, os Purpose dos specs `ferramenta-do-kit`, `hooks-do-git`, `horas-de-trabalho` e `trava-do-metodo`, o contexto do `openspec/config.yaml` e o CI (`.github/workflows/testes.yml`), que roda o ruff em `modelo/trilha-ai/`. Um `git grep -E "(^|[^[:alnum:]_-])trilha/"` fora dos registros históricos (as auditorias, o plano de migração, as changes arquivadas), desta change e dos requisitos dos specs principais (que o archive troca) só acha os nomes antigos de propósito: no `kit.py` (a migração, as versões antigas, a trava antiga), no `confere_regras.py` (as tags de antes da 2.19) e nos testes da migração

## 3. Integração

- [x] 3.1 O conjunto dos testes, o ruff e o `openspec validate --all --no-interactive` passam
- [ ] 3.2 A execução manual, por último, só no scratchpad, com o `TRILHA_AI` apontando para o kit: um projeto feito pelo `kit.py` da tag `v2.18`, com um `--vizinho` no `check.sh` e um documento que cita `trilha/`, commitado; antes da atualização, o `bash scripts/check.sh` dele termina com 0 com o kit novo ao lado (o link de transição); o `kit.py atualizar` atual o leva à `trilha-ai/`, avisa o documento e a sessão a reabrir, sugere o commit da cópia, e o `bash scripts/check.sh` termina com 0 de novo; o resultado vai a "Verificação", no `design.md`

## Os cenários e os testes

Cada cenário dos deltas e o teste de `testes/test_kit.py` que o comprova. Dois são comprovados só em parte por testes de antes desta change, cujo comportamento ela não muda: "Bloco da stack apagado" (o teste apaga o bloco `# Node`, não o `# Python`) e "Linha curta que falta" e "Chamada com os vizinhos" (o teste confere a função `_presente`, não a saída do `atualizar`).

| Capacidade | Requisito | Cenário | Teste |
| --- | --- | --- | --- |
| conferencias | Comum importado da pasta do método | Projeto no layout da pasta do método | `test_regras_aprovam_o_projeto_com_a_pasta_trilha`, `test_verificador_aprova_um_repositorio_feito_do_kit` |
| conferencias | Comum importado da pasta do método | Importação antiga | `test_regras_reprovam_a_importacao_antiga` |
| conferencias | Cópia idêntica da pasta do método | Pasta igual à do kit | `test_copia_da_pasta_trilha_igual_passa` |
| conferencias | Cópia idêntica da pasta do método | Trava editada no projeto | `test_copia_reprova_a_trava_editada` |
| conferencias | Cópia idêntica da pasta do método | Arquivo faltando ou a mais | `test_copia_reprova_arquivo_faltando_ou_a_mais` |
| conferencias | Cópia idêntica da pasta do método | Permissão de execução perdida | `test_copia_reprova_a_permissao_perdida` |
| conferencias | Cópia idêntica da pasta do método | Kit numa versão mais nova | `test_kit_mais_novo_compara_pela_tag_e_avisa` |
| conferencias | Cópia idêntica da pasta do método | Cópia divergente com o kit mais novo | `test_kit_mais_novo_reprova_a_copia_divergente_da_tag` |
| conferencias | Cópia idêntica da pasta do método | Kit sem as tags | `test_versao_sem_tag_no_kit_avisa_sem_comparar` |
| conferencias | Cópia idêntica da pasta do método | Versão que o kit não tem | `test_versao_que_o_kit_nao_tem_reprova` |
| conferencias | Cópia idêntica da pasta do método | Kit atrás do projeto | `test_kit_atras_do_projeto_avisa_sem_mandar_atualizar` |
| conferencias | Cópia idêntica da pasta do método | Comum sem a linha de versão | `test_comum_sem_versao_compara_com_a_copia_do_kit` |
| conferencias | Verificação fixa do projeto | Projeto novo | `test_verifica_aprova_o_projeto_novo` |
| conferencias | Verificação fixa do projeto | Vizinho repassado | `test_verifica_repassa_o_vizinho` |
| conferencias | Verificação fixa do projeto | Spec inválido | `test_verifica_reprova_quando_o_openspec_reprova` |
| conferencias | Verificação fixa do projeto | OpenSpec ausente | `test_verifica_sem_openspec_avisa` |
| conferencias | Verificação fixa do projeto | OpenSpec ausente no CI | `test_verifica_sem_openspec_no_ci_falha` |
| conferencias | Teto de tamanho das regras carregadas | Regras largas demais | `test_regras_largas_demais_reprovam` |
| conferencias | Teto de tamanho das regras carregadas | Linhas demais | `test_regras_com_linhas_demais_reprovam` |
| conferencias | Teto de tamanho das regras carregadas | Projeto novo dentro do teto | `test_regras_aprovam_o_projeto_com_a_pasta_trilha`, `test_verificador_aprova_um_repositorio_feito_do_kit` |
| conferencias | Travas desligadas pela configuração | Hooks desligados pela configuração local | `test_disable_all_hooks_local_avisa` |
| conferencias | Travas desligadas pela configuração | Hooks desligados pelo projeto | `test_disable_all_hooks_do_projeto_avisa` |
| conferencias | Travas desligadas pela configuração | Configuração local religa os hooks | `test_disable_all_hooks_religado_pelo_local_nao_avisa` |
| conferencias | Travas desligadas pela configuração | Travas ligadas no projeto novo | `test_projeto_novo_sem_aviso_de_trava` |
| conferencias | Regras por artefato iguais às do kit | Regras iguais às do kit | `test_config_com_as_regras_do_kit_passa` |
| conferencias | Regras por artefato iguais às do kit | Regras próprias | `test_config_com_regra_propria_reprova` |
| conferencias | Regras por artefato iguais às do kit | Linha do operations que falta | `test_config_sem_linha_do_operations_reprova` |
| conferencias | Regras por artefato iguais às do kit | Acréscimos próprios aceitos | `test_config_com_acrescimos_proprios_passa` |
| conferencias | Regras por artefato iguais às do kit | Projeto na versão anterior do kit | `test_config_da_versao_anterior_passa` |
| conferencias | Regras por artefato iguais às do kit | Projeto sem o config.yaml | `test_projeto_sem_config_nao_reprova_pelo_config` |
| conferencias | Link de transição da pasta antiga no kit | Projeto da 2.18 com o kit novo ao lado | `test_projeto_da_2_18_confere_com_o_kit_novo` |
| ferramenta-do-kit | Projeto novo com a pasta do método | Projeto novo verificado | `test_novo_cria_a_pasta_trilha_e_liga_as_travas` |
| ferramenta-do-kit | Projeto novo com a pasta do método | Trava do commit no projeto novo | `test_travas_ligadas_no_projeto_novo_e_a_do_commit_funciona` |
| ferramenta-do-kit | Atualização da pasta do método por inteiro | Arquivo que o kit tirou | `test_atualizar_apaga_da_trilha_o_que_o_kit_tirou` |
| ferramenta-do-kit | Migração do layout antigo | Projeto da versão 1.30 migrado | `test_migra_o_projeto_antigo` |
| ferramenta-do-kit | Migração do layout antigo | Hook de envio do projeto preservado | `test_migracao_preserva_o_pre_push_sem_aviso` |
| ferramenta-do-kit | Migração do layout antigo | Hook de envio do projeto que não pode rodar | `test_migracao_avisa_o_pre_push_que_nao_roda` |
| ferramenta-do-kit | Migração do layout antigo | Outro hook do projeto preservado | `test_migracao_preserva_e_avisa_o_hook_proprio` |
| ferramenta-do-kit | Migração do layout antigo | Migração parcial | `test_migracao_parcial_troca_a_importacao` |
| ferramenta-do-kit | Recusa da pasta trilha-ai de outra coisa | Pasta trilha do projeto | `test_atualizar_recusa_a_pasta_trilha_de_outra_coisa` |
| ferramenta-do-kit | Lista do método pelos arquivos versionados | Arquivo solto na pasta do kit | `test_lista_do_metodo_pelos_arquivos_versionados` |
| ferramenta-do-kit | Parte fixa do check.sh migrada | Parte fixa do kit com vizinhos | `test_migracao_troca_a_parte_fixa_com_vizinhos` |
| ferramenta-do-kit | Parte fixa do check.sh migrada | Parte fixa alterada pelo projeto | `test_migracao_avisa_a_parte_fixa_alterada` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Chamada com os vizinhos | `test_aviso_da_parte_fixa_preciso` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Linha curta que falta | `test_aviso_da_parte_fixa_preciso` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Linha que o projeto nunca copiou | `test_parte_fixa_avisa_a_linha_que_o_projeto_nunca_copiou` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Bloco da stack apagado | `test_parte_fixa_sem_o_bloco_da_stack` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Chamada dentro de uma função do projeto | `test_parte_fixa_aceita_a_chamada_dentro_de_uma_funcao`, `test_aviso_da_parte_fixa_preciso` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Bloco da parte da stack trocado | `test_parte_fixa_sem_o_bloco_da_parte_da_stack` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Ação atualizada pelo Dependabot | `test_parte_fixa_aceita_a_acao_atualizada_pelo_dependabot` |
| ferramenta-do-kit | Aviso da parte fixa que falta no projeto | Passo fixo do CI ao lado do comentário da stack | `test_parte_fixa_avisa_o_passo_do_ci_ao_lado_da_stack` |
| ferramenta-do-kit | Plugin declarado no projeto | Projeto novo com o plugin declarado | `test_novo_declara_o_plugin` |
| ferramenta-do-kit | Plugin declarado no projeto | Projeto atualizado com o settings.json próprio | `test_atualizar_soma_o_plugin_ao_settings_proprio` |
| ferramenta-do-kit | Plugin declarado no projeto | Plugin desligado pelo projeto | `test_atualizar_mantem_o_plugin_desligado` |
| ferramenta-do-kit | Plugin declarado no projeto | Atualização repetida | `test_atualizar_duas_vezes_nao_muda_o_settings` |
| ferramenta-do-kit | Settings.json somado do modelo inteiro | Chave nova no modelo | `test_soma_traz_toda_chave_do_modelo_sem_trocar_as_do_projeto` |
| ferramenta-do-kit | Settings.json somado do modelo inteiro | Trava de outra versão | `test_trava_de_outra_versao_troca_pela_do_modelo` |
| ferramenta-do-kit | Settings.json somado do modelo inteiro | Trava do modelo num grupo do projeto | `test_trava_do_modelo_num_grupo_do_projeto_nao_se_repete` |
| ferramenta-do-kit | Página regenerada só quando existe | Projeto sem a página | `test_atualizar_so_regera_a_pagina_que_existe` |
| ferramenta-do-kit | Página regenerada só quando existe | Projeto com a página | `test_atualizar_so_regera_a_pagina_que_existe` |
| ferramenta-do-kit | Update do OpenSpec que apagaria arquivos | Perfil da máquina sem o que o projeto versiona | `test_atualizar_openspec_recusa_o_update_que_apagaria` |
| ferramenta-do-kit | Update do OpenSpec que apagaria arquivos | De novo depois da recusa | `test_atualizar_openspec_roda_de_novo_depois_da_recusa` |
| ferramenta-do-kit | Update do OpenSpec que apagaria arquivos | Apagados fora do projeto | `test_atualizar_openspec_avisa_os_apagados_fora_do_projeto` |
| ferramenta-do-kit | Commit sugerido do atualizar | Só o OpenSpec muda | `test_atualizar_openspec_commit_so_do_openspec` |
| ferramenta-do-kit | Commit sugerido do atualizar | A cópia e o OpenSpec mudam | `test_atualizar_openspec_commit_da_copia_e_do_openspec` |
| ferramenta-do-kit | Commit sugerido do atualizar | Só a cópia muda, com o --openspec | `test_atualizar_openspec_commit_so_da_copia` |
| ferramenta-do-kit | Commit sugerido do atualizar | O dry-run previu, e o update não mudou | `test_atualizar_openspec_commit_previsto_e_nao_feito` |
| ferramenta-do-kit | Commit sugerido do atualizar | O update mudou sem o dry-run prever | `test_atualizar_openspec_commit_feito_sem_previsao` |
| ferramenta-do-kit | Commit sugerido do atualizar | Sem o --openspec | `test_atualizar_commit_sem_openspec` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Projeto da versão 2.18 migrado | `test_migra_a_pasta_trilha_da_2_18` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Arquivo a mais na pasta trilha do método | `test_migracao_avisa_o_arquivo_a_mais_da_trilha` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Pasta trilha que não é do método | `test_atualizar_deixa_a_pasta_trilha_do_projeto` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Arquivo do projeto que ainda cita a pasta trilha | `test_migracao_avisa_as_citacoes_da_trilha` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Caminho do projeto que cita trilha | `test_migracao_nao_troca_o_caminho_do_projeto` |
| ferramenta-do-kit | Migração da pasta trilha para trilha-ai | Versão de antes lida pelo nome novo | `test_migracao_le_as_versoes_da_pasta_trilha` |
| hooks-do-git | Envio pelo hook próprio do projeto | Hook próprio que aprova | `test_pre_push_repassa_ao_hook_proprio` |
| hooks-do-git | Envio pelo hook próprio do projeto | Hook próprio que reprova | `test_pre_push_recusa_quando_o_hook_proprio_reprova` |
| hooks-do-git | Envio pelo hook próprio do projeto | Código de saída e entrada repassados | `test_pre_push_repassa_o_codigo_e_a_entrada` |
| hooks-do-git | Envio pelo hook próprio do projeto | Projeto sem hook próprio | `test_pre_push_sem_hook_proprio_envia` |
| hooks-do-git | Hook próprio que não pode rodar | Hook próprio não executável | `test_pre_push_recusa_o_hook_proprio_nao_executavel` |
| hooks-do-git | Hook próprio que não pode rodar | Link simbólico quebrado | `test_pre_push_recusa_o_link_quebrado` |
| hooks-do-git | Hook próprio que não pode rodar | Repasse que volta a si mesmo | `test_pre_push_recusa_o_repasse_a_si_mesmo` |
| horas-de-trabalho | Só sob demanda | Nenhum gancho no modelo | `test_tempo_sem_gancho_no_modelo` |
| horas-de-trabalho | Só sob demanda | Fora de um repositório | `test_tempo_fora_de_repositorio` |
| trava-do-metodo | Trava do commit não se desliga | Hooks desligados por -c | `test_trava_barra_o_hookspath_desligado` |
| trava-do-metodo | Trava do commit não se desliga | Hooks trocados por git config | `test_trava_barra_o_hookspath_desligado` |
| trava-do-metodo | Trava do commit não se desliga | Leitura e valor do método | `test_trava_deixa_ler_e_gravar_o_hookspath_do_metodo` |

## Workflow follow-up

- A revisão dos artefatos, o `/opsx:verify` e o code review, por agentes sem o contexto da sessão; as respostas vão a "Respostas à revisão", no `design.md`.
- O `/opsx:archive`, os passos do `operations.archive`, o envio, o merge e a tag `v2.19`, com o "sim" do usuário.
