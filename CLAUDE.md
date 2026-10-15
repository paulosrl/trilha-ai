# CLAUDE.md — Trilha AI

Este repositório é a **fonte do padrão** Trilha AI. O que vai aos projetos fica em `modelo/`: a pasta `trilha/`, que os projetos recebem inteira e sem mudar (o `CLAUDE-comum.md`, os verificadores, as travas, o gerador da página), e os modelos que eles preenchem (o esqueleto do `CLAUDE.md`, o `ANDAMENTO.md`, o `openspec/config.yaml`, o `check.sh`); o resto é só do kit, e o `README.md` explica o uso. O kit não segue o próprio método: não importe o `CLAUDE-comum.md` aqui nem crie `sdd/` aqui.

## Regras

- A ferramenta (`ferramentas/kit.py`), os verificadores e as travas mudam por change do OpenSpec, com o `openspec/config.yaml` da raiz (o do kit, não o de `modelo/`). A change nasce de uma descrição curta aprovada pelo usuário, sem PRD nem TDD, e segue a branch, o pull request e o merge do ciclo do comum. O texto do método (o comum e os modelos) muda fora de change.
- Toda mudança em `modelo/` ou em `plugins/` sobe a versão e a data na linha "Versão X.Y, de AAAA-MM-DD." do `modelo/trilha/CLAUDE-comum.md`, e o `plugins/sdd/.claude-plugin/plugin.json` vai à `X.Y.0` (um teste confere); a mudança é registrada na mensagem do commit, que ganha a tag anotada `vX.Y` (enviada com ele: `git push origin main vX.Y`); os repositórios que seguem o padrão recebem a cópia depois, cada um sob ordem do usuário nomeando-o.
- Os arquivos de regras falam de "o usuário", nunca de "a pessoa"; o comum não menciona curso nenhum nem projeto nenhum: só o método.
- O `modelo/trilha/CLAUDE-comum.md` e o `modelo/esqueleto-CLAUDE.md` somados cabem em 200 linhas.
- Antes do commit, cada um sozinho, conferindo o código de saída: `python3 -m unittest discover -s testes` (Python 3 puro, sem dependências) e o ruff 0.17 em `modelo/trilha/` e `ferramentas/` (`uvx ruff@0.17.0 check --isolated --line-length 100` e o mesmo com `format --check`). O GitHub roda os mesmos a cada envio (`.github/workflows/testes.yml`).
- Responda em PT-BR, em linguagem simples, uma coisa por vez; publique só com "sim" explícito.
