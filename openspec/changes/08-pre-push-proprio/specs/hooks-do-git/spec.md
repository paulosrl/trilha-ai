# Spec Delta

## Purpose

Define o que os hooks do git da pasta `trilha/hooks`, ligada pelo `core.hooksPath`, rodam no projeto, para que a trava do método não desligue a verificação que o próprio projeto põe no envio.

## ADDED Requirements

### Requirement: Envio pelo hook próprio do projeto
A cada `git push`, o `trilha/hooks/pre-push` SHALL rodar o `.githooks/pre-push` do projeto quando ele existe, com os mesmos argumentos (o nome e o endereço do remoto) e a mesma entrada (as linhas das referências enviadas), e MUST terminar com o código de saída dele. Sem o `.githooks/pre-push`, o hook MUST sair com 0 e o envio segue.

#### Scenario: Hook próprio que aprova
- **WHEN** o projeto tem um `.githooks/pre-push` executável que sai com 0 e roda um `git push`
- **THEN** o envio chega ao remoto
- **AND** o hook próprio recebeu o nome e o endereço do remoto como argumentos e a linha da referência enviada na entrada

#### Scenario: Hook próprio que reprova
- **WHEN** o projeto tem um `.githooks/pre-push` executável que sai com 1 e roda um `git push`
- **THEN** o git recusa o envio, e o remoto fica sem o commit

#### Scenario: Projeto sem hook próprio
- **WHEN** o projeto não tem `.githooks/pre-push` e roda um `git push`
- **THEN** o envio chega ao remoto

### Requirement: Hook próprio sem permissão de execução
Quando o `.githooks/pre-push` existe sem a permissão de execução, o `trilha/hooks/pre-push` SHALL recusar o envio, citando o arquivo, e MUST NOT pulá-lo em silêncio, como o git faria com um hook dele.

#### Scenario: Hook próprio não executável
- **WHEN** o projeto tem um `.githooks/pre-push` sem a permissão de execução e roda um `git push`
- **THEN** o git recusa o envio
- **AND** a mensagem cita `.githooks/pre-push` e a permissão de execução
