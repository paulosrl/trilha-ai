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

### Requirement: Instalações que podem valer no projeto
Das instalações do plugin `sdd` que a lista traz, a conferência do método SHALL julgar todas as que podem valer no projeto: as sem pasta (escopo `user` ou outro da máquina inteira) e as de escopo `local` ou `project` cuja pasta é a do projeto. A de escopo `local` ou `project` de outra pasta MUST NOT contar. O aviso de versão SHALL dizer o escopo da instalação e trazer o comando de atualização com esse escopo.

#### Scenario: Instalação do usuário atrás da do projeto
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.2.0`, e o de escopo `user` na versão `1.35.0`
- **THEN** a conferência imprime um só aviso de versão, que cita `1.35.0`, `2.2` e `claude plugin update sdd@trilha-ai --scope user`

#### Scenario: Só a instalação do usuário
- **WHEN** a lista traz só o `sdd@trilha-ai` de escopo `user`, na versão do comum
- **THEN** a conferência não imprime aviso sobre o plugin

#### Scenario: Instalação do projeto atrás da versão
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.1.0`, e o de escopo `user` na versão `2.2.0`
- **THEN** a conferência imprime um só aviso de versão, que cita `2.1.0`, `2.2` e `claude plugin update sdd@trilha-ai --scope project`
