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

### Requirement: Aviso do plugin desligado
Quando o `sdd@trilha-ai` estiver instalado e desligado na pasta do projeto, a conferência do método SHALL avisar uma vez só, com o comando `claude plugin enable sdd@trilha-ai --scope <escopo>` no escopo da configuração que o desliga, sem falhar. O escopo SHALL vir da configuração que vale na pasta: a local (`.claude/settings.local.json`), que prevalece, a do projeto (`.claude/settings.json`) e, sem declaração nelas, a do usuário, pelo "ligado" da lista.

#### Scenario: Plugin do kit desligado
- **WHEN** a lista de plugins do Claude Code traz `sdd@trilha-ai` na versão do comum, com `enabled` falso, e o projeto não declara o plugin
- **THEN** a conferência imprime um aviso com `claude plugin enable sdd@trilha-ai --scope user`
- **AND** termina com o código de saída 0

#### Scenario: Plugin desligado pelo projeto
- **WHEN** o `.claude/settings.json` do projeto tem `sdd@trilha-ai` falso e a lista traz a instalação do usuário e a do projeto, esta com `enabled` verdadeiro
- **THEN** a conferência imprime um só aviso de desligado, com `claude plugin enable sdd@trilha-ai --scope project`

#### Scenario: Plugin desligado pela configuração local
- **WHEN** o `.claude/settings.local.json` do projeto tem `sdd@trilha-ai` falso
- **THEN** a conferência imprime um aviso com `claude plugin enable sdd@trilha-ai --scope local`

#### Scenario: Configuração local liga o que o projeto desliga
- **WHEN** o `.claude/settings.json` do projeto tem `sdd@trilha-ai` falso e o `.claude/settings.local.json` o tem verdadeiro
- **THEN** a conferência não imprime aviso de desligado

## ADDED Requirements

### Requirement: Instalação no projeto que declara o plugin
Quando o `.claude/settings.json` do projeto declara o `sdd@trilha-ai` ligado e a lista do Claude Code o traz instalado só para a máquina inteira, a conferência do método SHALL avisar, com `claude plugin install sdd@trilha-ai --scope project`, sem falhar: a máquina que recebe o projeto pelo git não roda o `kit.py`.

#### Scenario: Projeto declarado e plugin só do usuário
- **WHEN** o projeto declara o plugin e a lista traz só o `sdd@trilha-ai` de escopo `user`, na versão do comum
- **THEN** a conferência imprime um só aviso sobre o plugin, com `claude plugin install sdd@trilha-ai --scope project`
- **AND** termina com o código de saída 0

#### Scenario: Plugin instalado no projeto
- **WHEN** o projeto declara o plugin e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão do comum
- **THEN** a conferência não imprime aviso sobre o plugin

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
- **WHEN** o projeto não declara o plugin e a lista traz só o `sdd@trilha-ai` de escopo `user`, na versão do comum
- **THEN** a conferência não imprime aviso sobre o plugin

#### Scenario: Instalação do projeto atrás da versão
- **WHEN** o comum do projeto diz "Versão 2.2" e a lista traz o `sdd@trilha-ai` de escopo `project` na pasta do projeto, na versão `2.1.0`, e o de escopo `user` na versão `2.2.0`
- **THEN** a conferência imprime um só aviso de versão, que cita `2.1.0`, `2.2` e `claude plugin update sdd@trilha-ai --scope project`
