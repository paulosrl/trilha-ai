## ADDED Requirements

### Requirement: Padrões técnicos lidos do projeto
A skill `tdd` SHALL tomar os padrões técnicos de partida do arquivo `sdd/padroes-tecnicos.md` do projeto, quando ele existir, e MUST NOT trazer padrões técnicos próprios: sem o arquivo, a recomendação sai só da entrevista.

#### Scenario: Skill sem padrões próprios
- **WHEN** o `plugins/sdd/skills/tdd/SKILL.md` do kit é lido
- **THEN** ele cita o `sdd/padroes-tecnicos.md`
- **AND** não traz os padrões que estão no modelo (por exemplo, `pgvector`, `uv`, `pnpm`)

#### Scenario: Modelo dos padrões no kit
- **WHEN** o `modelo/sdd/padroes-tecnicos.md` do kit é lido
- **THEN** ele traz os padrões que saíram da skill
- **AND** o Python é declarado com `requires-python`, a sintaxe do `uv`, e não com a do Poetry (`python = "`)
