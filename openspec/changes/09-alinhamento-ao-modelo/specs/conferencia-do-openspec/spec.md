## ADDED Requirements

### Requirement: Aviso dos arquivos gerados que o update mudaria
A conferência do método SHALL ensaiar o `openspec update` numa pasta temporária, com a cópia dos arquivos gerados do OpenSpec que o projeto versiona e do `openspec/config.yaml`, sem consultar a rede, e MUST avisar, sem falhar, nomeando cada arquivo que ele apagaria, criaria ou trocaria, com o comando `openspec config list`. O ensaio MUST NOT mudar nenhum arquivo do projeto.

#### Scenario: Perfil só com comandos e skills no projeto
- **WHEN** o perfil do OpenSpec da máquina entrega só comandos e o projeto versiona `.claude/skills/openspec-propose/SKILL.md`
- **THEN** a conferência imprime um aviso que cita `.claude/skills/openspec-propose/SKILL.md` como arquivo que o `openspec update` apagaria e o comando `openspec config list`
- **AND** termina com o código de saída 0

#### Scenario: Perfil igual aos arquivos do projeto
- **WHEN** o ensaio do `openspec update` termina sem apagar, criar nem trocar nenhum arquivo gerado
- **THEN** a conferência não imprime aviso sobre os arquivos gerados

#### Scenario: Projeto intacto depois do aviso
- **WHEN** a conferência avisa que o `openspec update` apagaria arquivos gerados
- **THEN** os arquivos do projeto continuam como estavam antes da conferência

### Requirement: Silêncio do ensaio sem o OpenSpec da máquina
A conferência do método SHALL seguir sem aviso nem falha sobre os arquivos gerados quando o `openspec` não estiver no PATH, quando a máquina não tiver o arquivo de configuração global dele (como no CI), quando o ensaio falhar ou não terminar no prazo, ou quando o projeto não versionar nenhum arquivo gerado.

#### Scenario: Máquina sem o OpenSpec
- **WHEN** o comando `openspec` não existe no PATH
- **THEN** a conferência não imprime aviso sobre os arquivos gerados
- **AND** o código de saída não muda por causa do OpenSpec

#### Scenario: Máquina sem a configuração global
- **WHEN** o `openspec config path` aponta um arquivo que não existe
- **THEN** a conferência não ensaia o `openspec update` e não imprime aviso sobre os arquivos gerados

#### Scenario: Ensaio com erro ou sem resposta no prazo
- **WHEN** o `openspec update` do ensaio termina com erro ou não termina dentro do prazo
- **THEN** a conferência não imprime aviso sobre os arquivos gerados
- **AND** o código de saída não muda por causa do OpenSpec

#### Scenario: Projeto sem arquivos gerados
- **WHEN** o projeto não versiona nenhum arquivo gerado do OpenSpec
- **THEN** a conferência não ensaia o `openspec update`

### Requirement: Aviso da versão do OpenSpec diferente da do CI
Quando a versão do `openspec` instalado diferir da fixada no `.github/workflows/verificacao.yml` do projeto (`@fission-ai/openspec@X`), a conferência do método SHALL avisar, nomeando as duas versões e o comando `npm install -g @fission-ai/openspec@X`, sem falhar; sem a versão fixada ou sem o `openspec`, MUST seguir sem aviso.

#### Scenario: Versões diferentes
- **WHEN** o `openspec --version` responde `1.14.3` e o CI do projeto instala `@fission-ai/openspec@1.14.1`
- **THEN** a conferência imprime um aviso que cita `1.14.3`, `1.14.1` e `npm install -g @fission-ai/openspec@1.14.1`
- **AND** termina com o código de saída 0

#### Scenario: Versões iguais
- **WHEN** o `openspec --version` responde a mesma versão que o CI do projeto instala
- **THEN** a conferência não imprime aviso sobre a versão do OpenSpec

#### Scenario: CI sem a versão fixada
- **WHEN** o `.github/workflows/verificacao.yml` do projeto não existe ou não traz `@fission-ai/openspec@`
- **THEN** a conferência não imprime aviso sobre a versão do OpenSpec

### Requirement: Conferência do OpenSpec fora da trava do commit
A trava do commit SHALL rodar a conferência do método sem consultar o `openspec`, para continuar rápida; os avisos do OpenSpec MUST continuar na verificação do repositório (`scripts/check.sh`).

#### Scenario: Commit sem consultar o OpenSpec
- **WHEN** a trava do commit roda num projeto feito do kit, numa máquina com o OpenSpec
- **THEN** nem o `openspec update` nem o `openspec --version` são chamados
