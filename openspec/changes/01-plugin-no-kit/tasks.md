# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`.

## 1. O plugin dentro do kit

- [x] 1.1 Trazer o repositório `../pipeline-prd-tdd-openspec` (branch `main`) por `git merge --allow-unrelated-histories`, mantendo o `README.md` do kit no conflito; conferir com `git log --oneline -- plugins/sdd/skills/prd/SKILL.md`, que mostra os commits antigos, e com o `LICENSE` sem conflito
- [x] 1.2 Renomear o marketplace para `trilha-ai` e apontar o `homepage` do `plugin.json` para `https://github.com/paulosrl/trilha-ai`; o teste `test_marketplace_lido_da_raiz_do_kit` comprova o cenário "Marketplace lido da raiz do kit"
- [x] 1.3 O teste `test_as_tres_skills_no_plugin` comprova o cenário "As três skills no plugin" (pastas `prd`, `tdd`, `briefing`, cada uma com o `name` igual ao da pasta)
- [x] 1.4 O teste `test_plugin_sem_o_repositorio_antigo` comprova o cenário "Nenhuma referência ao repositório antigo no plugin" (nenhum arquivo de `.claude-plugin/` e de `plugins/` cita `pipeline-prd-tdd-openspec`)

## 2. Uma versão para o kit e o plugin

- [x] 2.1 Subir a linha do `modelo/CLAUDE-comum.md` para "Versão 1.35, de <data do dia>", o `plugin.json` para `1.35.0` e a regra do `CLAUDE.md` do kit para "toda mudança em `modelo/` ou em `plugins/` sobe a versão"; o teste `test_versao_do_plugin_igual_a_do_kit` comprova o cenário "Versões iguais"
- [x] 2.2 O teste `test_versao_do_plugin_esquecida_reprova` comprova o cenário "Versão do plugin esquecida": a mesma conferência do teste 2.1, aplicada a um comum na versão nova e a um manifesto na anterior, reprova e nomeia as duas versões

## 3. A conferência do plugin instalado

- [x] 3.1 Reescrever a leitura do plugin no `modelo/scripts/confere_metodo.py`: `claude plugin list --json` com prazo de 10 s, todas as instalações `sdd@…`, a versão do projeto lida do `CLAUDE-comum.md` da raiz, qualquer falha em silêncio; sem `../pipeline-prd-tdd-openspec` nem `installed_plugins.json`; o texto do arquivo diz o que ele confere. Nos testes, o `confere_metodo` roda sempre com um `claude` falso no PATH (nunca o da máquina)
- [x] 3.2 O teste `test_plugin_conferido_sem_a_pasta_vizinha` comprova o cenário "Pasta vizinha com outra versão"
- [x] 3.3 O teste `test_plugin_do_marketplace_antigo_avisa` comprova o cenário "Plugin do marketplace antigo" (o aviso com `claude plugin install sdd@trilha-ai` e a saída 0)
- [x] 3.4 O teste `test_plugin_com_versao_diferente_avisa` comprova o cenário "Versões diferentes" (o aviso cita `1.34.0` e `1.35`; saída 0)
- [x] 3.5 O teste `test_plugin_com_versao_igual_nao_avisa` comprova o cenário "Versões iguais" da conferência
- [x] 3.6 O teste `test_plugin_ausente_avisa` comprova o cenário "Claude Code sem o plugin"
- [x] 3.7 O teste `test_sem_o_claude_code_nao_avisa` comprova o cenário "Máquina sem o Claude Code"
- [x] 3.8 O teste `test_lista_de_plugins_com_erro_nao_avisa` comprova o cenário "Lista de plugins com erro" (saída diferente de 0 e texto que não é JSON)
- [x] 3.9 Rodar o ruff 0.17 do CI do kit (`uvx ruff@0.17.0 check --isolated --line-length 100 modelo/scripts/ ferramentas/` e o mesmo com `format --check`), sem erro

## 4. A documentação

- [x] 4.1 Escrever `plugins/sdd/README.md` a partir do `README.md` e do `docs/instalacao.md` do plugin: o que cada skill faz, a instalação só como plugin (`sdd@trilha-ai`), o pacote `@fission-ai/openspec`, o encadeamento das três skills, e o ciclo e o versionamento remetidos ao comum; tirar `docs/`, `prompts/` e `exemplo/`; conferir com `git grep -n "npm install -g openspec"`, que não acha nada
- [x] 4.2 Citar no `README.md` do kit o comando novo de instalação e o `plugins/sdd/README.md`; conferir com `git grep -n "sdd@pipeline"` restrito ao README do kit, que não acha nada

## 5. Execução manual

- [x] 5.1 Com a confirmação do usuário e ele olhando: trocar o plugin da máquina (`claude plugin uninstall sdd@pipeline-prd-tdd-openspec`, `claude plugin marketplace remove pipeline-prd-tdd-openspec`, `claude plugin marketplace add /home/pl/projetos/trilha-ai`, `claude plugin install sdd@trilha-ai`); conferir em `claude plugin list --json` o `sdd@trilha-ai` na `1.35.0`; num projeto descartável no scratchpad (`kit.py novo`), o `confere_metodo` sem aviso do plugin e, com o comum do descartável na "Versão 1.36", com o aviso

## 6. As correções da revisão independente

Cada teste é escrito antes da correção e falha antes dela.

- [ ] 6.1 O aviso de fora do kit vale para qualquer `sdd@` que não seja `sdd@trilha-ai`; o teste `test_plugin_de_outro_marketplace_avisa` comprova o cenário "Plugin de outro marketplace", e o `test_plugin_do_marketplace_antigo_avisa` continua comprovando o do marketplace antigo
- [ ] 6.2 Os comandos do aviso separados; o teste `test_aviso_do_plugin_com_comandos_separados` comprova o cenário "Comandos separados" (nos avisos de fora do kit e de ausente, nenhum `&&`)
- [ ] 6.3 O aviso do plugin desligado; o teste `test_plugin_desligado_avisa` comprova o cenário "Plugin do kit desligado"
- [ ] 6.4 A opção `--sem-plugin` no `confere_metodo.py`, usada pelo `modelo/.githooks/pre-commit`; o teste `test_trava_do_commit_nao_consulta_o_claude` comprova o cenário "Commit sem consultar o Claude Code" (um `claude` falso que deixa uma marca, e o commit sem a marca), e o `test_check_sh_avisa_o_plugin` comprova o cenário "Verificação do repositório com o aviso"
- [ ] 6.5 A guarda da versão: o teste `test_mudanca_sem_versao_nova_reprova` comprova os cenários "Mudança sem versão nova" e "Versão nova em preparo" (num repositório de teste com tag), e o `test_kit_sem_mudanca_depois_da_tag` aplica a guarda ao próprio kit
- [ ] 6.6 Os testes de versão usam a leitura do `kit.py` (`_versao`), sem regex própria; o `test_versao_do_plugin_igual_a_do_kit` e o `test_versao_do_plugin_esquecida_reprova` continuam passando
- [ ] 6.7 O `tearDownModule` devolve o PATH original; conferido pelo conjunto inteiro de testes
- [ ] 6.8 O conjunto de testes e o ruff do kit, cada um sozinho, sem erro; na máquina do usuário, o `check.sh` de um projeto descartável avisa o plugin de outra versão e um commit nele não consulta o Claude Code

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit, e a regra de versão do `CLAUDE.md` (a tag `v1.35` no merge commit da main, enviada com ele).
- Depois do merge, com a confirmação do usuário: trocar o marketplace local pelo do GitHub (`claude plugin marketplace remove trilha-ai`, `claude plugin marketplace add paulosrl/trilha-ai`), reinstalar e conferir a `1.35.0`.
- Passo à parte, só com a ordem do usuário nomeando o repositório: arquivar o `pipeline-prd-tdd-openspec`, com o README apontando para o kit.
