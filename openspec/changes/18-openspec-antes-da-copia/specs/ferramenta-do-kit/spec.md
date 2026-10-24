## MODIFIED Requirements

### Requirement: Update do OpenSpec que apagaria arquivos
Antes de mudar qualquer arquivo do projeto, o `kit.py atualizar --openspec` SHALL rodar o `openspec update --dry-run --json` na pasta do projeto, já na versão do kit. Se ele listar algum arquivo do projeto para apagar, sem a opção `--aceitar-apagados`, a ferramenta MUST NOT rodar o update nem mudar arquivo nenhum do projeto, e MUST terminar com o código 1, com uma recusa que nomeia esses arquivos, o comando `openspec config list` e a opção `--aceitar-apagados`. O que ele apagaria fora do projeto (no HOME ou num caminho absoluto) MUST NOT recusar o update; a ferramenta MUST avisá-lo, sem falhar.

#### Scenario: Perfil da máquina sem o que o projeto versiona
- **WHEN** o dry-run lista `.claude/skills/openspec-propose/SKILL.md` para apagar, a `trilha/` do projeto difere da do kit, e o `kit.py atualizar` roda com `--openspec`, sem `--aceitar-apagados`
- **THEN** a ferramenta não roda o `openspec update`, e a saída traz uma recusa que cita esse arquivo, o `openspec config list` e o `--aceitar-apagados`
- **AND** termina com o código de saída 1, sem o "commit sugerido", com o `git status` do projeto vazio e a `trilha/` dele como estava

#### Scenario: De novo depois da recusa
- **WHEN** o `kit.py atualizar --openspec` foi recusado porque o update apagaria arquivos do projeto, e roda de novo com um dry-run sem nada a apagar
- **THEN** a ferramenta não recusa o projeto por trabalho não commitado e roda o `openspec update`
- **AND** termina com o código de saída 0

#### Scenario: Apagados fora do projeto
- **WHEN** o dry-run lista para apagar só `~/.codex/prompts/opsx-ff.md` e `/etc/openspec/x.md`
- **THEN** a ferramenta roda o `openspec update`, e a saída traz um aviso que cita os dois
- **AND** termina com o código de saída 0

### Requirement: Falha da atualização do OpenSpec
Quando o projeto não tem a pasta `openspec/`, o CI do modelo do kit não fixa a versão do OpenSpec, o `npm` falta ou falha, o `openspec` do PATH responde outra versão depois da instalação, ou o dry-run falha, o `kit.py atualizar --openspec` MUST terminar com o código 1, com uma recusa que diz o que falhou, sem mudar arquivo nenhum do projeto. Quando o `openspec update`, que roda depois da cópia, falha, a ferramenta MUST terminar com o código 1, com uma FALHA que o cita, sem sugerir o commit; o que o kit já copiou fica no projeto, sem commit. Quando a migração do `check.sh` falharia, a ferramenta MUST NOT chamar o `npm` nem o `openspec update`.

#### Scenario: Projeto sem a pasta openspec
- **WHEN** o projeto não tem a pasta `openspec/`, a versão da máquina é outra, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a saída traz uma recusa que manda rodar o `kit.py atualizar` sem `--openspec`, fazer o commit e rodar de novo com `--openspec`, e a ferramenta não chama o `npm` nem o `openspec update`
- **AND** termina com o código de saída 1, com o `git status` do projeto vazio

#### Scenario: Máquina sem o npm
- **WHEN** a versão da máquina é outra e o comando `npm` não existe no PATH
- **THEN** a saída traz uma recusa que cita o `npm install -g @fission-ai/openspec@X`, e o `openspec update` não roda
- **AND** termina com o código de saída 1, sem o "commit sugerido", com o `git status` do projeto vazio

#### Scenario: Instalação que não muda o openspec do PATH
- **WHEN** a versão da máquina é outra, o `npm install` termina com 0, e o `openspec --version` continua respondendo a versão anterior
- **THEN** a saída traz uma recusa que cita outro `openspec` antes no PATH, e o `openspec update` não roda
- **AND** termina com o código de saída 1, com o `git status` do projeto vazio

#### Scenario: Update com erro
- **WHEN** o `openspec update` termina com erro
- **THEN** a saída traz uma FALHA que cita o `openspec update`
- **AND** termina com o código de saída 1, sem o "commit sugerido"

#### Scenario: Dry-run com erro
- **WHEN** o dry-run termina com erro, com a mensagem `No OpenSpec directory found.`
- **THEN** a saída traz essa mensagem e uma recusa que cita o dry-run, e o `openspec update` não roda
- **AND** termina com o código de saída 1, com o `git status` do projeto vazio

#### Scenario: Migração do check.sh que falha
- **WHEN** o `scripts/check.sh` do projeto ainda chama os `scripts/confere_*` fora da parte fixa do kit, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a ferramenta não chama o `npm` nem o `openspec update`
- **AND** termina com o código de saída 1

## ADDED Requirements

### Requirement: Aceite dos apagados no update do OpenSpec
Com `--openspec` e `--aceitar-apagados`, quando o dry-run listar arquivos do projeto para apagar, o `kit.py atualizar` SHALL avisar, sem falhar, com esses arquivos, e rodar o `openspec update`. Sem o `--openspec`, a opção `--aceitar-apagados` MUST ser recusada como erro de uso, antes de mudar qualquer arquivo.

#### Scenario: Apagados aceitos
- **WHEN** o dry-run lista `.claude/skills/openspec-propose/SKILL.md` para apagar, e o `kit.py atualizar` roda com `--openspec --aceitar-apagados`
- **THEN** a saída traz um aviso que cita esse arquivo, e a ferramenta roda o `openspec update`
- **AND** termina com o código de saída 0

#### Scenario: Opção sem o --openspec
- **WHEN** o `kit.py atualizar` roda com `--aceitar-apagados`, sem `--openspec`
- **THEN** a saída traz um erro de uso que diz que o `--aceitar-apagados` só vale com o `--openspec`, e a ferramenta não chama o `npm` nem o `openspec update`
- **AND** termina com o código de saída 2, com o `git status` do projeto vazio
