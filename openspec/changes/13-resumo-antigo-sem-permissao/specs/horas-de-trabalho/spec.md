# Spec Delta

## MODIFIED Requirements

### Requirement: Repositório que mudou de pasta
Quando há outro resumo do mesmo nome de repositório com outro caminho de raiz, e esse caminho já não tem um repositório git (a pasta `.git`), o comando SHALL juntar as conversas dele às deste resumo, renomear o arquivo dele e a página dele com o sufixo `.juntado`, sem apagá-los nem sobrescrever um `.juntado` anterior, e avisar, sem falhar, citando-o; quando o resumo dele não se lê, o comando SHALL avisar, citando-o e dizendo que se corrija ou mova o arquivo, sem juntá-lo nem renomeá-lo. O caminho cujo `.git` não se consegue conferir (sem permissão, por exemplo) MUST contar como um repositório, e o comando MUST terminar com o código de saída 0. Quando esse caminho ainda tem um repositório e não há resumo para o caminho da raiz, o comando SHALL só avisar, citando o outro resumo. O comando MUST NOT tomar por ele o resumo de um repositório cujo nome só começa com o deste.

#### Scenario: Pasta trocada
- **WHEN** o comando já rodou com a raiz em `/a/proj`, `/a/proj` ainda tem um repositório, e ele roda agora com a raiz em `/b/proj`
- **THEN** a saída traz um aviso que cita o resumo de `/a/proj`
- **AND** o comando termina com o código de saída 0

#### Scenario: Pasta antiga que já não existe
- **WHEN** o comando já rodou com a raiz em `/a/proj`, com uma conversa já apagada guardada no resumo, e a pasta foi movida para `/b/proj`
- **THEN** a execução em `/b/proj` conta as horas dessa conversa, o resumo e a página de `/a/proj` ganham o sufixo `.juntado`, e a saída traz um aviso que cita o resumo

#### Scenario: Pasta antiga que sobrou sem o repositório
- **WHEN** a pasta foi movida de `/a/proj` para `/b/proj`, mas sobrou em `/a/proj` uma pasta sem repositório git
- **THEN** a execução em `/b/proj` junta o resumo de `/a/proj`, como no cenário anterior

#### Scenario: Segundo resumo juntado com o mesmo nome
- **WHEN** já existe o `.juntado` de um resumo, e outro resumo de mesmo nome é juntado
- **THEN** os dois arquivos juntados continuam na pasta dos dados

#### Scenario: Pasta antiga juntada depois da primeira execução
- **WHEN** o comando já rodou em `/b/proj` antes de `/a/proj` deixar de existir, e roda de novo depois
- **THEN** a execução conta as horas guardadas no resumo de `/a/proj`, e ele ganha o sufixo `.juntado`

#### Scenario: Resumo antigo que não se lê
- **WHEN** a pasta `/a/proj` já não existe, e o resumo dela é de uma versão que o comando não conhece
- **THEN** a saída traz um aviso que cita esse resumo e diz "corrija-o ou mova-o", o resumo continua com o nome de antes, e as horas dele não entram

#### Scenario: Pasta antiga com um .git que o git recusa
- **WHEN** a pasta `/a/proj` ainda tem um `.git`, mas o git não a abre
- **THEN** o resumo de `/a/proj` não é juntado nem renomeado

#### Scenario: Pasta antiga sem permissão
- **WHEN** a pasta acima de `/a/proj` não se abre, por falta de permissão
- **THEN** o comando termina com o código de saída 0, e o resumo de `/a/proj` não é juntado nem renomeado

#### Scenario: Vizinho de nome parecido
- **WHEN** a pasta dos dados tem só o resumo de um repositório `proj-antigo`, e o comando roda na raiz `proj`
- **THEN** a saída não traz o aviso
