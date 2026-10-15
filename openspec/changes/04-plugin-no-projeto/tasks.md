# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. O plugin declarado no projeto

- [x] 1.1 O `modelo/claude-settings.json` ganha `enabledPlugins` (`sdd@trilha-ai` verdadeiro) e `extraKnownMarketplaces` (`trilha-ai`, origem `github`, repositório `paulosrl/trilha-ai`); a soma do `kit.py` passa a ler as duas chaves do modelo, entrada por entrada, só quando falta (design, decisão 1); o teste `test_novo_declara_o_plugin` comprova o cenário "Projeto novo com o plugin declarado" (`-k test_novo_declara_o_plugin`)
- [x] 1.2 O teste `test_atualizar_soma_o_plugin_ao_settings_proprio` comprova o cenário "Projeto atualizado com o settings.json próprio" (`-k test_atualizar_soma_o_plugin_ao_settings_proprio`), e o `test_atualizar_soma_a_trava_ao_settings_que_ja_existe` continua passando
- [x] 1.3 O teste `test_atualizar_mantem_o_plugin_desligado` comprova o cenário "Plugin desligado pelo projeto" (`-k test_atualizar_mantem_o_plugin_desligado`)
- [x] 1.4 O teste `test_atualizar_duas_vezes_nao_muda_o_settings` comprova o cenário "Atualização repetida" (`-k test_atualizar_duas_vezes_nao_muda_o_settings`)

## 2. O comando de instalação por máquina

- [x] 2.1 O `kit.py` ganha a constante do comando `claude plugin install sdd@trilha-ai --scope project`; o `novo` a põe nos próximos passos e o teste `test_novo_imprime_o_comando_de_instalacao` comprova o cenário "Comando no projeto novo" (`-k test_novo_imprime_o_comando_de_instalacao`)
- [x] 2.2 O `atualizar` imprime o comando ao fim, sem recusa; o teste `test_atualizar_imprime_o_comando_de_instalacao` comprova o cenário "Comando na atualização" (`-k test_atualizar_imprime_o_comando_de_instalacao`)
- [x] 2.3 O teste `test_comando_de_instalacao_igual_no_kit_e_na_conferencia` confere que o `kit.py` e o `confere_metodo.py` citam o mesmo comando (design, decisão 2) (`-k test_comando_de_instalacao_igual_no_kit_e_na_conferencia`)

## 3. A conferência do plugin no projeto

- [x] 3.1 O `INSTALAR` do `confere_metodo.py` passa a `claude plugin install sdd@trilha-ai --scope project`, ainda separado do `marketplace add`; o `test_plugin_ausente_avisa` passa a exigir o `--scope project` e comprova o cenário "Claude Code sem o plugin" (`-k test_plugin_ausente_avisa`), e o `test_aviso_do_plugin_com_comandos_separados` continua passando
- [x] 3.2 A lista de plugins roda com a pasta do projeto como `cwd` (design, decisão 3); o teste `test_lista_de_plugins_roda_na_pasta_do_projeto`, com um `claude` falso que só responde na pasta do projeto e a conferência chamada de outra pasta, comprova o cenário "Conferência chamada de outra pasta" (`-k test_lista_de_plugins_roda_na_pasta_do_projeto`)
- [x] 3.3 A conferência julga, por id, só a instalação que vale (design, decisão 4); o teste `test_plugin_de_outro_projeto_avisa_o_install` comprova o cenário "Plugin instalado só para outro projeto" (`-k test_plugin_de_outro_projeto_avisa_o_install`)
- [x] 3.4 O teste `test_instalacao_do_projeto_vale_sobre_a_do_usuario` comprova o cenário "Instalação do projeto e do usuário em versões diferentes" (`-k test_instalacao_do_projeto_vale_sobre_a_do_usuario`); substituído na 7.1, depois que a execução manual desmentiu o cenário
- [x] 3.5 O `test_plugin_com_versao_igual_nao_avisa` continua passando e comprova o cenário "Só a instalação do usuário" (`-k test_plugin_com_versao_igual_nao_avisa`)
- [x] 3.6 O teste `test_instalacao_do_projeto_atras_avisa` comprova o cenário "Instalação do projeto atrás da versão" (`-k test_instalacao_do_projeto_atras_avisa`)

## 4. Os padrões técnicos fora da skill

- [x] 4.1 Nasce o `modelo/sdd/padroes-tecnicos.md` com a seção "Defaults institucionais" da skill `tdd`, a primeira linha dizendo para que serve e o Python em `requires-python = ">=3.12.3"` na seção `[project]` (design, decisão 5); o teste `test_modelo_dos_padroes_com_requires_python` comprova o cenário "Modelo dos padrões no kit" (`-k test_modelo_dos_padroes_com_requires_python`)
- [x] 4.2 A seção 4 e o princípio 4 da skill `tdd` passam a ler o `sdd/padroes-tecnicos.md` (design, decisão 6); o teste `test_skill_tdd_le_os_padroes_do_projeto` comprova o cenário "Skill sem padrões próprios" (`-k test_skill_tdd_le_os_padroes_do_projeto`)
- [x] 4.3 O `sdd/padroes-tecnicos.md` entra no `A_PREENCHER` do `kit.py` e o `novo` aceita a pasta `sdd/` já criada; os testes que criam `sdd/` numa cópia do kit passam a aceitá-la existente, e o do aviso "sem a pasta sdd/" a apaga antes (design, decisão 8); o teste `test_novo_traz_os_padroes_tecnicos` comprova o cenário "Projeto novo com os padrões" (`-k test_novo_traz_os_padroes_tecnicos`), com o `test_verifica_aprova_o_projeto_novo` passando
- [x] 4.4 O teste `test_atualizar_preserva_os_padroes_do_projeto` comprova o cenário "Padrões ajustados pelo projeto" (`-k test_atualizar_preserva_os_padroes_do_projeto`)
- [x] 4.5 O teste `test_atualizar_cria_os_padroes_que_faltam` comprova o cenário "Projeto sem os padrões" (`-k test_atualizar_cria_os_padroes_que_faltam`)
- [x] 4.6 A linha de `sdd/` do `modelo/esqueleto-CLAUDE.md` cita o `padroes-tecnicos.md` (design, decisão 7); o `test_verificador_aprova_um_repositorio_feito_do_kit` continua passando

## 5. A instalação nos READMEs e a versão

- [x] 5.1 O `README.md` do kit e o `plugins/sdd/README.md` ensinam a instalação por projeto (`claude plugin marketplace add paulosrl/trilha-ai`, depois `claude plugin install sdd@trilha-ai --scope project` em cada projeto) e como tirar a do usuário quando todos os projetos da máquina declararem o plugin; conferido lendo os dois
- [x] 5.2 O comum vai a "Versão 2.2, de <data do commit>." e o plugin a `2.2.0`; o `test_versao_do_plugin_igual_a_do_kit` passa, e o `openspec validate --all --no-interactive` também
- [x] 5.3 O conjunto de testes e o ruff (check e format), cada um sozinho, sem erro

## 7. A correção da execução manual

Cada teste é ajustado antes do código e falha antes dele.

- [x] 7.1 A conferência julga todas as instalações que podem valer no projeto, descartando só as de outra pasta (design, decisão 4); o aviso de versão diz o escopo e dá `claude plugin update sdd@trilha-ai --scope <escopo>`; o teste `test_instalacao_do_usuario_atras_da_do_projeto_avisa` (no lugar do `test_instalacao_do_projeto_vale_sobre_a_do_usuario`) comprova o cenário "Instalação do usuário atrás da do projeto" (`-k test_instalacao_do_usuario_atras_da_do_projeto_avisa`)
- [x] 7.2 O `test_instalacao_do_projeto_atras_avisa` passa a exigir o `--scope project` no comando e comprova o cenário "Instalação do projeto atrás da versão" (`-k test_instalacao_do_projeto_atras_avisa`); o `test_plugin_com_versao_igual_nao_avisa` e o `test_plugin_de_outro_projeto_avisa_o_install` continuam passando
- [x] 7.3 O `README.md` do kit e o `plugins/sdd/README.md` dizem que, enquanto a instalação do usuário existir, ela pode ser a versão que a sessão carrega; conferido lendo os dois
- [x] 7.4 O conjunto de testes, o ruff (check e format), cada um sozinho, e o `openspec validate --all --no-interactive`, sem erro

## 6. Execução manual

- [x] 6.1 Com o usuário olhando: um projeto novo pelo `kit.py novo`, numa pasta descartável, com o settings.json declarando o plugin e o `sdd/padroes-tecnicos.md`; nele, `claude plugin install sdd@trilha-ai --scope project` ao lado da instalação do usuário, o `bash scripts/check.sh` sem aviso do plugin, e uma sessão do Claude Code aberta nele para ver qual versão da skill carrega (design, risco 1); depois, a instalação de projeto desfeita e a lista de instalações da máquina igual à de antes

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit, e a regra de versão do `CLAUDE.md` (a tag `v2.2` no merge commit da main, enviada com ele).
- Depois do merge, com a confirmação do usuário: atualizar o marketplace e o plugin da máquina (`claude plugin marketplace update trilha-ai`, `claude plugin update sdd@trilha-ai`).
- Cada projeto real recebe a 2.2 com o `kit.py atualizar`, só com a ordem do usuário nomeando-o (item 10 do plano); a instalação do usuário sai só depois.
