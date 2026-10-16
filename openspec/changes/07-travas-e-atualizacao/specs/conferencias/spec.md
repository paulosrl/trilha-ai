## MODIFIED Requirements

### Requirement: Aviso da stack por preencher depois do TDD
Quando a pasta `sdd/` tiver um `tdd-*.md`, a conferência das regras SHALL avisar, sem falhar, cada lugar da stack que ainda traz o texto do modelo do kit que pede o preenchimento: o `.github/dependabot.yml`, o `.gitignore` e a linha "Stack" do `openspec/config.yaml`, desde o TDD; o `scripts/check.sh` e o `.github/workflows/verificacao.yml`, só a partir do primeiro spec em `openspec/specs/`, que a change 01 cria. Sem TDD, ela MUST NOT dar esse aviso.

#### Scenario: TDD com a stack do modelo
- **WHEN** o projeto feito do kit tem um `sdd/tdd-x.md`, nenhum spec em `openspec/specs/` e os cinco lugares da stack como o modelo os deixou
- **THEN** a conferência das regras imprime um aviso que cita o `.github/dependabot.yml`, o `.gitignore` e o `openspec/config.yaml`
- **AND** o aviso não cita o `scripts/check.sh` nem o `.github/workflows/verificacao.yml`
- **AND** termina com o código de saída 0

#### Scenario: Change 01 arquivada com a stack do modelo
- **WHEN** o projeto tem um `sdd/tdd-x.md`, um spec em `openspec/specs/` e os cinco lugares da stack como o modelo os deixou
- **THEN** a conferência das regras imprime um aviso que cita os cinco

#### Scenario: Stack preenchida
- **WHEN** o projeto tem um `sdd/tdd-x.md` e nenhum dos cinco lugares traz mais o texto do modelo que pede o preenchimento
- **THEN** a conferência das regras não imprime o aviso da stack

#### Scenario: Stack preenchida como o modelo pede
- **WHEN** o projeto tem um `sdd/tdd-x.md`, apagou do `.gitignore` o bloco da stack que não é a sua e o comentário que pede isso, e trocou os exemplos do `.github/dependabot.yml` pelo bloco real, apagando o comentário que pede isso
- **THEN** o aviso da stack não cita o `.gitignore` nem o `.github/dependabot.yml`

#### Scenario: Projeto sem TDD
- **WHEN** o projeto feito do kit não tem `sdd/tdd-*.md`
- **THEN** a conferência das regras não imprime o aviso da stack
