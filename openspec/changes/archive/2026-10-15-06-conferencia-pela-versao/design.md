# Design

## Context

O `--fonte` está no `modelo/trilha/confere_regras.py`: a função `conferir` lê a `modelo/trilha/` da pasta do kit e a compara, arquivo a arquivo (conteúdo e permissão de execução), com a pasta `trilha/` do projeto. O `trilha/verifica.sh` passa o `--fonte` quando o kit está ao lado (ou em `TRILHA_AI`). Os avisos das travas saem da `avisos_das_travas`, que hoje olha o `core.hooksPath` e se o `.claude/settings.json` cita o `trilha/guarda.py`. O script roda com `python3 -I`, só com a biblioteca padrão, e o kit é um clone git com as tags `vX.Y`.

## Goals / Non-Goals

**Goals:**
- A versão de referência da comparação é a do projeto, nunca a da cópia de trabalho do kit, quando as duas diferem.
- Nenhuma falha nova sem o git do kit, sem as tags ou com um clone raso: nesses casos, aviso.

**Non-Goals:**
- Conferir o projeto contra uma versão diferente da dele (isso é o `kit.py atualizar`).
- Avisar o que o usuário escolhe por sessão (`--bare`, `--settings`).

## Decisions

**1. A versão de cada lado pela linha "Versão X.Y" do comum.** O projeto lê a do `trilha/CLAUDE-comum.md`; o kit, a da `modelo/trilha/CLAUDE-comum.md` da cópia de trabalho. Iguais: a comparação é a de hoje, com a cópia de trabalho, o que cobre o caso comum e a versão em preparo no kit (sem tag ainda). Alternativa descartada: comparar sempre com a tag; reprovaria o projeto feito da cópia de trabalho durante o preparo de uma versão, quando a tag ainda não existe.

**2. A pasta da tag lida pelo git, sem extrair arquivos.** `git -C <kit> ls-tree -r -z vX.Y -- modelo/trilha` dá, por arquivo, o modo (`100755` é executável) e o objeto; `git -C <kit> cat-file --batch` dá o conteúdo de todos de uma vez. Os dois lados viram o mesmo formato (nome → conteúdo e se é executável), e uma só função compara, com as mensagens de hoje. Alternativa descartada: `git archive` extraído numa pasta temporária, que pede o `tarfile` com filtro de extração (diferente entre versões do Python) e escreve no disco.

**3. A tag que não se lê.** Sem a linha de versão no projeto, a comparação é com a cópia de trabalho. Com a versão, e o kit com as tags `v*` mas sem a da versão do projeto, a conferência reprova: essa versão nunca existiu (revista depois da revisão de código, ponto 1). Sem tag nenhuma (clone raso), sem o git, ou com a tag que existe e não se lê (clone parcial sem rede), só avisa que a pasta não foi comparada. Kit atrás do projeto (os números da versão comparados) avisa para atualizar o kit, nunca o projeto.

**4. As mensagens.** A falha mantém o começo de hoje ("trilha/<arquivo> difere do kit", "falta", "não é do kit", "perdeu a permissão de execução") e termina com "rode o kit.py atualizar do kit, com a escolha do usuário; não edite a pasta". O aviso da versão diferente cita as duas versões: "o kit está na A.B e o projeto na X.Y: a pasta trilha/ foi comparada com a vX.Y; rode o kit.py atualizar do kit, com a escolha do usuário".

**5. O `disableAllHooks` pela precedência.** Lê o `.claude/settings.local.json` e depois o `.claude/settings.json`; o primeiro que tem a chave decide. JSON inválido não conta, como no `confere_metodo.py`. Verdadeiro: aviso que cita a chave e o arquivo.

## Risks / Trade-offs

- [Kit sem as tags (clone raso, cópia baixada sem o git)] → aviso, sem comparar; a cópia continua conferida no `kit.py atualizar`.
- [Dois processos git a mais por verificação, só quando as versões diferem] → custo de milissegundos; a trava do commit não usa o `--fonte`.
- [Tag apontando para o commit errado] → fora do alcance da conferência; a regra de versão do `CLAUDE.md` do kit põe a tag no commit da versão.

## Migration Plan

Nenhuma: os projetos recebem a conferência nova com a cópia da 2.4, pelo `kit.py atualizar`, sob ordem do usuário.

## Verificação

Cada cenário com o teste que o comprova, rodado com `python3 -m unittest discover -s testes -k <teste>`, todos com `OK` em 2026-10-15; o conjunto (173 testes) passou três rodadas seguidas, o ruff (check e format) e o `openspec validate --all --no-interactive` sem erro.

| Cenário | Teste |
|---|---|
| Pasta igual à do kit | `test_copia_da_pasta_trilha_igual_passa` |
| Trava editada no projeto | `test_copia_reprova_a_trava_editada` (agora com o `kit.py atualizar` na mensagem) |
| Arquivo faltando ou a mais | `test_copia_reprova_arquivo_faltando_ou_a_mais` |
| Permissão de execução perdida | `test_copia_reprova_a_permissao_perdida` |
| Kit numa versão mais nova | `test_kit_mais_novo_compara_pela_tag_e_avisa` |
| Cópia divergente com o kit mais novo | `test_kit_mais_novo_reprova_a_copia_divergente_da_tag` |
| Kit sem as tags | `test_versao_sem_tag_no_kit_avisa_sem_comparar` |
| Versão que o kit não tem | `test_versao_que_o_kit_nao_tem_reprova` |
| Kit atrás do projeto | `test_kit_atras_do_projeto_avisa_sem_mandar_atualizar` |
| Comum sem a linha de versão | `test_comum_sem_versao_compara_com_a_copia_do_kit` |
| Hooks desligados pela configuração local | `test_disable_all_hooks_local_avisa` |
| Hooks desligados pelo projeto | `test_disable_all_hooks_do_projeto_avisa` |
| Configuração local religa os hooks | `test_disable_all_hooks_religado_pelo_local_nao_avisa` |
| Travas ligadas no projeto novo | `test_projeto_novo_sem_aviso_de_trava` |

Antes do código, falharam os testes dos cenários "Kit numa versão mais nova", "Versão do projeto sem tag no kit", "Trava editada no projeto" e os dois do `disableAllHooks` que avisam. Os outros já passavam e ficam como guarda do que não pode mudar. Uma rodada do conjunto falhou no `test_scripts_cabem_no_lint_de_quem_copia`, por duas linhas com mais de 100 caracteres, que o `ruff format` quebrou.

Execução manual (tarefa 5.1), num clone descartável do kit com a tag `v2.4` e a cópia de trabalho na 2.5, e um projeto feito na 2.4: o `bash scripts/check.sh` com `TRILHA_AI` no clone terminou com 0, com o aviso "o kit está na 2.5 e o projeto na 2.4: a pasta trilha/ foi comparada com a v2.4"; com o `trilha/guarda.py` editado, terminou com 1 e "FALHA: trilha/guarda.py difere do kit; rode o kit.py atualizar do kit, com a escolha do usuário; não edite a pasta". A pasta foi apagada.

## Respostas à revisão

O `/opsx:verify` não achou crítico nem aviso e fez uma sugestão. A revisão de código, num agente sem o contexto da sessão, achou 7 pontos. O usuário delegou as escolhas ("sempre a melhor escolha", na rodada 1 da auditoria); a decisão de cada um:

1. **Aplicado.** A linha "Versão" trocada à mão para uma versão sem tag desligava a comparação (provado: `guarda.py` editado e versão 2.9 ou 1.99 passavam). Agora reprova num kit com as tags; teste `test_versao_que_o_kit_nao_tem_reprova`.
2. **Recusado.** O fim de linha CRLF (`core.autocrlf=true`) e a permissão de execução no Windows nativo: o método é só para Linux ou WSL (`CLAUDE-comum.md`, segundo parágrafo), onde o git não converte o fim de linha e a permissão existe.
3. **Aplicado.** Com o kit atrás do projeto, o aviso mandava rodar o `kit.py atualizar`, que rebaixaria o projeto. Agora manda atualizar o kit; teste `test_kit_atras_do_projeto_avisa_sem_mandar_atualizar`.
4. **Aplicado.** Sem a linha de versão no projeto, nada era comparado. Agora compara com a cópia de trabalho; teste `test_comum_sem_versao_compara_com_a_copia_do_kit`.
5. **Aplicado.** A tag que existe e não se lê (clone parcial, `safe.directory`) recebe a mensagem neutra "não foi possível ler a vX.Y do kit pelo git".
6. **Aplicado.** O git ausente não quebra mais a conferência (o `OSError` vira aviso), a tag é lida por `refs/tags/vX.Y` (não pega uma branch de mesmo nome), e o objeto que falta no `cat-file` vira aviso, sem erro.
7. **Aplicado.** O kit falso dos testes não usa os ganchos nem a assinatura da configuração global do git.

Sugestão do verify, **aplicada**: o `test_kit_mais_novo_reprova_a_copia_divergente_da_tag` confere que o comum não aparece como divergente, o que só vale na comparação pela tag.
