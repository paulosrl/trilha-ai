# Proposal

## Why

Num projeto do método, o que o kit copia sem mudar fica espalhado pela raiz, por `scripts/` e por `.githooks/`, misturado ao que é do projeto: a fronteira entre método e projeto só existe na lista do `kit.py`. Por isso a conferência de cópia idêntica cobre só o `CLAUDE-comum.md`, e a trava ou um verificador editado no projeto passa calado (achado F05 da auditoria, severidade alta); a dispensa de change repete à mão a lista do que se copia, que já divergiu do que o `kit.py` escreve (F23, conflito C13); e a parte fixa da verificação é repetida em cada `check.sh` e no CI, sem o `openspec validate` local (F34). A auditoria decidiu uma pasta do método por projeto, intocável e conferida inteira (D2), e a parte fixa da verificação num script do método (D5).

## What Changes

- **BREAKING** Num projeto, o comum, os verificadores, a trava do Claude Code, o gerador da página com o modelo dela e a trava do commit passam a morar em `trilha/` (a trava do commit em `trilha/hooks/`); o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`. No kit, a fonte passa a ser `modelo/trilha/`. O kit vai à versão 2.0 (o comum "Versão 2.0", o plugin 2.0.0).
- A parte fixa da verificação vira `trilha/verifica.sh`: as regras, com a pasta `trilha/` comparada à do kit; o método, repassando os `--vizinho`; e o `openspec validate --all --no-interactive`. O `scripts/check.sh` do projeto fica com a stack e uma linha que chama o `verifica.sh`; o CI deixa o passo próprio do `openspec validate`.
- A conferência de cópia idêntica cobre a pasta `trilha/` inteira: arquivo editado, a mais ou faltando reprova.
- O comum dispensa change para "a pasta `trilha/` e o que o `kit.py atualizar` escreve", sem repetir a lista; os caminhos citados no comum e no esqueleto passam a ser os de `trilha/`.
- O `kit.py atualizar` migra o projeto antigo para `trilha/`, inclusive a importação, a trava do commit, o hook do Claude Code e a parte fixa do `check.sh` quando ela é a do kit.
- Sai o atalho `CLAUDE-comum.md` da raiz do kit.

**Fora desta change:** declarar o plugin no `.claude/settings.json` do projeto (item 7 do plano); o teto em bytes do comum (item 6); os textos do item 8; o README e o mapa além do mínimo que os caminhos novos exigem (item 9); a migração dos projetos reais, cada um com a ordem do usuário nomeando-o.

## Capabilities

### New Capabilities
- `ferramenta-do-kit`: o que o `kit.py` faz num projeto — criar um novo e atualizar um existente, inclusive a migração do layout antigo para a pasta `trilha/`.

### Modified Capabilities
- `conferencias`: ganha a cópia idêntica da pasta `trilha/` inteira, a importação do comum pela pasta `trilha/` e a verificação fixa do projeto no `trilha/verifica.sh`; os requisitos atuais do aviso do plugin não mudam.

## Impact

- Kit: `modelo/scripts/` e `modelo/.githooks/` passam a `modelo/trilha/` (com `hooks/`), mais o novo `modelo/trilha/verifica.sh`; mudam `modelo/scripts/check.sh`, `modelo/.github/workflows/verificacao.yml`, `modelo/claude-settings.json`, `modelo/esqueleto-CLAUDE.md`, `modelo/trilha/CLAUDE-comum.md` (caminhos e versão), `ferramentas/kit.py`, `testes/test_kit.py`, o CI do kit (o ruff), o `CLAUDE.md` e o `README.md` do kit; sai o atalho da raiz.
- Plugin: só a versão (2.0.0).
- Projetos: todos mudam de caminhos na próxima atualização, pela migração do `kit.py atualizar`; os cinco projetos reais estão na 1.30, com a parte fixa do `check.sh` igual à do kit.
