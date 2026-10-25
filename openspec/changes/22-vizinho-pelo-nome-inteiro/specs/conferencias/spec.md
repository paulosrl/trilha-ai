## ADDED Requirements

### Requirement: Vizinho citado pelo nome inteiro no ANDAMENTO
A conferência do método SHALL reprovar o `ANDAMENTO.md` que cita um vizinho (`--vizinho`) pelo nome inteiro e solto, e MUST NOT reprovar o nome que é parte de outro nome (com letra, número, `_`, `-` ou `.` encostado) nem o nome seguido de barra, que é um caminho do próprio projeto, como a pasta `trilha-ai/` do método. O `../` MUST continuar reprovando onde estiver.

#### Scenario: Vizinho pelo nome
- **WHEN** o `ANDAMENTO.md` diz "o kit trilha-ai está na 2.21" e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela reprova, citando `trilha-ai`

#### Scenario: Pasta do método
- **WHEN** o `ANDAMENTO.md` cita `trilha-ai/verifica.sh` e a conferência roda com `--vizinho trilha-ai`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Nome dentro de outro nome
- **WHEN** o `ANDAMENTO.md` cita a change `hooks-pela-trilha-ai` e a palavra `outros`, e a conferência roda com `--vizinho trilha-ai --vizinho outro`
- **THEN** ela não reprova pelo vizinho

#### Scenario: Caminho para fora do projeto
- **WHEN** o `ANDAMENTO.md` cita `../qualquer/coisa`
- **THEN** ela reprova, citando `../`
