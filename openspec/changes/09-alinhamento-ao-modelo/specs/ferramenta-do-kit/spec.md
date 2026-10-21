## RENAMED Requirements

- FROM: `### Requirement: Aviso da parte fixa que mudou no kit`
- TO: `### Requirement: Aviso da parte fixa que falta no projeto`

## MODIFIED Requirements

### Requirement: Aviso da parte fixa que falta no projeto
O `kit.py atualizar` SHALL avisar cada linha da parte fixa do modelo atual que o projeto não tem, em qualquer versão dele, aceitando como presente a linha igual, a mesma seguida de espaço e argumentos ou ela como comando dentro de uma linha do projeto, depois de um espaço. MUST NOT avisar os blocos da parte da stack (os que abrem com o comentário "# Parte da stack" e, no `.gitignore`, `# Python` e `# Node`). O que o kit tirou SHALL seguir pela diferença entre as versões.

#### Scenario: Chamada com os vizinhos
- **WHEN** o `scripts/check.sh` migrado tem `bash trilha/verifica.sh --vizinho trilha-ai \`
- **THEN** a ferramenta não avisa que falta `bash trilha/verifica.sh`

#### Scenario: Linha curta que falta
- **WHEN** o kit acrescentou à parte fixa a linha `fi` e o projeto só tem uma linha que começa com `fi` sem ser ela (por exemplo, `find .`)
- **THEN** a ferramenta avisa que falta `fi`

#### Scenario: Linha que o projeto nunca copiou
- **WHEN** o modelo do `.gitignore` já trazia `*.log` na versão do projeto e o `.gitignore` do projeto não o tem
- **THEN** a ferramenta avisa que falta `*.log`

#### Scenario: Bloco da stack apagado
- **WHEN** o `.gitignore` do projeto não tem o bloco `# Python` do modelo
- **THEN** a ferramenta não avisa que falta `.venv/`

#### Scenario: Chamada dentro de uma função do projeto
- **WHEN** o `scripts/check.sh` do projeto chama `etapa "regras" bash trilha/verifica.sh --vizinho trilha-ai`
- **THEN** a ferramenta não avisa que falta `bash trilha/verifica.sh`

#### Scenario: Bloco da parte da stack trocado
- **WHEN** o `scripts/check.sh` do projeto trocou o bloco "Parte da stack" do modelo pelos comandos da stack dele
- **THEN** a ferramenta não avisa a linha `echo` daquele bloco

#### Scenario: Passo fixo do CI ao lado do comentário da stack
- **WHEN** o CI do projeto não tem o passo `actions/setup-node` do modelo, que fica no mesmo bloco do comentário "Parte da stack"
- **THEN** a ferramenta avisa que falta a linha do `actions/setup-node`
