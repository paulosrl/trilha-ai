## MODIFIED Requirements

### Requirement: Travas desligadas pela configuração
A conferência das regras SHALL avisar, sem falhar, cada trava desligada: a do commit, quando o `core.hooksPath` do clone não é `trilha-ai/hooks`, salvo `trilha/hooks` com o link de transição `trilha` no projeto, que conta como ligada, com o aviso para trocar; a do Claude Code, quando o `.claude/settings.json` não liga o `trilha-ai/guarda.py` ou quando o `disableAllHooks` que vale no projeto é verdadeiro, lido do `.claude/settings.local.json`, que prevalece, e do `.claude/settings.json`.

#### Scenario: Hooks desligados pela configuração local
- **WHEN** o `.claude/settings.local.json` do projeto tem `"disableAllHooks": true`
- **THEN** a conferência das regras avisa que a trava do Claude Code está desligada, citando o `disableAllHooks` e o `.claude/settings.local.json`
- **AND** termina com o código de saída 0

#### Scenario: Hooks desligados pelo projeto
- **WHEN** o `.claude/settings.json` do projeto tem `"disableAllHooks": true` e não há `.claude/settings.local.json`
- **THEN** a conferência das regras avisa, citando o `disableAllHooks` e o `.claude/settings.json`

#### Scenario: Configuração local religa os hooks
- **WHEN** o `.claude/settings.json` tem `"disableAllHooks": true` e o `.claude/settings.local.json` o tem falso
- **THEN** a conferência das regras não avisa o `disableAllHooks`

#### Scenario: Travas ligadas no projeto novo
- **WHEN** a conferência das regras roda num projeto recém-criado pelo kit
- **THEN** ela não avisa trava desligada

#### Scenario: Trava do commit pelo link de transição
- **WHEN** o projeto tem o link de transição `trilha` para `trilha-ai` e o `core.hooksPath` do clone é `trilha/hooks`
- **THEN** a conferência das regras não avisa a trava do commit desligada
- **AND** avisa que ela está ligada pelo link de transição e dá o comando `git config core.hooksPath trilha-ai/hooks`

#### Scenario: Trava do commit na pasta antiga sem o link
- **WHEN** o projeto não tem `trilha` e o `core.hooksPath` do clone é `trilha/hooks`
- **THEN** a conferência das regras avisa a trava do commit desligada

## ADDED Requirements

### Requirement: Aviso do link de transição no projeto
Quando o projeto tem o link simbólico `trilha` que aponta para a `trilha-ai/` dele, a conferência das regras SHALL avisar, sem falhar, que esse é o link de transição da pasta antiga e que ele sai pelo `kit.py atualizar` quando nenhum arquivo do projeto citar mais `trilha/`. Um `trilha` que não é esse link MUST NOT gerar o aviso.

#### Scenario: Projeto com o link de transição
- **WHEN** a conferência das regras roda num projeto com o link `trilha` para `trilha-ai`
- **THEN** ela avisa o link de transição e o que o tira
- **AND** termina com o código de saída 0

#### Scenario: Pasta trilha própria do projeto
- **WHEN** o projeto tem uma pasta `trilha/` própria, que não é link
- **THEN** a conferência das regras não avisa o link de transição
