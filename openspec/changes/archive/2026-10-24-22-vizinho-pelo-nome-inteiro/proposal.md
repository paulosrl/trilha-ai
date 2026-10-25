# Proposal

## Why

Pedido do usuário, de 2026-10-24 ("faça"), depois de um achado na change 36 do Heimdall: a conferência do método reprova o `ANDAMENTO.md` que contém o nome de um vizinho como texto solto, e os projetos declaram `--vizinho trilha-ai`, o nome do repositório do kit, que desde a 2.19 também é o nome da pasta do método. O `ANDAMENTO.md` do Heimdall reprovou só por citar a change `hooks-pela-trilha-ai`, e a change foi renomeada para passar. Citar a pasta `trilha-ai/`, que todo projeto tem, também reprova; e o vizinho `outro` reprova a palavra `outros`.

A descrição curta foi aprovada pelo usuário.

## What Changes

- A conferência do método conta o vizinho no `ANDAMENTO.md` pelo nome inteiro e solto, ou pelo caminho que chega a ele de fora (a URL, com o `.git` ou sem, o caminho absoluto, o `~/`): não quando ele é parte de outro nome (`hooks-pela-trilha-ai`, `outros`), nem num arquivo com extensão (`heimdall.yaml`), nem no caminho que começa no próprio projeto, como a pasta `trilha-ai/` do método (com o `./` ou sem). O `../` continua contando onde estiver.
- O método vai à 2.21: a versão do comum, o plugin `sdd` 2.21.0 e a tag `v2.21`.

**Fora desta change:**
- trocar o nome que os projetos dão ao vizinho no `scripts/check.sh` (`--vizinho trilha-ai`);
- voltar o nome da change 36 do Heimdall, que segue `hooks-na-pasta-nova`;
- as outras conferências do método.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `conferencias`: o vizinho citado no `ANDAMENTO.md` pelo nome inteiro.

## Impact

- `modelo/trilha-ai/confere_metodo.py` e `testes/test_kit.py`.
- A versão do `modelo/trilha-ai/CLAUDE-comum.md` e o `plugins/sdd/.claude-plugin/plugin.json`.
