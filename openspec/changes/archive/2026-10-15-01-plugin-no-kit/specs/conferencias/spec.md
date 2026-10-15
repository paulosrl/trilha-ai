# Spec Delta

## Purpose

Define o que os verificadores que os projetos copiam do kit conferem e avisam antes do commit e no CI, para que um documento ou uma instalação fora do método seja apontado sem depender da máquina de quem o escreveu.

## ADDED Requirements

### Requirement: Plugin instalado lido pelo Claude Code
A conferência do método SHALL ler o plugin `sdd` instalado pela lista de plugins do próprio Claude Code (`claude plugin list --json`) e MUST NOT depender de outra pasta ao lado do projeto nem de arquivos internos do Claude Code.

#### Scenario: Pasta vizinha com outra versão
- **WHEN** existe, ao lado do projeto, uma pasta `pipeline-prd-tdd-openspec` com outra versão do plugin
- **THEN** o resultado da conferência é o mesmo que sem essa pasta

### Requirement: Aviso do plugin de fora do kit
Quando um plugin `sdd@…` instalado não for `sdd@trilha-ai` (o do marketplace antigo ou o de qualquer outro), a conferência do método SHALL avisar, nomeando-o, e mostrar como trocar para `sdd@trilha-ai`, com cada comando separado, sem falhar.

#### Scenario: Plugin do marketplace antigo
- **WHEN** a lista de plugins do Claude Code traz `sdd@pipeline-prd-tdd-openspec`
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai`
- **AND** termina com o código de saída 0

#### Scenario: Plugin de outro marketplace
- **WHEN** a lista de plugins do Claude Code traz só `sdd@meu-fork`
- **THEN** a conferência imprime um aviso que cita `sdd@meu-fork` e `claude plugin install sdd@trilha-ai`
- **AND** termina com o código de saída 0

#### Scenario: Comandos separados
- **WHEN** a conferência avisa sobre o plugin de fora do kit ou ausente
- **THEN** `claude plugin marketplace add paulosrl/trilha-ai` e `claude plugin install sdd@trilha-ai` aparecem como comandos separados, nunca ligados por `&&`, para que o install rode mesmo se o marketplace já existir

### Requirement: Aviso do plugin desligado
Quando o `sdd@trilha-ai` estiver instalado e desligado, a conferência do método SHALL avisar, com o comando `claude plugin enable sdd@trilha-ai`, sem falhar.

#### Scenario: Plugin do kit desligado
- **WHEN** a lista de plugins do Claude Code traz `sdd@trilha-ai` na versão do comum, com `enabled` falso
- **THEN** a conferência imprime um aviso com `claude plugin enable sdd@trilha-ai`
- **AND** termina com o código de saída 0

### Requirement: Conferência do plugin fora da trava do commit
A trava do commit SHALL rodar a conferência do método sem consultar o Claude Code, para continuar rápida; o aviso do plugin MUST continuar na verificação do repositório (`scripts/check.sh`), que o método manda rodar antes do commit.

#### Scenario: Commit sem consultar o Claude Code
- **WHEN** a trava do commit roda num projeto feito do kit, numa máquina com o Claude Code
- **THEN** a lista de plugins do Claude Code não é consultada

#### Scenario: Verificação do repositório com o aviso
- **WHEN** o `scripts/check.sh` roda numa máquina com o plugin de fora do kit
- **THEN** o aviso do plugin aparece

### Requirement: Aviso da versão do plugin diferente da do projeto
Quando a versão do `sdd@trilha-ai` instalado não for `X.Y.0` para a "Versão X.Y" do `CLAUDE-comum.md` do projeto, a conferência do método SHALL avisar, nomeando as duas versões, sem falhar.

#### Scenario: Versões diferentes
- **WHEN** o comum do projeto diz "Versão 1.35" e o plugin instalado é `sdd@trilha-ai` na versão `1.34.0`
- **THEN** a conferência imprime um aviso que cita `1.34.0` e `1.35`
- **AND** termina com o código de saída 0

#### Scenario: Versões iguais
- **WHEN** o comum do projeto diz "Versão 1.35" e o plugin instalado é `sdd@trilha-ai` na versão `1.35.0`
- **THEN** a conferência não imprime aviso sobre o plugin

### Requirement: Aviso do plugin ausente
Quando o Claude Code responder e nenhum plugin `sdd` estiver instalado, a conferência do método SHALL avisar, com o comando de instalação, sem falhar.

#### Scenario: Claude Code sem o plugin
- **WHEN** a lista de plugins do Claude Code não traz nenhum `sdd@…`
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai`
- **AND** termina com o código de saída 0

### Requirement: Silêncio sem o Claude Code
Quando o Claude Code não estiver disponível, ou a lista de plugins falhar, a conferência do método SHALL seguir sem aviso nem falha sobre o plugin, como no CI.

#### Scenario: Máquina sem o Claude Code
- **WHEN** o comando `claude` não existe no PATH
- **THEN** a conferência não imprime aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin

#### Scenario: Lista de plugins com erro
- **WHEN** `claude plugin list --json` termina com erro ou devolve um texto que não é JSON
- **THEN** a conferência não imprime aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin
