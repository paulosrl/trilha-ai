# Proposal

## Why

Pedido do usuário, de 2026-10-21 ("prossiga com a change"), depois da revisão de código do commit `c8f032a` da change 12 (versão 2.10). Ela achou que:
- quando uma pasta acima da raiz antiga de um resumo de mesmo nome não se abre (sem permissão), o comando termina com rastro de exceção no Python 3.12 (conferido), sem gravar o resumo nem a página; no Python 3.14, a mesma conferência diria "não existe", e a cópia viva seria juntada e renomeada;
- o aviso do resumo antigo que não se lê não diz como resolver, e repete a cada execução.

A descrição curta foi aprovada pelo usuário.

## What Changes

- O erro do sistema ao conferir o `.git` da raiz antiga (sem permissão, por exemplo) conta como "ainda é um repositório": o resumo dela não é juntado nem renomeado, e o comando termina normalmente.
- O aviso do resumo antigo que não se lê passa a dizer "corrija-o ou mova-o", como o do resumo principal ilegível.
- A versão passa a 2.11 e o plugin `sdd` a 2.11.0, com a data do dia.

**Fora desta change:** os outros achados da mesma revisão, casos raros ou só de forma:
- o `.git` velho que sobrou na raiz antiga;
- o `EMAIL` com o `user.useConfigOnly`;
- o e-mail da configuração do sistema;
- duas execuções ao mesmo tempo;
- a numeração do `.juntado` entre o resumo e a página;
- a frase do design arquivado da change 12;

e a cópia da 2.11 nos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `horas-de-trabalho`: a raiz antiga que não se confere por falta de permissão e o aviso do resumo antigo que não se lê.

## Impact

- `modelo/trilha/tempo.py` (o `_ainda_repositorio` e o texto de um aviso).
- `testes/test_kit.py`: um teste novo e um ajustado.
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão) e `plugins/sdd/.claude-plugin/plugin.json`.
