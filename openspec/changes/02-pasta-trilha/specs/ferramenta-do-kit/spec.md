# Spec Delta

## Purpose

Define o que a ferramenta do kit (`ferramentas/kit.py`) faz num repositório: criar um projeto novo no método e atualizar um existente para a versão do kit, inclusive migrar o layout antigo para a pasta `trilha/`, sem fazer commit nem envio.

## ADDED Requirements

### Requirement: Projeto novo com a pasta do método
O `kit.py novo` SHALL criar o projeto com a pasta `trilha/` igual à `modelo/trilha/` do kit, o `CLAUDE.md` importando `@trilha/CLAUDE-comum.md`, a trava do commit ligada em `trilha/hooks` e o hook do Claude Code apontando para `trilha/guarda.py`.

#### Scenario: Projeto novo verificado
- **WHEN** o `kit.py novo` cria um projeto numa pasta vazia
- **THEN** a pasta `trilha/` do projeto é igual à `modelo/trilha/` do kit
- **AND** `git config core.hooksPath` responde `trilha/hooks`
- **AND** o `.claude/settings.json` liga `trilha/guarda.py`
- **AND** o `scripts/check.sh` do projeto termina com o código de saída 0

#### Scenario: Trava do commit no projeto novo
- **WHEN** o projeto novo recebe um commit com o `CLAUDE.md` sem a importação do comum
- **THEN** a trava do commit o barra

### Requirement: Atualização da pasta do método por inteiro
O `kit.py atualizar` SHALL deixar a pasta `trilha/` do projeto igual à `modelo/trilha/` do kit, inclusive apagando dela o arquivo que o kit não tem mais, sem tocar no que o projeto preencheu fora dela.

#### Scenario: Arquivo que o kit tirou
- **WHEN** a pasta `trilha/` do projeto tem um arquivo que o kit não tem mais
- **THEN** depois do `kit.py atualizar` esse arquivo não existe
- **AND** a pasta é igual à do kit

### Requirement: Migração do layout antigo
Num projeto com as cópias do método na raiz, em `scripts/` e em `.githooks/pre-commit`, o `kit.py atualizar` SHALL levá-las para `trilha/` e apagar as antigas, trocar a importação do `CLAUDE.md` para `@trilha/CLAUDE-comum.md`, o `core.hooksPath` para `trilha/hooks` e o hook do Claude Code para `trilha/guarda.py`, sem duplicá-lo e sem tocar em outros hooks do projeto.

#### Scenario: Projeto da versão 1.30 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 1.30
- **THEN** não existem mais `CLAUDE-comum.md` na raiz, os `scripts/confere_*.py`, o `scripts/gerar_pagina_sdd.py`, o `scripts/pagina_sdd_modelo.html`, o `scripts/guarda.py` nem o `.githooks/pre-commit`
- **AND** o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`, o `core.hooksPath` é `trilha/hooks` e o `.claude/settings.json` liga só `trilha/guarda.py`, uma vez
- **AND** a conferência das regras e a do método passam

#### Scenario: Outro hook do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, um hook próprio em `.githooks/` (por exemplo, `pre-push`)
- **THEN** depois da migração esse hook continua em `.githooks/`, sem mudança
- **AND** a ferramenta avisa que ele não roda mais, porque a trava do commit passou a `trilha/hooks`, citando o arquivo

### Requirement: Parte fixa do check.sh migrada
Na migração, quando o `scripts/check.sh` do projeto tiver a parte fixa do kit, o `kit.py atualizar` SHALL trocá-la pela chamada `bash trilha/verifica.sh`, preservando os argumentos e a continuação de linha da chamada antiga e o resto do arquivo; quando não tiver, SHALL deixar o arquivo como está e avisar o que trocar.

#### Scenario: Parte fixa do kit com vizinhos
- **WHEN** o `scripts/check.sh` tem o bloco `FONTE=…` até o `fi` e `python3 -I scripts/confere_metodo.py --vizinho trilha-ai \` seguido de outra linha
- **THEN** depois da migração o bloco não existe mais e a chamada é `bash trilha/verifica.sh --vizinho trilha-ai \`, com a linha seguinte e a parte da stack intactas

#### Scenario: Parte fixa alterada pelo projeto
- **WHEN** o `scripts/check.sh` não tem a parte fixa do kit
- **THEN** o arquivo fica como está
- **AND** a ferramenta avisa que a chamada a `bash trilha/verifica.sh` deve ser posta à mão
