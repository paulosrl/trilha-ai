# Validar um projeto contra o kit

O prompt para conferir se um repositório segue o kit Trilha AI. Cole-o como está numa sessão do
Claude Code: ele pergunta primeiro o nome da pasta do projeto, que fica sempre em
`/home/pl/projetos/<nome>`. Ele só audita: grava o relatório em
`<pasta>/docs/validacao-trilha-ai.md` e não corrige nada.

```text
Antes de qualquer outra coisa, pergunte o nome da pasta do projeto a validar e espere a resposta. É só o nome (por exemplo, xavier): todo projeto fica em /home/pl/projetos/<nome>, e é esse caminho que <pasta> quer dizer daqui em diante. Se a pasta não existir ou não for um repositório git, diga isso e pergunte de novo.

Valide o repositório <pasta> contra o kit Trilha AI que está em /home/pl/projetos/trilha-ai. É uma auditoria: não corrija nada, não commite e não mexa no ANDAMENTO.md. O único arquivo que você grava é o relatório.

Confira, rodando os comandos e lendo o código de saída de cada um:
1. A cópia do kit: a pasta trilha/ existe e é igual à modelo/trilha/ do kit (diff -r, ignorando __pycache__). Anote a versão do CLAUDE-comum.md do projeto e a do kit.
2. As regras: python3 -I trilha/confere_regras.py . --fonte /home/pl/projetos/trilha-ai
3. O método: python3 -I trilha/confere_metodo.py, com os --vizinho que o scripts/check.sh do projeto usa.
4. A verificação completa: bash scripts/check.sh, sozinho, sem filtro.
5. As travas: git config core.hooksPath (deve ser trilha/hooks); o guarda.py e o plugin sdd@trilha-ai no .claude/settings.json.
6. Os documentos: o PRD, o TDD e a decomposição em sdd/; o ANDAMENTO.md; o openspec/config.yaml comparado ao modelo/openspec/config.yaml do kit. O context é do projeto. De rules: até o fim, o texto é o do kit: só passam linhas próprias a mais no operations e chaves de topo do próprio OpenSpec (o githubCopilot). Qualquer outra diferença nas regras é desvio, mesmo com um ADR que as chame de próprias, salvo exceção declarada em "Exceções ao comum" do CLAUDE.md, com o motivo. Desde a 2.7, o item 2 reprova o rules: diferente.
7. O CI: o .github/workflows roda o scripts/check.sh.
8. Os dados: arquivos no git com dados pessoais ou segredos, fora do que o "Dados a proteger" do CLAUDE.md permite.
9. As ferramentas da máquina: o openspec --version diante do @fission-ai/openspec@X do CI do projeto; o perfil do OpenSpec (openspec config list), com o verify e a entrega em skills e comandos (both); os avisos do OpenSpec que o item 3 dá (o que o openspec update mudaria nos arquivos gerados); o plugin sdd na versão X.Y.0 do comum (claude plugin list); o gh e o Claude Code (gh --version, claude --version) diante da última versão publicada, como aviso. O .gitignore, o CI, o Dependabot e o check.sh comparados ao modelo do kit, fora dos blocos da parte da stack (o kit.py atualizar avisa o que falta).

Se não houver pasta trilha/, o veredito é "não segue o kit": diga o que falta e o comando do kit que resolve (python3 ferramentas/kit.py novo|atualizar <pasta>).

Grave o relatório em <pasta>/docs/validacao-trilha-ai.md, sobrescrevendo o anterior, com:
- a data e a hora, lidas do `date`; a versão do comum no projeto e no kit;
- o veredito numa linha: "de acordo", "de acordo, com pendências" ou "não está de acordo";
- uma tabela com cada item de 1 a 9: o resultado (ok, aviso ou falha) e a evidência (o comando e a saída resumida);
- as pendências numeradas, cada uma com a correção recomendada.

No fim, responda em PT-BR, curto: o veredito, as pendências e o caminho do relatório. Pergunte se deve commitar o relatório; envio ao GitHub, só com "sim" explícito.
```
