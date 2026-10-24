# Proposal

## Why

Pedido do usuário, de 2026-10-24, depois do ensaio da migração do Heimdall (2.15 → 2.19) num clone descartável: o código próprio do projeto que cita a pasta antiga `trilha/` quebra depois da migração. O `scripts/lib/common.sh` do Heimdall grava `core.hooksPath=trilha/hooks`, e as travas deixam de rodar sem erro nenhum; o `teste-common`, o `teste-pre-push`, o `local-012` e a evidência do TDD citam `trilha/`, e o `pre-push` do projeto passa a recusar o envio. A change 20 aceitou esse risco com um aviso depois da cópia, que não protege: o projeto fica quebrado até a troca à mão, que, no Heimdall, é uma change dele. No mesmo clone, com o link `trilha → trilha-ai`, passaram o `check.sh`, o `pre-push` com os 49 testes pareados e a trava do commit.

A descrição curta foi aprovada pelo usuário ("sim, prossiga até finalizar com perfeição").

## What Changes

- Na migração da `trilha/` do método, quando arquivos versionados do projeto, fora da `trilha-ai/`, ainda citam `trilha/` (a mesma busca do aviso das citações), o `kit.py atualizar` cria no projeto o link simbólico `trilha → trilha-ai`, que o git versiona, e diz que o criou e por quê, com a lista. Sem citação, não cria.
- Num `atualizar` seguinte, o link `trilha` que aponta para a `trilha-ai/` é o de transição: não recusa nem migra. Ele sai quando a busca não acha mais citação, com aviso, e fica, com a lista, quando ainda acha. O link `trilha` que aponta para outro lugar continua recusado como hoje.
- A conferência das regras avisa, sem reprovar, que o link de transição existe e que ele sai quando o projeto deixar de citar `trilha/`; e aceita o `core.hooksPath` em `trilha/hooks` com o link como trava ligada, com o aviso para trocar por `trilha-ai/hooks`, em vez de "trava do commit desligada".
- O roteiro de validação (`ferramentas/validar-projeto.md`) trata o link como transição, e não como migração pela metade.
- O método vai à 2.20: a versão do comum, o plugin `sdd` 2.20.0 e a tag `v2.20`.

**Fora desta change:**
- trocar os arquivos do projeto que citam `trilha/`: o kit só os lista, e a troca é do projeto;
- tirar o link `modelo/trilha` do kit;
- a regra no `CLAUDE.md` do kit (toda troca de caminho que vai aos projetos mantém o antigo funcionando) e o ensaio com o `pre-push` do projeto no plano de migração, que são texto do kit, fora de change;
- atualizar o Heimdall e os outros projetos, cada um sob ordem do usuário.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `ferramenta-do-kit`: a migração cria o link de transição quando o projeto ainda cita `trilha/`, e o `atualizar` seguinte o mantém ou o tira; a recusa do link vale só para o que não aponta para a `trilha-ai/`.
- `conferencias`: o aviso do link de transição e a trava do commit ligada pelo link.

## Impact

- `ferramentas/kit.py` e `testes/test_kit.py`.
- `modelo/trilha-ai/confere_regras.py` e a versão do `modelo/trilha-ai/CLAUDE-comum.md`; `plugins/sdd/.claude-plugin/plugin.json`.
- `ferramentas/validar-projeto.md`.
- Nos projetos: o link `trilha` versionado, só nos que ainda citam a pasta antiga, até eles deixarem de citá-la.
