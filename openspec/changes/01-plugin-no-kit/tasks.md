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

- [ ] 5.1 Com a confirmação do usuário e ele olhando: trocar o plugin da máquina (`claude plugin uninstall sdd@pipeline-prd-tdd-openspec`, `claude plugin marketplace remove pipeline-prd-tdd-openspec`, `claude plugin marketplace add /home/pl/projetos/trilha-ai`, `claude plugin install sdd@trilha-ai`); conferir em `claude plugin list --json` o `sdd@trilha-ai` na `1.35.0`; num projeto descartável no scratchpad (`kit.py novo`), o `confere_metodo` sem aviso do plugin e, com o comum do descartável na "Versão 1.36", com o aviso

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit, e a regra de versão do `CLAUDE.md` (a tag `v1.35` no merge commit da main, enviada com ele).
- Depois do merge, com a confirmação do usuário: trocar o marketplace local pelo do GitHub (`claude plugin marketplace remove trilha-ai`, `claude plugin marketplace add paulosrl/trilha-ai`), reinstalar e conferir a `1.35.0`.
- Passo à parte, só com a ordem do usuário nomeando o repositório: arquivar o `pipeline-prd-tdd-openspec`, com o README apontando para o kit.
