## MODIFIED Requirements

### Requirement: Só sob demanda
O `trilha-ai/tempo.py` SHALL rodar só quando chamado, de dentro de um repositório git. O modelo do `.claude/settings.json` do kit MUST NOT ligar o `tempo.py` a nenhum gancho do Claude Code. Fora de um repositório git, o comando MUST terminar com código diferente de 0 e dizer por quê, sem escrever nada.

#### Scenario: Nenhum gancho no modelo
- **WHEN** o `modelo/claude-settings.json` do kit é lido
- **THEN** nenhum comando de gancho cita o `tempo.py`

#### Scenario: Fora de um repositório
- **WHEN** o comando roda numa pasta que não pertence a um repositório git
- **THEN** ele termina com código diferente de 0, com uma mensagem que diz que a pasta não é um repositório git
- **AND** nenhum arquivo é criado na pasta de dados do usuário

