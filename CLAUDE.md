# CLAUDE.md — Trilha AI

Este repositório é a **fonte do padrão** Trilha AI. O que vai aos projetos fica em `modelo/`: a pasta `trilha-ai/`, que os projetos recebem inteira e sem mudar (o `CLAUDE-comum.md`, os verificadores, as travas, o gerador da página; o `modelo/trilha` é só um link para ela, que a verificação dos projetos de antes da 2.19 procura), e os modelos que eles preenchem, na tabela do passo 3 do `README.md`. O plugin `sdd` fica em `plugins/`. O resto é só do kit: a ferramenta, os testes, o OpenSpec do kit, o mapa e as auditorias (`docs/auditorias/`). O kit não segue o próprio método: não importe o `CLAUDE-comum.md` aqui nem crie `sdd/` aqui.

## Regras

- A ferramenta (`ferramentas/kit.py`), os verificadores e as travas mudam por change do OpenSpec, com o `openspec/config.yaml` da raiz (o do kit, não o de `modelo/`), no ciclo abaixo. O texto do método (o comum, os modelos e as skills do plugin) e o do kit (este arquivo, os READMEs, o mapa, as auditorias) mudam fora de change, como os testes e o CI do kit quando não acompanham uma change.
- Toda mudança em `modelo/` ou em `plugins/` sobe a versão e a data na linha "Versão X.Y, de AAAA-MM-DD." do `modelo/trilha-ai/CLAUDE-comum.md`, e o `plugins/sdd/.claude-plugin/plugin.json` vai à `X.Y.0` (um teste confere); a mudança é registrada na mensagem do commit, que ganha a tag anotada `vX.Y` (enviada com ele: `git push origin main vX.Y`); os repositórios que seguem o padrão recebem a cópia depois, cada um sob ordem do usuário nomeando-o.
- Os arquivos de regras falam de "o usuário", nunca de "a pessoa"; o comum não menciona curso nenhum nem projeto nenhum: só o método.
- O `modelo/trilha-ai/CLAUDE-comum.md` e o `modelo/esqueleto-CLAUDE.md` somados cabem em 200 linhas, e o comum sozinho em 16 KB, metade do teto de 32 KB que a conferência cobra de cada projeto.
- Antes do commit, cada um sozinho, conferindo o código de saída: `python3 -m unittest discover -s testes` (Python 3 puro, sem dependências) e o ruff 0.17 em `modelo/trilha-ai/` e `ferramentas/` (`uvx ruff@0.17.0 check --isolated --line-length 100` e o mesmo com `format --check`). O GitHub roda os mesmos a cada envio (`.github/workflows/testes.yml`).
- Responda em PT-BR, em linguagem simples, uma coisa por vez; publique só com "sim" explícito.

## Precedência

Em conflito, vale nesta ordem: os testes e o CI do kit; a escolha do usuário; o OpenSpec (fluxo e formato), que nunca se ajusta: quem cede é o kit; este arquivo; o `openspec/config.yaml` da raiz; as skills `sdd:*`. O `~/.claude/CLAUDE.md` global e a memória automática cedem a este arquivo.

## O ciclo de uma change do kit

1. a descrição curta (a origem, o comportamento esperado e o que fica fora), aprovada pelo usuário, sem PRD nem TDD; a branch `change/NN-nome`, aberta da main atualizada;
2. `/opsx:propose` com a descrição; commit, envio e pull request em rascunho (`gh pr create --draft`);
3. a revisão dos artefatos antes do apply; o que reprovar se corrige com `/opsx:update`, depois da escolha do usuário;
4. `/opsx:apply`, com o teste escrito antes do código e a execução manual como última tarefa; commit a cada parada;
5. `/opsx:verify` e o `/code-review <número do PR>`, numa sessão nova ou num agente sem o contexto da sessão; cada sugestão dos dois, aplicada ou recusada com o motivo, vai à seção "Respostas à revisão" do `design.md` da change, ou ao `notas.md` da pasta da change quando o propose não criar o `design.md`;
6. `/opsx:archive` e os passos do `operations.archive` do `openspec/config.yaml`; o pull request sai do rascunho (`gh pr ready`);
7. o merge, com a verificação do GitHub verde e o "sim" do usuário: `gh pr merge --merge --delete-branch`, e a tag `vX.Y` quando a regra da versão pedir.

Cada envio ao GitHub, em qualquer passo, só com o "sim" do usuário.
