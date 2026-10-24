## MODIFIED Requirements

### Requirement: Aviso dos arquivos gerados que o update mudaria
A conferência do método SHALL perguntar ao próprio OpenSpec, pelo `openspec update --dry-run --json` rodado na raiz do projeto e sem consultar a rede, o que o update mudaria, e MUST avisar, sem falhar, nomeando cada arquivo do projeto que ele apagaria, criaria ou trocaria, com o comando `openspec config list`. O que o dry-run lista fora do projeto MUST NOT entrar no aviso. A conferência MUST NOT mudar nenhum arquivo do projeto nem a configuração do OpenSpec da máquina.

#### Scenario: Perfil só com comandos e skills no projeto
- **WHEN** o perfil do OpenSpec da máquina entrega só comandos, o projeto versiona `.claude/skills/openspec-propose/SKILL.md` e o dry-run o lista para apagar
- **THEN** a conferência imprime um aviso que cita `.claude/skills/openspec-propose/SKILL.md` como arquivo que o `openspec update` apagaria e o comando `openspec config list`
- **AND** termina com o código de saída 0

#### Scenario: Perfil igual aos arquivos do projeto
- **WHEN** o dry-run do `openspec update` não lista nenhuma mudança
- **THEN** a conferência não imprime aviso sobre os arquivos gerados

#### Scenario: Projeto intacto depois do aviso
- **WHEN** a conferência avisa que o `openspec update` apagaria arquivos gerados
- **THEN** os arquivos do projeto continuam como estavam antes da conferência

#### Scenario: Configuração da máquina intacta
- **WHEN** o dry-run lista a configuração global da máquina para trocar (a migração que o OpenSpec faz quando ela não tem o perfil), pelo caminho dela: com `~/` no HOME, o lugar padrão, ou o absoluto fora dele
- **THEN** o aviso não cita a configuração global
- **AND** a configuração global da máquina continua como estava antes da conferência

#### Scenario: Arquivos que ele criaria ou trocaria
- **WHEN** o dry-run lista um arquivo gerado para adicionar e outro para trocar
- **THEN** o aviso cita o primeiro em "criaria" e o segundo em "trocaria"

### Requirement: Silêncio do ensaio sem o OpenSpec da máquina
A conferência do método SHALL seguir sem aviso nem falha sobre os arquivos gerados quando o `openspec` não estiver no PATH, quando a máquina não tiver o arquivo de configuração global dele (como no CI), quando o dry-run falhar, não responder o JSON esperado ou não terminar no prazo, ou quando o projeto não versionar nenhum arquivo gerado.

#### Scenario: Máquina sem o OpenSpec
- **WHEN** o comando `openspec` não existe no PATH
- **THEN** a conferência não imprime aviso sobre os arquivos gerados
- **AND** o código de saída não muda por causa do OpenSpec

#### Scenario: Máquina sem a configuração global
- **WHEN** o `openspec config path` aponta um arquivo que não existe
- **THEN** a conferência não roda o dry-run do `openspec update` e não imprime aviso sobre os arquivos gerados

#### Scenario: Ensaio com erro ou sem resposta no prazo
- **WHEN** o dry-run do `openspec update` termina com erro ou não termina dentro do prazo
- **THEN** a conferência não imprime aviso sobre os arquivos gerados
- **AND** o código de saída não muda por causa do OpenSpec

#### Scenario: Dry-run com falhas ou sem o JSON esperado
- **WHEN** o dry-run termina com o código 0, mas com a lista `failures` não vazia ou com uma saída que não é o JSON dele
- **THEN** a conferência não imprime aviso sobre os arquivos gerados

#### Scenario: OpenSpec sem o dry-run
- **WHEN** o `openspec` da máquina é anterior à 1.15 e recusa a opção `--dry-run` com erro
- **THEN** a conferência não imprime aviso sobre os arquivos gerados
- **AND** o aviso da versão diferente da do CI continua valendo

#### Scenario: Projeto sem arquivos gerados
- **WHEN** o projeto não versiona nenhum arquivo gerado do OpenSpec
- **THEN** a conferência não roda o dry-run do `openspec update`
