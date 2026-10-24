## MODIFIED Requirements

### Requirement: Envio pelo hook próprio do projeto
A cada `git push`, o `trilha-ai/hooks/pre-push` SHALL rodar o `.githooks/pre-push` do projeto quando ele existe, com os mesmos argumentos (o nome e o endereço do remoto) e a mesma entrada (as linhas das referências enviadas), e MUST terminar com o código de saída dele. Sem o `.githooks/pre-push`, o hook MUST sair com 0 e o envio segue.

#### Scenario: Hook próprio que aprova
- **WHEN** o projeto tem um `.githooks/pre-push` executável que sai com 0 e roda um `git push`
- **THEN** o envio chega ao remoto
- **AND** o hook próprio recebeu o nome e o endereço do remoto como argumentos e a linha da referência enviada na entrada

#### Scenario: Hook próprio que reprova
- **WHEN** o projeto tem um `.githooks/pre-push` executável que sai com 1 e roda um `git push`
- **THEN** o git recusa o envio, e o remoto fica sem o commit

#### Scenario: Código de saída e entrada repassados
- **WHEN** o `trilha-ai/hooks/pre-push` roda com dois argumentos e uma linha na entrada, e o `.githooks/pre-push` sai com 3
- **THEN** o `trilha-ai/hooks/pre-push` sai com 3
- **AND** o hook próprio recebeu os dois argumentos e a linha da entrada, sem mudança

#### Scenario: Projeto sem hook próprio
- **WHEN** o projeto não tem `.githooks/pre-push` e roda um `git push`
- **THEN** o envio chega ao remoto

### Requirement: Hook próprio que não pode rodar
Quando o `.githooks/pre-push` existe sem a permissão de execução, é um link simbólico quebrado ou leva de volta ao próprio `trilha-ai/hooks/pre-push` no mesmo repositório, o `trilha-ai/hooks/pre-push` SHALL recusar o envio, citando o arquivo, e MUST NOT deixar o envio seguir sem ele, como o git faz com um hook dele que não é executável (só avisa e segue), nem rodar sem fim.

#### Scenario: Hook próprio não executável
- **WHEN** o projeto tem um `.githooks/pre-push` sem a permissão de execução e roda um `git push`
- **THEN** o git recusa o envio
- **AND** a mensagem cita `.githooks/pre-push` e a permissão de execução

#### Scenario: Link simbólico quebrado
- **WHEN** o `.githooks/pre-push` do projeto é um link simbólico para um arquivo que não existe e o projeto roda um `git push`
- **THEN** o git recusa o envio
- **AND** a mensagem cita `.githooks/pre-push`

#### Scenario: Repasse que volta a si mesmo
- **WHEN** o `.githooks/pre-push` do projeto é um link simbólico para o `trilha-ai/hooks/pre-push` e o projeto roda um `git push`
- **THEN** o git recusa o envio, sem ficar rodando sem fim
- **AND** a mensagem cita `.githooks/pre-push`

