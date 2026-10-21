# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. Cada teste novo é escrito antes do código e falha antes dele, salvo os que guardam o que já passa (dito na tarefa). Os testes do OpenSpec usam um `openspec` falso no PATH, um script que responde a `config path`, a `--version` e a `update <pasta>` como o caso pede, sem a rede e sem o OpenSpec da máquina.

## 1. A parte fixa no kit.py (fora de `modelo/`)

- [x] 1.1 O teste `test_parte_fixa_avisa_a_linha_que_o_projeto_nunca_copiou` comprova o cenário "Linha que o projeto nunca copiou": um projeto na versão atual, com o `.gitignore` do modelo sem `*.log`; o `atualizar` avisa que falta `*.log`. Falha antes do código (`-k test_parte_fixa_avisa_a_linha_que_o_projeto_nunca_copiou`)
- [x] 1.2 O teste `test_parte_fixa_sem_o_bloco_da_stack` comprova o cenário "Bloco da stack apagado": o mesmo projeto, sem o bloco `# Python`; o `atualizar` não avisa `.venv/`. Também confere que o `modelo/gitignore` ainda tem as linhas `# Python` e `# Node` (design, decisão 1). Já passa, porque o aviso de hoje só olha o que mudou entre as versões, e guarda o que a comparação inteira não pode quebrar (`-k test_parte_fixa_sem_o_bloco_da_stack`)
- [x] 1.3 O `test_migracao_troca_a_parte_fixa_com_vizinhos` e o `test_aviso_da_parte_fixa_preciso` continuam comprovando os cenários "Chamada com os vizinhos" e "Linha curta que falta"; já passam e guardam o que não pode mudar (`-k test_migracao_troca_a_parte_fixa_com_vizinhos` e `-k test_aviso_da_parte_fixa_preciso`)
- [x] 1.4 O `test_atualizar_avisa_a_parte_fixa_que_mudou_no_kit` passa a esperar o texto "difere do modelo do kit" (design, "Testes que mudam")
- [x] 1.5 O `_avisar_parte_fixa` do `ferramentas/kit.py` compara o modelo atual inteiro, sem os blocos da stack do `.gitignore`, com o projeto, e mantém as linhas que sobram pela diferença entre as versões (design, decisão 1); os testes do grupo 1 passam

- [ ] 1.6 O teste `test_parte_fixa_aceita_a_chamada_dentro_de_uma_funcao` comprova o cenário "Chamada dentro de uma função do projeto": o `scripts/check.sh` do projeto com `etapa "regras" bash trilha/verifica.sh --vizinho trilha-ai`; o `atualizar` não avisa `bash trilha/verifica.sh`. O `test_aviso_da_parte_fixa_preciso` ganha o mesmo caso no `_presente` e mantém o `fi` diante de `find .`. Falha antes do código (`-k test_parte_fixa_aceita_a_chamada_dentro_de_uma_funcao` e `-k test_aviso_da_parte_fixa_preciso`)
- [ ] 1.7 O teste `test_parte_fixa_sem_o_bloco_da_parte_da_stack` comprova o cenário "Bloco da parte da stack trocado": o bloco "Parte da stack" do `scripts/check.sh` trocado por um comando da stack; o `atualizar` não avisa o `echo` dele. Confere também que o `modelo/scripts/check.sh` ainda tem o comentário `# Parte da stack`. Falha antes do código (`-k test_parte_fixa_sem_o_bloco_da_parte_da_stack`)
- [ ] 1.8 O `_presente` e a separação dos blocos do `ferramentas/kit.py` seguem a decisão 1 do design, com os dois casos novos; os testes do grupo 1 passam

## 2. A versão

- [x] 2.1 A linha "Versão 2.7, de <data>." no `modelo/trilha/CLAUDE-comum.md` e a `2.7.0` no `plugins/sdd/.claude-plugin/plugin.json`, só com o "sim" do usuário para a versão e antes de qualquer outro arquivo de `modelo/` mudar (design, decisão 6); o `test_kit_sem_mudanca_depois_da_tag`, o `test_versao_no_comum` e o teste da versão do plugin passam

## 3. As regras do config.yaml na conferência das regras

- [x] 3.1 O teste `test_config_com_as_regras_do_kit_passa` comprova o cenário "Regras iguais às do kit": um projeto do `kit.py novo`, conferido com `--fonte`, não reprova pelo `config.yaml`. Já passa e guarda o que não pode mudar (`-k test_config_com_as_regras_do_kit_passa`)
- [x] 3.2 O teste `test_config_com_regra_propria_reprova` comprova o cenário "Regras próprias": uma regra a mais no bloco `rules:`; a conferência reprova, citando `openspec/config.yaml` e `rules:`. Falha antes do código (`-k test_config_com_regra_propria_reprova`)
- [x] 3.3 O teste `test_config_sem_linha_do_operations_reprova` comprova o cenário "Linha do operations que falta": uma linha do `operations.archive` do kit apagada; a conferência reprova, citando o começo dela. Falha antes do código (`-k test_config_sem_linha_do_operations_reprova`)
- [x] 3.4 O teste `test_config_com_acrescimos_proprios_passa` comprova o cenário "Acréscimos próprios aceitos": uma linha a mais no `operations.archive` e a chave `githubCopilot` no topo; a conferência não reprova pelo `config.yaml` (`-k test_config_com_acrescimos_proprios_passa`)
- [x] 3.5 O teste `test_config_da_versao_anterior_passa` comprova o cenário "Projeto na versão anterior do kit": um kit de teste com a tag da versão do projeto e regras mudadas na cópia de trabalho; o projeto com as regras da tag não reprova, e com as da cópia de trabalho reprova (`-k test_config_da_versao_anterior_passa`)
- [x] 3.6 O teste `test_projeto_sem_config_nao_reprova_pelo_config` comprova o cenário "Projeto sem o config.yaml" (`-k test_projeto_sem_config_nao_reprova_pelo_config`)
- [x] 3.7 O `modelo/trilha/confere_regras.py` compara o `config.yaml` como o design manda (decisão 2), com a escolha da versão da pasta `trilha/`, e o texto de ajuda dele cita a comparação; os testes do grupo 3 passam

## 4. O OpenSpec na conferência do método

- [x] 4.1 O teste `test_openspec_avisa_as_skills_que_o_update_apagaria` comprova o cenário "Perfil só com comandos e skills no projeto": o `update` falso apaga a pasta `.claude/skills/openspec-propose` da pasta que recebe; o aviso cita o arquivo e `openspec config list`, e a saída é 0. Falha antes do código (`-k test_openspec_avisa_as_skills_que_o_update_apagaria`)
- [x] 4.2 O teste `test_openspec_em_dia_nao_avisa` comprova o cenário "Perfil igual aos arquivos do projeto": o `update` falso não muda nada; nenhum aviso sobre os arquivos gerados (`-k test_openspec_em_dia_nao_avisa`)
- [x] 4.3 O teste `test_openspec_ensaio_nao_toca_o_projeto` comprova o cenário "Projeto intacto depois do aviso": com o `update` falso que apaga, os arquivos do projeto ficam iguais, byte a byte (`-k test_openspec_ensaio_nao_toca_o_projeto`)
- [x] 4.4 O teste `test_openspec_ausente_nao_avisa` comprova o cenário "Máquina sem o OpenSpec": só a pasta do falso no PATH, sem `openspec` (`-k test_openspec_ausente_nao_avisa`)
- [x] 4.5 O teste `test_openspec_sem_configuracao_global_nao_ensaia` comprova o cenário "Máquina sem a configuração global": o `config path` falso aponta um arquivo que não existe, e o falso grava num registro cada chamada; nenhum `update` é chamado (`-k test_openspec_sem_configuracao_global_nao_ensaia`)
- [x] 4.6 O teste `test_openspec_ensaio_com_erro_nao_avisa` comprova o cenário "Ensaio com erro ou sem resposta no prazo": o `update` falso sai com 1; e, com o prazo trocado para 1 segundo no teste, um `update` que dorme 5 (`-k test_openspec_ensaio_com_erro_nao_avisa`)
- [x] 4.7 O teste `test_openspec_sem_arquivos_gerados_nao_ensaia` comprova o cenário "Projeto sem arquivos gerados": nenhum `update` é chamado (`-k test_openspec_sem_arquivos_gerados_nao_ensaia`)
- [x] 4.8 O teste `test_openspec_versao_diferente_da_do_ci_avisa` comprova o cenário "Versões diferentes": o falso responde `1.14.3` e o CI do projeto instala `@fission-ai/openspec@1.14.1`; o aviso cita as duas e o `npm install -g @fission-ai/openspec@1.14.1`, e a saída é 0. Falha antes do código (`-k test_openspec_versao_diferente_da_do_ci_avisa`)
- [x] 4.9 O teste `test_openspec_versao_igual_a_do_ci_nao_avisa` comprova o cenário "Versões iguais" (`-k test_openspec_versao_igual_a_do_ci_nao_avisa`)
- [x] 4.10 O teste `test_openspec_sem_versao_no_ci_nao_avisa` comprova o cenário "CI sem a versão fixada": sem o arquivo e com o arquivo sem o pin (`-k test_openspec_sem_versao_no_ci_nao_avisa`)
- [x] 4.11 O teste `test_trava_do_commit_nao_consulta_o_openspec` comprova o cenário "Commit sem consultar o OpenSpec": a trava do commit roda com o falso que grava cada chamada; o registro fica vazio (`-k test_trava_do_commit_nao_consulta_o_openspec`)
- [x] 4.12 O `modelo/trilha/confere_metodo.py` faz o ensaio e a comparação da versão como o design manda (decisões 3 a 5), atrás do `--sem-plugin`, com o texto de ajuda atualizado; os testes do grupo 4 passam

## 5. O texto do kit

- [x] 5.1 O passo 4 do `README.md` do kit pede o perfil do OpenSpec com skills e comandos, além do `verify` (design, decisão 6); conferido pela leitura do passo

## 6. O fechamento

- [x] 6.1 A suíte inteira (`python3 -m unittest discover -s testes`) e o ruff (`check` e `format --check`) verdes, cada um sozinho, com o código de saída conferido
- [ ] 6.2 A execução manual, com o usuário olhando: o `kit.py atualizar` numa cópia descartável do Xavier anterior ao alinhamento (o commit `e2115a8`) avisa as seis linhas do `.gitignore` fora dos blocos da stack e nenhuma do `scripts/check.sh`; a conferência das regras dessa cópia, com `--fonte`, reprova as regras próprias; a conferência do método, com o perfil antigo por `XDG_CONFIG_HOME`, avisa as skills que o `update` apagaria. O resultado de cada uma vai à seção "Verificação" do `design.md`
