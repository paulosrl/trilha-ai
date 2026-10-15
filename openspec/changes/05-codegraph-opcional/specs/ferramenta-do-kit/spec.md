## ADDED Requirements

### Requirement: CodeGraph opcional nos próximos passos
Os próximos passos do `kit.py novo` SHALL citar o `codegraph init` como opcional, condicionado ao uso do CodeGraph, e MUST NOT apresentá-lo como passo obrigatório junto do `openspec init`.

#### Scenario: Projeto novo com o CodeGraph opcional
- **WHEN** o `kit.py novo` cria um projeto
- **THEN** a linha dos próximos passos que cita o `codegraph init` diz que ele vale só para quem usa o CodeGraph
- **AND** a mesma linha diz que ele roda em cada clone
- **AND** o item do `openspec init` não cita o `codegraph init`
