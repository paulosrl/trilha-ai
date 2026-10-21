## ADDED Requirements

### Requirement: Regras por artefato iguais às do kit
Com a pasta do kit indicada, a conferência das regras SHALL comparar o bloco `rules:` do `openspec/config.yaml` do projeto com o do modelo do kit na versão do projeto, escolhida como na pasta `trilha/`, e MUST reprovar o bloco diferente e cada linha do `operations` do kit que falte no projeto. Linhas próprias a mais no `operations`, chaves próprias no topo do arquivo e o projeto sem o `config.yaml` MUST NOT reprovar.

#### Scenario: Regras iguais às do kit
- **WHEN** o bloco `rules:` e o `operations` do `openspec/config.yaml` do projeto são os do modelo do kit
- **THEN** a conferência das regras não reprova pelo `config.yaml`

#### Scenario: Regras próprias
- **WHEN** o bloco `rules:` do projeto tem uma regra que o modelo do kit não tem
- **THEN** a conferência das regras reprova, citando o `openspec/config.yaml` e o bloco `rules:`

#### Scenario: Linha do operations que falta
- **WHEN** falta no `operations` do projeto uma linha do `operations` do modelo do kit
- **THEN** a conferência das regras reprova, citando o começo da linha que falta

#### Scenario: Acréscimos próprios aceitos
- **WHEN** o projeto tem as regras do kit, uma linha a mais no `operations.archive` e a chave `githubCopilot` no topo
- **THEN** a conferência das regras não reprova pelo `config.yaml`

#### Scenario: Projeto na versão anterior do kit
- **WHEN** o kit está numa versão nova, com regras mudadas, e o projeto, na anterior, tem as regras da tag dela
- **THEN** a conferência das regras não reprova pelo `config.yaml`

#### Scenario: Projeto sem o config.yaml
- **WHEN** o projeto não tem `openspec/config.yaml`
- **THEN** a conferência das regras não reprova pelo `config.yaml`
