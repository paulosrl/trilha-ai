# Spec Delta

## Purpose

Define como o kit Trilha AI publica o plugin `sdd`, com as skills `prd`, `tdd` e `briefing`, e como a versão do plugin acompanha a versão do kit, para que o método tenha uma fonte e uma versão só.

## ADDED Requirements

### Requirement: Marketplace publicado pelo kit
O kit SHALL publicar, na raiz do repositório, um marketplace do Claude Code chamado `trilha-ai`, que lista o plugin `sdd` a partir de `./plugins/sdd`, para que `claude plugin marketplace add paulosrl/trilha-ai` e `claude plugin install sdd@trilha-ai` instalem o plugin.

#### Scenario: Marketplace lido da raiz do kit
- **WHEN** o arquivo `.claude-plugin/marketplace.json` da raiz do kit é lido
- **THEN** o nome do marketplace é `trilha-ai`
- **AND** ele lista um plugin chamado `sdd` com a origem `./plugins/sdd`
- **AND** o manifesto `plugins/sdd/.claude-plugin/plugin.json` existe e declara o nome `sdd`

#### Scenario: As três skills no plugin
- **WHEN** a pasta `plugins/sdd/skills/` do kit é lida
- **THEN** existem `prd/SKILL.md`, `tdd/SKILL.md` e `briefing/SKILL.md`
- **AND** cada uma declara, no cabeçalho, o nome igual ao da pasta

#### Scenario: Nenhuma referência ao repositório antigo no plugin
- **WHEN** os arquivos de `.claude-plugin/` e de `plugins/` do kit são lidos
- **THEN** nenhum deles cita `pipeline-prd-tdd-openspec`

### Requirement: Versão do plugin igual à do kit
A versão declarada no manifesto do plugin MUST ser `X.Y.0` quando a linha de versão do `modelo/CLAUDE-comum.md` for "Versão X.Y", e os testes do kit MUST reprovar qualquer divergência entre as duas.

#### Scenario: Versões iguais
- **WHEN** o comum diz "Versão 1.35" e o manifesto do plugin declara `1.35.0`
- **THEN** os testes do kit passam

#### Scenario: Versão do plugin esquecida
- **WHEN** o comum sobe para uma versão nova e o manifesto do plugin continua com a anterior
- **THEN** os testes do kit reprovam, nomeando as duas versões
