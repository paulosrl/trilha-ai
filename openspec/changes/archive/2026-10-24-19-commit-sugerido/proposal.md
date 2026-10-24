# Proposal

## Why

Pedido do usuário, de 2026-10-24 ("resolve tudo"), sobre os dois pontos que sobraram da change 18:

- a execução manual dela mostrou que, com o `--openspec` e a mesma versão do comum, o `kit.py atualizar` sugere o commit "os arquivos gerados pelo OpenSpec X" mesmo quando a cópia do kit também trocou arquivos (a `trilha/`), e a mensagem esconde parte do que vai no commit;
- o code review dela deixou de fora, por não ter efeito, a regra "o `check.sh` migrado ainda chama os `scripts/confere_*`", repetida na previsão da migração e na migração.

A descrição curta foi aprovada pelo usuário.

## What Changes

- O commit sugerido do `kit.py atualizar` diz o que mudou: "cópia do kit Trilha AI, comum A → B" quando a versão do comum muda ou a cópia trocou algum arquivo; "os arquivos gerados pelo OpenSpec X" quando, com `--openspec`, o dry-run previu mudanças dentro do projeto; as duas partes juntas quando as duas acontecem. Sem o `--openspec`, a mensagem continua a de hoje.
- A regra do `check.sh` migrado fica num lugar só, usada pela previsão e pela migração, sem mudar o comportamento.

**Fora desta change:**
- o resto do `atualizar`;
- o nome da pasta `trilha/`, que é a change seguinte;
- a versão do método: a ferramenta é só do kit, não vai aos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `ferramenta-do-kit`: o commit sugerido do `atualizar`, que hoje nenhum requisito descreve.

## Impact

- `ferramentas/kit.py`: o fim do `atualizar`, o retorno do `_preparar_o_openspec` e a regra do `check.sh`.
- `testes/test_kit.py`: os testes do commit sugerido.
