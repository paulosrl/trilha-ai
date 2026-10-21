## RENAMED Requirements

- FROM: `### Requirement: Aviso da parte fixa que mudou no kit`
- TO: `### Requirement: Aviso da parte fixa que falta no projeto`

## MODIFIED Requirements

### Requirement: Aviso da parte fixa que falta no projeto
O `kit.py atualizar` SHALL avisar cada linha da parte fixa do modelo atual dos arquivos preenchidos que o projeto não tem, qualquer que seja a versão do projeto, aceitando como presente só a linha igual ou a mesma linha seguida de espaço e argumentos. No `.gitignore`, MUST NOT avisar as linhas dos blocos da stack (os de comentário `# Python` e `# Node`). O aviso das linhas que o kit tirou SHALL seguir pela diferença entre a versão do projeto e a atual.

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
