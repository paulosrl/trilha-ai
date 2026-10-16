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
6. Os documentos: o PRD, o TDD e a decomposição em sdd/; o ANDAMENTO.md; o openspec/config.yaml comparado ao modelo/openspec/config.yaml do kit (o que diverge e se a divergência é própria do projeto ou um desvio).
7. O CI: o .github/workflows roda o scripts/check.sh.
8. Os dados: arquivos no git com dados pessoais ou segredos, fora do que o "Dados a proteger" do CLAUDE.md permite.

Se não houver pasta trilha/, o veredito é "não segue o kit": diga o que falta e o comando do kit que resolve (python3 ferramentas/kit.py novo|atualizar <pasta>).

Grave o relatório em <pasta>/docs/validacao-trilha-ai.md, sobrescrevendo o anterior, com:
- a data e a hora, lidas do `date`; a versão do comum no projeto e no kit;
- o veredito numa linha: "de acordo", "de acordo, com pendências" ou "não está de acordo";
- uma tabela com cada item de 1 a 8: o resultado (ok, aviso ou falha) e a evidência (o comando e a saída resumida);
- as pendências numeradas, cada uma com a correção recomendada.

No fim, responda em PT-BR, curto: o veredito, as pendências e o caminho do relatório. Pergunte se deve commitar o relatório; envio ao GitHub, só com "sim" explícito.
```
