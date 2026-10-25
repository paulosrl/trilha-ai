# Proposal

## Why

O `/code-review` da change 22, de 2026-10-25, achou sete defeitos no `conferir_andamento` do `confere_metodo.py`, e o usuário pediu o ajuste de todos ("ajuste td que foi relatado"). As duas buscas por regex, com regras que se cruzam, deixam passar formas que a conferência por substring reprovava (`trilha-ai.git` solto, `trilha-ai.git.` no fim da frase, `trilha-ai.wiki`, `heimdall/scripts/check.sh` com `--vizinho heimdall`) e reprovam o `./trilha-ai` sem barra, que é a pasta do método. Cada isenção nova precisava entrar nos dois padrões, e os defeitos vêm daí.

A descrição curta foi aprovada pelo usuário em 2026-10-25.

## What Changes

- A conferência do método divide o texto do `ANDAMENTO.md` em palavras, e cada palavra em partes, separadas por `/`, `:`, `#` e `?`. Reprova a parte que é o nome do vizinho, sozinho ou com `.git`, `.wiki` ou um final que não é só de letras (`trilha-ai.v2`). O `.`, o `:`, o `?` e o `!` do fim da palavra não contam. O arquivo com extensão só de letras (`heimdall.yaml`) não reprova.
- A isenção da pasta do método vale só para o nome da própria pasta (`trilha-ai`), no começo de um caminho relativo (`trilha-ai/...` ou `./trilha-ai`, com a barra ou sem). O nome de outro vizinho no começo de um caminho relativo (`heimdall/scripts/check.sh`) passa a reprovar.
- O `../` continua reprovando onde estiver.
- Um teste para cada forma que a revisão achou.
- O método vai à 2.22: a versão do comum, o plugin `sdd` 2.22.0 e a tag `v2.22`.

**Fora desta change:**
- maiúsculas e minúsculas: `Heimdall` continua passando com `--vizinho heimdall`, como na recusa R5 da change 22;
- trocar o nome que os projetos dão ao vizinho no `scripts/check.sh` (`--vizinho trilha-ai`);
- as outras conferências do método.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `conferencias`: o vizinho citado no `ANDAMENTO.md`, conferido por palavra.

## Impact

- `modelo/trilha-ai/confere_metodo.py` e `testes/test_kit.py`.
- A versão do `modelo/trilha-ai/CLAUDE-comum.md` e o `plugins/sdd/.claude-plugin/plugin.json`.
