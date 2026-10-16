## ADDED Requirements

### Requirement: Recusa do kit atrás do projeto
O `kit.py atualizar` SHALL recusar, antes de mudar qualquer arquivo, o projeto cuja versão do comum é mais nova que a do kit, mandando atualizar o kit (`git pull`), e MUST NOT sugerir o commit nesse caso.

#### Scenario: Projeto mais novo que o kit
- **WHEN** o `kit.py atualizar` roda num projeto cujo comum está numa versão mais nova que a do kit (a 9.9, por exemplo); a proteção vale a partir do kit da 2.5, que a traz
- **THEN** a ferramenta recusa, citando as duas versões e o `git pull`, e termina com o código de saída 1
- **AND** o projeto fica sem mudança

### Requirement: Recusa do kit sem o histórico do git
O `kit.py atualizar` SHALL recusar, antes de mudar qualquer arquivo, o kit que não é um repositório git ou que é um clone raso, porque a atualização lê as versões antigas do kit pelo histórico.

#### Scenario: Kit sem o git
- **WHEN** o `kit.py atualizar` roda de uma cópia do kit sem o `.git` (baixada como ZIP)
- **THEN** a ferramenta recusa, dizendo que o kit precisa ser um clone do git, e termina com o código de saída 1
- **AND** o projeto fica sem mudança

#### Scenario: Kit extraído dentro de outro repositório
- **WHEN** o `kit.py atualizar` roda de uma cópia do kit sem o `.git`, extraída numa pasta que está dentro de outro repositório git
- **THEN** a ferramenta recusa, dizendo que o kit precisa ser um clone do git
- **AND** o projeto fica sem mudança

#### Scenario: Kit clonado raso
- **WHEN** o `kit.py atualizar` roda de um clone raso do kit
- **THEN** a ferramenta recusa, citando o `git fetch --unshallow --tags`
- **AND** o projeto fica sem mudança
