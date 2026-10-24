# Proposal

## Why

Pedido do usuário, de 2026-10-24, ao atualizar o OpenSpec da 1.14.1 para a 1.15.0: rever o método diante da versão nova, com o OpenSpec no comando. A 1.15.0 trouxe o `openspec update --dry-run --json`, que lista o que o update adicionaria, trocaria ou apagaria sem escrever nada. A conferência do método faz hoje o mesmo à mão: ensaia o update numa pasta temporária, com a cópia dos arquivos gerados, do `config.yaml` e da configuração global da máquina, e compara os arquivos. Com o comando do OpenSpec, o ensaio próprio fica redundante.

A descrição curta foi aprovada pelo usuário.

## What Changes

- O aviso dos arquivos gerados que o `openspec update` mudaria passa a vir do `openspec update --dry-run --json`, rodado na raiz do projeto e sem a rede, no lugar do ensaio numa pasta temporária. O texto do aviso fica igual ("apagaria", "criaria", "trocaria" e o `openspec config list`).
- Só entram no aviso os arquivos do projeto: o que o dry-run lista fora dele (a configuração global, que a migração do OpenSpec regravaria) fica de fora.
- O dry-run que falha (código diferente de 0, saída que não é o JSON esperado ou com `failures`) segue em silêncio, como o ensaio de hoje. O `openspec` anterior à 1.15, que não conhece o `--dry-run`, cai nesse caso; o aviso da versão diferente da do CI continua apontando a troca.
- A versão fixada do OpenSpec passa a 1.15.0 no CI do modelo, no CI do kit e no README.
- A versão passa a 2.16 e o plugin `sdd` a 2.16.0, com a data do dia.

**Fora desta change:**
- os fluxos novos que o OpenSpec oferece no perfil (`new`, `continue`, `ff`, `bulk-archive`, `onboard`): o ciclo não os usa;
- a instalação do OpenSpec sem o Node: o método segue com o npm, que o CI usa;
- a cópia da 2.16 nos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `conferencia-do-openspec`: o aviso dos arquivos gerados vem do dry-run do OpenSpec, e o silêncio cobre o dry-run que falha ou que o `openspec` não conhece.

## Impact

- `modelo/trilha/confere_metodo.py` (o `_aviso_do_update` e as constantes dele).
- `testes/test_kit.py`: o `openspec` falso responde ao dry-run; os testes do ensaio passam a ele, e a versão fixada vai à 1.15.0.
- `modelo/.github/workflows/verificacao.yml`, `.github/workflows/testes.yml` e `README.md` (a versão fixada).
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão) e `plugins/sdd/.claude-plugin/plugin.json`.
