## ADDED Requirements

### Requirement: Vizinho citado pelo nome inteiro no ANDAMENTO
A conferência do método SHALL reprovar o `ANDAMENTO.md` que cita um vizinho (`--vizinho`) pelo nome inteiro e solto, ou por um caminho que chega a ele de fora (depois de `/`, `~` ou `:`). MUST NOT reprovar o nome que é parte de outro nome, o arquivo com extensão nem o caminho que começa no próprio projeto, como a pasta `trilha-ai/` do método. O `../` MUST continuar reprovando onde estiver.

#### Scenario: Vizinho pelo nome
- **WHEN** o `ANDAMENTO.md` diz "o kit trilha-ai está na 2.21", ou termina a frase com "o kit trilha-ai.", e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Caminho que chega ao vizinho de fora
- **WHEN** o `ANDAMENTO.md` cita `https://github.com/paulosrl/trilha-ai/pull/22`, `/home/pl/projetos/trilha-ai/x` ou `git@github.com:paulosrl/trilha-ai.git` e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Pasta do método
- **WHEN** o `ANDAMENTO.md` cita `trilha-ai/verifica.sh` ou `./trilha-ai/verifica.sh` e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Nome dentro de outro nome
- **WHEN** o `ANDAMENTO.md` cita a change `hooks-pela-trilha-ai`, a palavra `outros` e o arquivo `heimdall.yaml`, e a conferência roda com `--vizinho trilha-ai --vizinho outro --vizinho heimdall`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Caminho para fora do projeto
- **WHEN** o `ANDAMENTO.md` cita `../qualquer/coisa`
- **THEN** ela reprova, citando `../`

#### Scenario: Vizinho vazio
- **WHEN** a conferência roda com `--vizinho ""`
- **THEN** ela não reprova pelo vizinho
