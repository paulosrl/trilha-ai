# Spec Delta

## ADDED Requirements

### Requirement: Decomposição no esqueleto da skill
A conferência do método SHALL exigir que a decomposição (`sdd/decomposicao-*.md`) tenha as linhas de título `## 1.`, `## 2.` e `## Ciclo`, cada uma no começo da linha e fora de bloco de código, lendo cada seção até o título seguinte, de qualquer nível, e MUST reprovar a que não tiver, nomeando cada título que falta e o esqueleto da skill `sdd:briefing`.

#### Scenario: Esqueleto da skill
- **WHEN** a decomposição é o esqueleto que a skill `sdd:briefing` traz, com ou sem uma change retirada
- **THEN** a conferência do método termina com o código de saída 0

#### Scenario: Título só dentro do texto
- **WHEN** a decomposição tem `## Ciclo` e `## 2.` como títulos, mas `## 1.` só aparece dentro de outra linha (por exemplo, em `### 1. Recepção`)
- **THEN** a conferência do método reprova, citando `## 1.` e a skill `sdd:briefing`

#### Scenario: Sem a seção 2
- **WHEN** a decomposição tem os títulos `## 1.` e `## Ciclo`, e não o `## 2.`
- **THEN** a conferência do método reprova, citando `## 2.`

#### Scenario: Subseção depois do Ciclo
- **WHEN** a decomposição traz, depois da tabela do `## Ciclo`, uma subseção `###` com outra tabela numerada
- **THEN** a conferência do método compara só a tabela do "Ciclo" com a da seção 1 e termina com o código de saída 0

#### Scenario: Título citado em bloco de código
- **WHEN** a decomposição cita, dentro de um bloco de código, um `## 2.` ou um `## Ciclo` com uma tabela
- **THEN** o título citado não conta: sem o `## 2.` de verdade, a conferência reprova, citando `## 2.`; com os três de verdade, a tabela citada não entra na comparação

### Requirement: Aviso da stack por preencher depois do TDD
Quando a pasta `sdd/` tiver um `tdd-*.md`, a conferência das regras SHALL avisar, sem falhar, cada lugar da stack que ainda traz o texto do modelo do kit que pede o preenchimento: `scripts/check.sh`, `.github/workflows/verificacao.yml`, `.github/dependabot.yml`, `.gitignore` e a linha "Stack" do `openspec/config.yaml`. Sem TDD, ela MUST NOT dar esse aviso.

#### Scenario: TDD com a stack do modelo
- **WHEN** o projeto feito do kit tem um `sdd/tdd-x.md` e os cinco lugares da stack como o modelo os deixou
- **THEN** a conferência das regras imprime um aviso que cita os cinco
- **AND** termina com o código de saída 0

#### Scenario: Stack preenchida
- **WHEN** o projeto tem um `sdd/tdd-x.md` e nenhum dos cinco lugares traz mais o texto do modelo que pede o preenchimento
- **THEN** a conferência das regras não imprime o aviso da stack

#### Scenario: Stack preenchida como o modelo pede
- **WHEN** o projeto tem um `sdd/tdd-x.md`, apagou do `.gitignore` o bloco da stack que não é a sua e o comentário que pede isso, e trocou os exemplos do `.github/dependabot.yml` pelo bloco real, apagando o comentário que pede isso
- **THEN** o aviso da stack não cita o `.gitignore` nem o `.github/dependabot.yml`

#### Scenario: Projeto sem TDD
- **WHEN** o projeto feito do kit não tem `sdd/tdd-*.md`
- **THEN** a conferência das regras não imprime o aviso da stack

### Requirement: Teto de tamanho das regras carregadas
A conferência das regras SHALL reprovar o projeto cujo `CLAUDE.md` e `trilha/CLAUDE-comum.md` somados passem de 200 linhas ou de 32.768 bytes (32 KB), citando a soma e o limite que ela passou.

#### Scenario: Regras largas demais
- **WHEN** o `CLAUDE.md` e o comum somam menos de 200 linhas e mais de 32.768 bytes
- **THEN** a conferência das regras reprova, citando os bytes e o limite de 32.768

#### Scenario: Linhas demais
- **WHEN** o `CLAUDE.md` e o comum somam mais de 200 linhas
- **THEN** a conferência das regras reprova, citando as linhas e o limite de 200

#### Scenario: Projeto novo dentro do teto
- **WHEN** a conferência das regras roda num projeto recém-criado pelo kit
- **THEN** ela não reprova pelo tamanho

## MODIFIED Requirements

### Requirement: Silêncio sem o Claude Code
Quando o Claude Code não estiver disponível, ou a lista de plugins falhar ou não responder no prazo (10 segundos), a conferência do método SHALL seguir sem aviso nem falha sobre o plugin, como no CI.

#### Scenario: Máquina sem o Claude Code
- **WHEN** o comando `claude` não existe no PATH
- **THEN** a conferência não imprime aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin

#### Scenario: Lista de plugins com erro
- **WHEN** `claude plugin list --json` termina com erro ou devolve um texto que não é JSON
- **THEN** a conferência não imprime aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin

#### Scenario: Lista de plugins sem resposta no prazo
- **WHEN** `claude plugin list --json` não termina dentro do prazo
- **THEN** a conferência segue sem esperar mais, sem imprimir aviso sobre o plugin
- **AND** o código de saída não muda por causa do plugin
