## MODIFIED Requirements

### Requirement: Trava do commit não se desliga
A trava SHALL barrar o comando git que desliga a trava do commit: o `core.hooksPath` com valor diferente de `trilha-ai/hooks` passado num `-c` (separado ou colado) e o `git config` que o grava com outro valor ou o apaga. A leitura do `core.hooksPath` e a gravação de `trilha-ai/hooks` MUST passar.

#### Scenario: Hooks desligados por -c
- **WHEN** o comando é `git -c core.hooksPath=/dev/null commit -m x` ou `git -ccore.hooksPath= commit -m x`
- **THEN** a trava barra

#### Scenario: Hooks trocados por git config
- **WHEN** o comando é `git config core.hooksPath .git/hooks` ou `git config --unset core.hooksPath`
- **THEN** a trava barra

#### Scenario: Leitura e valor do método
- **WHEN** o comando é `git config core.hooksPath` ou `git config core.hooksPath trilha-ai/hooks`
- **THEN** a trava deixa passar

