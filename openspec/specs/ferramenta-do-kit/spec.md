# ferramenta-do-kit Specification

## Purpose

Define o que a ferramenta do kit (`ferramentas/kit.py`) faz num repositório: criar um projeto novo no método e atualizar um existente para a versão do kit, inclusive migrar o layout antigo para a pasta `trilha/`, sem fazer commit nem envio.

## Requirements

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
Num projeto com as cópias do método na raiz, em `scripts/` e em `.githooks/pre-commit`, o `kit.py atualizar` SHALL levá-las para `trilha/` e apagar as antigas, trocar a importação do `CLAUDE.md` para `@trilha/CLAUDE-comum.md` (também quando as cópias já tiverem saído), o `core.hooksPath` para `trilha/hooks` e o hook do Claude Code para `trilha/guarda.py`, sem duplicá-lo e sem tocar em outros hooks do projeto.

#### Scenario: Projeto da versão 1.30 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 1.30
- **THEN** não existem mais `CLAUDE-comum.md` na raiz, os `scripts/confere_*.py`, o `scripts/gerar_pagina_sdd.py`, o `scripts/pagina_sdd_modelo.html`, o `scripts/guarda.py` nem o `.githooks/pre-commit`
- **AND** o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`, o `core.hooksPath` é `trilha/hooks` e o `.claude/settings.json` liga só `trilha/guarda.py`, uma vez
- **AND** a conferência das regras e a do método passam

#### Scenario: Outro hook do projeto preservado
- **WHEN** o projeto tem, além do `.githooks/pre-commit`, um hook próprio em `.githooks/` (por exemplo, `pre-push`)
- **THEN** depois da migração esse hook continua em `.githooks/`, sem mudança
- **AND** a ferramenta avisa que ele não roda mais, porque a trava do commit passou a `trilha/hooks`, citando o arquivo

#### Scenario: Migração parcial
- **WHEN** as cópias soltas já saíram, mas o `CLAUDE.md` ainda importa `@CLAUDE-comum.md` (com ou sem espaço no fim da linha)
- **THEN** depois do `kit.py atualizar` o `CLAUDE.md` importa `@trilha/CLAUDE-comum.md`

### Requirement: Recusa da pasta trilha de outra coisa
O `kit.py atualizar` SHALL recusar, sem apagar nem copiar nada, o projeto que já tem uma pasta `trilha/` sem `trilha/CLAUDE-comum.md`, porque ela não é a do método.

#### Scenario: Pasta trilha do projeto
- **WHEN** o projeto tem `trilha/` com arquivos próprios e sem `trilha/CLAUDE-comum.md`
- **THEN** o `kit.py atualizar` recusa, com o motivo
- **AND** os arquivos da pasta continuam lá

### Requirement: Lista do método pelos arquivos versionados
O que o kit copia sem mudar SHALL ser a lista dos arquivos versionados no git em `modelo/trilha/`, e não o que estiver na pasta: arquivo não versionado ali não vai ao projeto.

#### Scenario: Arquivo solto na pasta do kit
- **WHEN** a pasta `modelo/trilha/` do kit tem um arquivo que o git não versiona
- **THEN** ele não está na lista do que se copia

### Requirement: Parte fixa do check.sh migrada
Na migração, quando o `scripts/check.sh` do projeto tiver a parte fixa do kit, o `kit.py atualizar` SHALL trocá-la pela chamada `bash trilha/verifica.sh`, preservando os argumentos e a continuação de linha da chamada antiga e o resto do arquivo; quando não tiver, SHALL deixar o arquivo como está e avisar o que trocar.

#### Scenario: Parte fixa do kit com vizinhos
- **WHEN** o `scripts/check.sh` tem o bloco `FONTE=…` até o `fi` e `python3 -I scripts/confere_metodo.py --vizinho trilha-ai \` seguido de outra linha
- **THEN** depois da migração o bloco não existe mais e a chamada é `bash trilha/verifica.sh --vizinho trilha-ai \`, com a linha seguinte e a parte da stack intactas

#### Scenario: Parte fixa alterada pelo projeto
- **WHEN** o `scripts/check.sh` não tem a parte fixa do kit e ainda chama `scripts/confere_*`, que a migração tirou
- **THEN** o arquivo fica como está
- **AND** a ferramenta diz que a chamada a `bash trilha/verifica.sh` deve ser posta à mão
- **AND** a atualização termina com o código de saída 1, sem sugerir o commit

### Requirement: Aviso da parte fixa que mudou no kit
O `kit.py atualizar` SHALL avisar cada linha que o kit acrescentou à parte fixa dos arquivos preenchidos desde a versão do projeto e que o projeto não tem, aceitando como presente só a linha igual ou a mesma linha seguida de espaço e argumentos.

#### Scenario: Chamada com os vizinhos
- **WHEN** o `scripts/check.sh` migrado tem `bash trilha/verifica.sh --vizinho trilha-ai \`
- **THEN** a ferramenta não avisa que falta `bash trilha/verifica.sh`

#### Scenario: Linha curta que falta
- **WHEN** o kit acrescentou à parte fixa a linha `fi` e o projeto só tem uma linha que começa com `fi` sem ser ela (por exemplo, `find .`)
- **THEN** a ferramenta avisa que falta `fi`
