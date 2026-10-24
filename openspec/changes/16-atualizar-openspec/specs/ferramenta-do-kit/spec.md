## ADDED Requirements

### Requirement: Atualização do OpenSpec sob pedido
Com a opção `--openspec`, o `kit.py atualizar` SHALL instalar o OpenSpec na versão fixada no CI do modelo do kit (`npm install -g @fission-ai/openspec@X`) quando a da máquina for outra ou faltar, e depois rodar o `openspec update` na pasta do projeto, sem consultar a rede por versão nova, antes da conferência. Sem a opção, o `kit.py atualizar` MUST NOT chamar o `npm` nem o `openspec update`.

#### Scenario: Versão da máquina diferente da do kit
- **WHEN** o `openspec --version` responde `1.14.1`, o CI do modelo do kit fixa `1.15.0`, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a ferramenta roda `npm install -g @fission-ai/openspec@1.15.0` e depois o `openspec update` na pasta do projeto
- **AND** termina com o código de saída 0

#### Scenario: Versão da máquina igual à do kit
- **WHEN** o `openspec --version` responde a versão que o CI do modelo do kit fixa, e o `kit.py atualizar` roda com `--openspec`
- **THEN** a ferramenta não chama o `npm` e roda o `openspec update` na pasta do projeto

#### Scenario: Sem a opção
- **WHEN** o `kit.py atualizar` roda sem `--openspec`
- **THEN** a ferramenta não chama o `npm` nem o `openspec update`

### Requirement: Update do OpenSpec que apagaria arquivos
Antes do `openspec update`, o `kit.py atualizar --openspec` SHALL rodar o `openspec update --dry-run --json` na pasta do projeto; se ele listar algum arquivo do projeto para apagar, a ferramenta MUST NOT rodar o update e MUST terminar com o código 1, com uma FALHA que nomeia esses arquivos e o comando `openspec config list`.

#### Scenario: Perfil da máquina sem o que o projeto versiona
- **WHEN** o dry-run lista `.claude/skills/openspec-propose/SKILL.md` para apagar
- **THEN** a ferramenta não roda o `openspec update`, e a saída traz uma FALHA que cita esse arquivo e o `openspec config list`
- **AND** termina com o código de saída 1, e o arquivo continua no projeto

### Requirement: Falha da atualização do OpenSpec
Quando o `npm` falta ou falha, o `openspec` falta depois da instalação, ou o dry-run ou o `openspec update` falham, o `kit.py atualizar --openspec` MUST terminar com o código 1, com uma FALHA que diz o que falhou, sem sugerir o commit; o que o kit já copiou fica no projeto, sem commit.

#### Scenario: Máquina sem o npm
- **WHEN** a versão da máquina é outra e o comando `npm` não existe no PATH
- **THEN** a saída traz uma FALHA que cita o `npm install -g @fission-ai/openspec@X`, e o `openspec update` não roda
- **AND** termina com o código de saída 1, sem o "commit sugerido"

#### Scenario: Update com erro
- **WHEN** o `openspec update` termina com erro
- **THEN** a saída traz uma FALHA que cita o `openspec update`
- **AND** termina com o código de saída 1, sem o "commit sugerido"

### Requirement: Aviso da versão do OpenSpec no atualizar
Sem a opção `--openspec`, quando a versão do `openspec` da máquina diferir da fixada no CI do modelo do kit, o `kit.py atualizar` SHALL avisar, sem falhar, com as duas versões e a opção `--openspec`; sem o `openspec`, ou com a mesma versão, MUST seguir sem esse aviso.

#### Scenario: Versão diferente sem a opção
- **WHEN** o `openspec --version` responde `1.14.1`, o CI do modelo do kit fixa `1.15.0`, e o `kit.py atualizar` roda sem `--openspec`
- **THEN** a saída traz um aviso que cita `1.14.1`, `1.15.0` e `--openspec`

#### Scenario: Versão igual sem a opção
- **WHEN** o `openspec --version` responde a versão que o CI do modelo do kit fixa
- **THEN** a saída não traz o aviso da opção `--openspec`
