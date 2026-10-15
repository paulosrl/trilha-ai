# Spec Delta

## Purpose

Define o que os verificadores que os projetos copiam do kit conferem e avisam antes do commit e no CI, para que um documento ou uma instalação fora do método seja apontado sem depender da máquina de quem o escreveu.

## ADDED Requirements

### Requirement: Plugin instalado lido pelo Claude Code
A conferência do método SHALL ler o plugin `sdd` instalado pela lista de plugins do próprio Claude Code (`claude plugin list --json`) e MUST NOT depender de outra pasta ao lado do projeto nem de arquivos internos do Claude Code.

#### Scenario: Pasta vizinha com outra versão
- **WHEN** existe, ao lado do projeto, uma pasta `pipeline-prd-tdd-openspec` com outra versão do plugin
- **THEN** o resultado da conferência é o mesmo que sem essa pasta

### Requirement: Aviso do plugin do marketplace antigo
Quando o plugin instalado for `sdd@pipeline-prd-tdd-openspec`, a conferência do método SHALL avisar que ele vem do marketplace antigo e mostrar os comandos para trocar para `sdd@trilha-ai`, sem falhar.

#### Scenario: Plugin do marketplace antigo
- **WHEN** a lista de plugins do Claude Code traz `sdd@pipeline-prd-tdd-openspec`
- **THEN** a conferência imprime um aviso com `claude plugin install sdd@trilha-ai`
- **AND** termina com o código de saída 0

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
