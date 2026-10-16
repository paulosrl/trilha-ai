# Tasks

Os testes rodam com `python3 -m unittest discover -s testes -k <nome do teste>`; o conjunto, com `python3 -m unittest discover -s testes`; o ruff, com `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check`. Cada teste novo é escrito antes do código e falha antes dele.

## 1. A versão 2.4 aberta

- [x] 1.1 A linha "Versão 2.4, de 2026-10-15." no `modelo/trilha/CLAUDE-comum.md` e a versão `2.4.0` no `plugins/sdd/.claude-plugin/plugin.json`; o `test_versao_do_plugin_igual_a_do_kit` e o `test_kit_sem_mudanca_depois_da_tag` passam (`-k test_versao_do_plugin_igual_a_do_kit`, `-k test_kit_sem_mudanca_depois_da_tag`)

## 2. A cópia comparada com a versão do projeto

- [x] 2.1 Em `testes/test_kit.py`, um kit falso para os testes: um repositório git temporário com a `modelo/trilha/` atual, commit e a tag da versão dele, cuja cópia de trabalho sobe de versão (a linha "Versão" do comum)
- [x] 2.2 O teste `test_kit_mais_novo_compara_pela_tag_e_avisa` comprova o cenário "Kit numa versão mais nova": um projeto novo, conferido com `--fonte` no kit falso à frente, termina com 0 e avisa as duas versões e o `kit.py atualizar`; falha antes do código (`-k test_kit_mais_novo_compara_pela_tag_e_avisa`)
- [x] 2.3 O teste `test_kit_mais_novo_reprova_a_copia_divergente_da_tag` comprova o cenário "Cópia divergente com o kit mais novo": o `trilha/guarda.py` editado reprova, citando-o (`-k test_kit_mais_novo_reprova_a_copia_divergente_da_tag`)
- [x] 2.4 O teste `test_versao_sem_tag_no_kit_avisa_sem_comparar` comprova o cenário "Kit sem as tags": o kit falso à frente, sem tag nenhuma, termina com 0 e avisa que a pasta não foi comparada; falha antes do código (`-k test_versao_sem_tag_no_kit_avisa_sem_comparar`)
- [x] 2.5 O `test_copia_reprova_a_trava_editada` passa a conferir também que a mensagem manda rodar o `kit.py atualizar` (cenário "Trava editada no projeto"); falha antes do código (`-k test_copia_reprova_a_trava_editada`)
- [x] 2.6 O `confere_regras.py` lê a versão dos dois lados, compara com a cópia de trabalho quando são iguais e com a tag pelo git do kit quando não são (design, decisões 1 a 4), com as mensagens novas; os testes de 2.2 a 2.5 passam, e os que comprovam os cenários "Pasta igual à do kit", "Arquivo faltando ou a mais" e "Permissão de execução perdida" continuam passando (`-k test_copia_da_pasta_trilha_igual_passa`, `-k test_copia_reprova_arquivo_faltando_ou_a_mais`, `-k test_copia_reprova_a_permissao_perdida`)

## 3. As travas desligadas pela configuração

- [x] 3.1 O teste `test_disable_all_hooks_local_avisa` comprova o cenário "Hooks desligados pela configuração local"; falha antes do código (`-k test_disable_all_hooks_local_avisa`)
- [x] 3.2 O teste `test_disable_all_hooks_do_projeto_avisa` comprova o cenário "Hooks desligados pelo projeto"; falha antes do código (`-k test_disable_all_hooks_do_projeto_avisa`)
- [x] 3.3 O teste `test_disable_all_hooks_religado_pelo_local_nao_avisa` comprova o cenário "Configuração local religa os hooks" (`-k test_disable_all_hooks_religado_pelo_local_nao_avisa`)
- [x] 3.4 O teste `test_projeto_novo_sem_aviso_de_trava` comprova o cenário "Travas ligadas no projeto novo" (`-k test_projeto_novo_sem_aviso_de_trava`)
- [x] 3.5 O `avisos_das_travas` lê o `disableAllHooks` do `.claude/settings.local.json` e depois do `.claude/settings.json`, o primeiro com a chave decidindo (design, decisão 5); os testes de 3.1 a 3.4 passam

## 4. Os textos que descrevem a conferência

- [x] 4.1 O docstring do `confere_regras.py`, o comentário do `trilha/verifica.sh` e o README (passo 5 e "Ao mudar o padrão") dizem que a pasta é comparada com a versão do projeto e que o kit mais novo só avisa; `grep -rn "cópia idêntica\|acusa a cópia divergente" README.md modelo/` não mostra texto antigo
- [x] 4.2 O conjunto de testes, o ruff (check e format), cada um sozinho, e o `openspec validate --all --no-interactive`, sem erro

## 5. Execução manual

- [x] 5.1 Numa pasta descartável do scratchpad: uma cópia do kit com a versão da cópia de trabalho à frente, um projeto feito na versão de agora e o `bash scripts/check.sh` dele com `TRILHA_AI` nessa cópia, que termina com `ok` e o aviso da versão; depois, o mesmo com um `trilha/guarda.py` editado, que reprova; a saída mostrada ao usuário e a pasta apagada

## 6. As respostas à revisão de código

- [x] 6.1 O teste `test_versao_que_o_kit_nao_tem_reprova` comprova o cenário "Versão que o kit não tem", com a versão trocada abaixo (1.99) e acima (9.98) da do kit; falhou antes da correção (`-k test_versao_que_o_kit_nao_tem_reprova`)
- [x] 6.2 O teste `test_kit_atras_do_projeto_avisa_sem_mandar_atualizar` comprova o cenário "Kit atrás do projeto"; falhou antes da correção (`-k test_kit_atras_do_projeto_avisa_sem_mandar_atualizar`)
- [x] 6.3 O teste `test_comum_sem_versao_compara_com_a_copia_do_kit` comprova o cenário "Comum sem a linha de versão"; falhou antes da correção (`-k test_comum_sem_versao_compara_com_a_copia_do_kit`)
- [x] 6.4 O `confere_regras.py` compara os números das versões, reprova a versão que um kit com as tags não tem, lê a tag por `refs/tags/`, sobrevive à falta do git e ao objeto que falta, e usa a mensagem neutra quando a tag existe e não se lê; o `test_kit_mais_novo_reprova_a_copia_divergente_da_tag` passa a provar a comparação pela tag, e o kit falso dos testes não depende da configuração global do git; o conjunto, o ruff e o `openspec validate` sem erro

## Workflow follow-up

- Depois do archive: `openspec validate --all --no-interactive`, os testes e o ruff do kit; a tag `v2.4` no commit do merge, enviada com o "sim" do usuário (`git push origin main v2.4`).
