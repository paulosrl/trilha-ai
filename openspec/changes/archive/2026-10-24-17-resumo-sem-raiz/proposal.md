# Proposal

## Why

Pedido do usuário, de 2026-10-24 ("prossiga e resolva"), sobre o que ficou fora da change 15 (achados V5 e C3 da revisão dela): o resumo de horas com o nome deste repositório que nem deixa ler a raiz gravada (não é JSON, não é um objeto, ou não tem a raiz em texto) é ignorado pelo `trilha/tempo.py` sem aviso. Se ele for de uma pasta antiga deste repositório, as horas das conversas já apagadas que só ele guarda ficam de fora, e ninguém fica sabendo.

A descrição curta foi aprovada pelo usuário.

## What Changes

- Esse resumo passa a gerar um aviso em toda execução, que o cita e diz que, se ele for de uma pasta antiga deste repositório, as horas dele não vieram: corrija-o ou mova-o. O comando continua terminando com 0 e não mexe no arquivo.
- A versão passa a 2.17 e o plugin `sdd` a 2.17.0, com a data do dia.

**Fora desta change:**
- os outros casos do resumo de mesmo nome (a raiz que ainda é repositório, a que não se confere, o resumo de versão desconhecida), que já avisam;
- o resumo do próprio caminho que não se lê, que já recusa a execução;
- a cópia da 2.17 nos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `horas-de-trabalho`: o aviso do resumo de mesmo nome que não deixa ler a raiz.

## Impact

- `modelo/trilha/tempo.py` (o `_outros_resumos` e o `main`).
- `testes/test_kit.py`: um teste novo.
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão) e `plugins/sdd/.claude-plugin/plugin.json`.
