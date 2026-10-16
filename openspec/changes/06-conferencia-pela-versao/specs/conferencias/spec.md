## MODIFIED Requirements

### Requirement: Cópia idêntica da pasta do método
Com a pasta do kit indicada, a conferência das regras SHALL comparar a pasta `trilha/` do projeto com a `modelo/trilha/` da versão do projeto (a linha "Versão X.Y" do `trilha/CLAUDE-comum.md`): a cópia de trabalho do kit, quando ele está na mesma versão; a tag `vX.Y` do kit, quando não está. Ela MUST reprovar, nomeando o arquivo e mandando rodar o `kit.py atualizar`, quando um arquivo estiver diferente, faltar no projeto, existir só no projeto ou tiver perdido a permissão de execução.

#### Scenario: Pasta igual à do kit
- **WHEN** a pasta `trilha/` do projeto tem os mesmos arquivos, com o mesmo conteúdo, que a `modelo/trilha/` do kit
- **THEN** a conferência das regras não reprova pela cópia

#### Scenario: Trava editada no projeto
- **WHEN** o `trilha/guarda.py` do projeto difere do kit
- **THEN** a conferência das regras reprova, citando `trilha/guarda.py`
- **AND** a mensagem manda rodar o `kit.py atualizar`, e não editar a pasta

#### Scenario: Arquivo faltando ou a mais
- **WHEN** falta no projeto um arquivo que a pasta do kit tem, ou o projeto tem em `trilha/` um arquivo que o kit não tem
- **THEN** a conferência das regras reprova, citando o arquivo

#### Scenario: Permissão de execução perdida
- **WHEN** o `trilha/hooks/pre-commit` do projeto tem o mesmo conteúdo do kit, mas sem a permissão de execução
- **THEN** a conferência das regras reprova, citando `trilha/hooks/pre-commit`

#### Scenario: Kit numa versão mais nova
- **WHEN** a cópia de trabalho do kit está numa versão mais nova que a do projeto, o kit tem a tag da versão do projeto, e a pasta `trilha/` do projeto é igual à `modelo/trilha/` dessa tag
- **THEN** a conferência das regras não reprova pela cópia
- **AND** avisa, citando as duas versões e o `kit.py atualizar`

#### Scenario: Cópia divergente com o kit mais novo
- **WHEN** a cópia de trabalho do kit está numa versão mais nova, o kit tem a tag da versão do projeto, e o `trilha/guarda.py` do projeto difere do dessa tag
- **THEN** a conferência das regras reprova, citando `trilha/guarda.py`

#### Scenario: Versão do projeto sem tag no kit
- **WHEN** o kit está noutra versão e não tem a tag da versão do projeto
- **THEN** a conferência das regras avisa que a pasta `trilha/` não foi comparada
- **AND** não reprova pela cópia

## ADDED Requirements

### Requirement: Travas desligadas pela configuração
A conferência das regras SHALL avisar, sem falhar, cada trava desligada: a do commit, quando o `core.hooksPath` do clone não é `trilha/hooks`; a do Claude Code, quando o `.claude/settings.json` não liga o `trilha/guarda.py` ou quando o `disableAllHooks` que vale no projeto é verdadeiro, lido do `.claude/settings.local.json`, que prevalece, e do `.claude/settings.json`.

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
