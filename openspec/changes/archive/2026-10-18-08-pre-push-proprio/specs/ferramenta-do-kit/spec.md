# Spec Delta

## MODIFIED Requirements

### Requirement: Migração do layout antigo
Num projeto com as cópias do método na raiz, em `scripts/` e em `.githooks/pre-commit`, o `kit.py atualizar` SHALL levá-las para `trilha/` e apagar as antigas, trocar a importação do `CLAUDE.md` para `@trilha/CLAUDE-comum.md` (também quando as cópias já tiverem saído), o `core.hooksPath` para `trilha/hooks` e o hook do Claude Code para `trilha/guarda.py`, sem duplicá-lo e sem tocar em outros hooks do projeto.

#### Scenario: Projeto da versão 1.30 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 1.30
- **THEN** não existem mais `CLAUDE-comum.md` na raiz, os `scripts/confere_*.py`, o `scripts/gerar_pagina_sdd.py`, o `scripts/pagina_sdd_modelo.html`, o `scripts/guarda.py` nem o `.githooks/pre-commit`
- **AND** o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`, o `core.hooksPath` é `trilha/hooks` e o `.claude/settings.json` liga só `trilha/guarda.py`, uma vez
- **AND** a conferência das regras e a do método passam

#### Scenario: Hook de envio do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, um `.githooks/pre-push` próprio
- **THEN** depois da migração o `.githooks/pre-push` continua em `.githooks/`, sem mudança
- **AND** a ferramenta não avisa que ele deixou de rodar, porque o `trilha/hooks/pre-push` o roda
- **AND** um `git push` do projeto migrado roda o `.githooks/pre-push`

#### Scenario: Hook de envio do projeto que não pode rodar
- **WHEN** o `.githooks/pre-push` do projeto está sem a permissão de execução ou é um link simbólico quebrado
- **THEN** a migração o mantém como está
- **AND** a ferramenta avisa que o envio será recusado até ele ser corrigido, citando o arquivo

#### Scenario: Outro hook do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, outro hook próprio em `.githooks/` (por exemplo, `commit-msg`)
- **THEN** depois da migração esse hook continua em `.githooks/`, sem mudança
- **AND** a ferramenta avisa que ele não roda mais, porque a trava do commit passou a `trilha/hooks`, citando o arquivo

#### Scenario: Migração parcial
- **WHEN** as cópias soltas já saíram, mas o `CLAUDE.md` ainda importa `@CLAUDE-comum.md` (com ou sem espaço no fim da linha)
- **THEN** depois do `kit.py atualizar` o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`
