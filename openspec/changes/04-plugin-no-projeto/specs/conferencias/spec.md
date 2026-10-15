## MODIFIED Requirements

### Requirement: Aviso do plugin ausente
Quando o Claude Code responder e nenhum plugin `sdd` valer no projeto, a conferência do método SHALL avisar, com o comando de instalação no projeto (`claude plugin install sdd@trilha-ai --scope project`), sem falhar.

#### Scenario: Claude Code sem o plugin
- **WHEN** a lista de plugins do Claude Code não traz nenhum `sdd@…`
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai --scope project`
- **AND** termina com o código de saída 0

#### Scenario: Plugin instalado só para outro projeto
- **WHEN** a lista de plugins do Claude Code traz o `sdd@trilha-ai` só com o escopo `project`, na pasta de outro projeto
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai --scope project`
- **AND** termina com o código de saída 0

## ADDED Requirements

### Requirement: Lista de plugins lida da pasta do projeto
A conferência do método SHALL consultar a lista de plugins do Claude Code com a pasta do projeto como pasta de trabalho, de onde quer que seja chamada, porque o "ligado" que a lista devolve segue o `.claude/settings.json` da pasta em que ela roda.

#### Scenario: Conferência chamada de outra pasta
- **WHEN** a conferência do método de um projeto é chamada a partir de outra pasta
- **THEN** a lista de plugins do Claude Code roda na pasta do projeto

### Requirement: Instalação que vale no projeto
Das instalações do plugin `sdd` que a lista traz, a conferência do método SHALL julgar só a que vale no projeto: a de escopo `local` ou `project` cuja pasta é a do projeto e, sem ela, a de escopo `user`. A instalação de escopo `local` ou `project` de outra pasta MUST NOT contar.

#### Scenario: Instalação do projeto e do usuário em versões diferentes
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.2.0`, e o de escopo `user` na versão `1.35.0`
- **THEN** a conferência não imprime aviso sobre o plugin

#### Scenario: Só a instalação do usuário
- **WHEN** a lista traz só o `sdd@trilha-ai` de escopo `user`, na versão do comum
- **THEN** a conferência não imprime aviso sobre o plugin

#### Scenario: Instalação do projeto atrás da versão
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.1.0`, e o de escopo `user` na versão `2.2.0`
- **THEN** a conferência imprime um aviso que cita `2.1.0` e `2.2`
