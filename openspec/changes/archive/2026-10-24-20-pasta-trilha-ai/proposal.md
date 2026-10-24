# Proposal

## Why

Pedido do usuário, de 2026-10-24: a pasta que o kit põe em cada repositório deve se chamar `trilha-ai`, o nome do kit, e não `trilha`. Hoje ela é `trilha/`, e o nome está nos verificadores, nas travas, no comum, nos modelos, na ferramenta e em cada projeto (a importação do `CLAUDE.md`, a chamada do `check.sh`, o `core.hooksPath` e a trava do `.claude/settings.json`).

A descrição curta foi aprovada pelo usuário.

## What Changes

- **BREAKING** A pasta do método passa de `trilha/` a `trilha-ai/`: no kit, `modelo/trilha/` vira `modelo/trilha-ai/`, e todo caminho que a cita acompanha (os verificadores, as travas, o `verifica.sh`, o comum, o esqueleto do `CLAUDE.md`, o `scripts/check.sh` e o `claude-settings.json` do modelo, o `kit.py`, o README e os specs).
- O `kit.py atualizar` migra o projeto que tem a pasta `trilha/` do método (com o `trilha/CLAUDE-comum.md`): tira a pasta, cria a `trilha-ai/`, troca as citações à pasta no `CLAUDE.md` (a importação e o texto) e no `check.sh` (a chamada do `verifica.sh`, com os argumentos), a trava do `settings.json` e o `core.hooksPath`; avisa o arquivo a mais que a pasta antiga tinha, os outros arquivos do projeto que ainda citam `trilha/` e que a sessão do Claude Code aberta no projeto precisa ser reaberta. Uma pasta `trilha/` sem o comum é do projeto e fica. O usuário aprovou essas trocas e esses avisos além da descrição curta (2026-10-24).
- O kit mantém `modelo/trilha` como link simbólico para `modelo/trilha-ai`, escolha do usuário (2026-10-24): a verificação de um projeto ainda de antes da 2.19 acha a pasta do kit pelo nome antigo e não quebra até a atualização dele.
- A recusa da pasta que não é do método passa a valer para a `trilha-ai/`.
- O kit continua lendo as versões antigas: as tags de antes da 2.19 têm `modelo/trilha/`, que a ferramenta e a conferência das regras leem.
- O método vai à 2.19: a versão do comum, o plugin `sdd` 2.19.0 e a tag `v2.19`.

**Fora desta change:**
- atualizar os projetos que seguem o kit, cada um sob ordem do usuário;
- os registros históricos do kit (as auditorias, o plano de migração e as changes arquivadas), que citam a pasta como ela era;
- o nome do repositório do kit e do marketplace do plugin, que já são `trilha-ai`.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `ferramenta-do-kit`: a pasta `trilha-ai/` no projeto novo e na atualização, a migração da `trilha/` do método, a recusa da `trilha-ai/` de outra coisa e as leituras das versões antigas.
- `conferencias`: a importação, a cópia idêntica (com as tags de antes da 2.19), a verificação fixa, o teto e as travas pela `trilha-ai/`.
- `hooks-do-git`: o envio pelo `trilha-ai/hooks/pre-push`.
- `horas-de-trabalho`: o `trilha-ai/tempo.py`.
- `trava-do-metodo`: o `core.hooksPath` em `trilha-ai/hooks`.

## Impact

- `modelo/`: a pasta renomeada, o link de transição e os arquivos que a citam; a versão do comum.
- `plugins/sdd/`: o `plugin.json` na 2.19.0 e o README.
- `ferramentas/kit.py` e `testes/test_kit.py`.
- O kit: `README.md`, `CLAUDE.md`, `ferramentas/validar-projeto.md`, os Purpose de quatro specs principais, `openspec/config.yaml` (o contexto) e o CI (`.github/workflows/testes.yml`), que rodam o ruff em `modelo/trilha-ai/`.
