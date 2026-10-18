# Proposal

## Why

Pedido do usuário, de 2026-10-18, na etapa 1 do plano de migração dos projetos (`docs/plano-migracao-projetos.md`). O Heimdall tem um `.githooks/pre-push` próprio, exigido pelo spec `dev-scripts` e pelo ADR-011 dele. Esse hook é a única verificação a cada envio do Heimdall, porque o CI pesado está desligado por custo. A migração ao formato 2.x põe o `core.hooksPath` em `trilha/hooks`, onde só há o `pre-commit`, e o hook próprio deixa de rodar. O `kit.py atualizar` só avisa. Migrar o Heimdall na 2.5 desligaria essa proteção sem ninguém perceber.

## What Changes

- Um hook novo, o `trilha/hooks/pre-push`, roda o `.githooks/pre-push` do projeto quando ele existe. Passa a ele os mesmos argumentos e a mesma entrada e devolve o código de saída dele. Sem o hook próprio, sai com 0 e o envio segue.
- A migração do layout antigo mantém o `.githooks/pre-push` e deixa de avisar que ele não roda. Para outro arquivo que sobrar em `.githooks/`, o aviso continua.
- O comum ganha meia frase: o hook de envio próprio do projeto fica em `.githooks/pre-push` e roda pela `trilha/hooks`.
- A versão passa a 2.6 e o plugin `sdd` a 2.6.0.

**Fora desta change:**
- os outros hooks próprios (um `pre-commit` ou um `commit-msg` do projeto), que hoje não têm caso real;
- qualquer mudança no `guarda.py`, que já barra trocar o `core.hooksPath`;
- a migração do Heimdall, que é a etapa 2 do plano.

## Capabilities

### New Capabilities

- `hooks-do-git`: o que os hooks do git da pasta `trilha/hooks` rodam no projeto. Nesta change, o envio pelo hook próprio do projeto.

### Modified Capabilities

- `ferramenta-do-kit`: a migração do layout antigo deixa de avisar sobre o `.githooks/pre-push`, que passa a rodar pela `trilha/hooks`.

## Impact

- Kit:
  - `modelo/trilha/hooks/pre-push`, novo e executável;
  - `ferramentas/kit.py`, no aviso da migração;
  - `modelo/trilha/CLAUDE-comum.md`, com a frase e a versão 2.6;
  - `plugins/sdd/.claude-plugin/plugin.json`;
  - `testes/test_kit.py`;
  - o `README.md`, se a lista da pasta `trilha/` citar os hooks.
- A conferência das regras já cobra, para todo arquivo de `trilha/`, o conteúdo igual ao do kit e a permissão de execução. O hook novo entra nela sem mudança de código.
- Projetos: recebem o hook com a cópia da 2.6, pelo `kit.py atualizar`, sob ordem do usuário. No projeto sem `.githooks/pre-push`, o envio continua igual.
