## MODIFIED Requirements

### Requirement: Vizinho citado pelo nome inteiro no ANDAMENTO
A conferência do método SHALL reprovar o `ANDAMENTO.md` que cita um vizinho (`--vizinho`): em cada palavra, partida em `/`, `:`, `#` e `?`, a parte que é o nome, sozinho ou com `.git`, `.wiki` ou um final que não é só de letras, sem contar o `.`, `:`, `?` ou `!` do fim da palavra. MUST NOT reprovar o nome dentro de outro nome, o arquivo com extensão só de letras nem a pasta do método no começo de um caminho relativo. O `../` MUST continuar reprovando onde estiver.

#### Scenario: Vizinho pelo nome
- **WHEN** o `ANDAMENTO.md` diz "o kit trilha-ai está na 2.21", termina a frase com "o kit trilha-ai.", diz "clonar trilha-ai.git ao lado" ou "versão trilha-ai.v2", e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Caminho que chega ao vizinho de fora
- **WHEN** o `ANDAMENTO.md` cita `https://github.com/paulosrl/trilha-ai/pull/22`, `/home/pl/projetos/trilha-ai/x`, `git@github.com:paulosrl/trilha-ai.git`, `https://github.com/paulosrl/trilha-ai.wiki` ou termina a frase com `https://github.com/paulosrl/trilha-ai.git.`, e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Pasta do método
- **WHEN** o `ANDAMENTO.md` cita `trilha-ai/verifica.sh`, `./trilha-ai/verifica.sh` ou `./trilha-ai`, sem a barra, e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Caminho relativo que começa em outro vizinho
- **WHEN** o `ANDAMENTO.md` diz "ajustar heimdall/scripts/check.sh" e a conferência roda com `--vizinho heimdall`
- **THEN** ela reprova, citando `heimdall`

#### Scenario: Nome dentro de outro nome
- **WHEN** o `ANDAMENTO.md` cita a change `hooks-pela-trilha-ai`, a palavra `outros` e o arquivo `heimdall.yaml`, e a conferência roda com `--vizinho trilha-ai --vizinho outro --vizinho heimdall`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Caminho para fora do projeto
- **WHEN** o `ANDAMENTO.md` cita `../qualquer/coisa`
- **THEN** ela reprova, citando `../`

#### Scenario: Vizinho vazio
- **WHEN** a conferência roda com `--vizinho ""`
- **THEN** ela não reprova pelo vizinho
