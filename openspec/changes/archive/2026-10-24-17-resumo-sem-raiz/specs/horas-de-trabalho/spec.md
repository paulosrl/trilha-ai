## ADDED Requirements

### Requirement: Resumo de mesmo nome sem a raiz legível
Quando um resumo com o nome deste repositório e de outro caminho não diz de que pasta deste repositório veio (não é JSON, não é um objeto, não tem a raiz em texto, ou a raiz gravada não termina no nome deste repositório), o comando SHALL avisar em toda execução, citando-o e dizendo que, se ele for de uma pasta antiga deste repositório, as horas dele não vieram e que se corrija ou mova o arquivo; o comando MUST NOT falhar por isso nem mudar o arquivo.

#### Scenario: Resumo de mesmo nome que não é JSON
- **WHEN** a pasta dos dados tem um `proj-<8 dígitos hexadecimais>.json` de outro caminho cujo conteúdo não é JSON, e o comando roda na raiz `proj`
- **THEN** a saída traz um aviso que cita esse arquivo e diz "corrija-o ou mova-o"
- **AND** o comando termina com o código de saída 0, e o arquivo continua igual

#### Scenario: Resumo de mesmo nome sem a raiz
- **WHEN** o resumo de mesmo nome de outro caminho é JSON, mas é uma lista, um objeto sem a raiz, um objeto com a raiz que não é texto, um objeto com a raiz vazia, ou um aninhado fundo demais para o Python ler
- **THEN** a saída traz o mesmo aviso, citando o arquivo
- **AND** o comando termina com o código de saída 0

#### Scenario: Resumo de mesmo nome com a raiz de outro nome
- **WHEN** o resumo de mesmo nome de outro caminho grava a raiz `/a/outro`, e o comando roda na raiz `proj`
- **THEN** a saída traz o mesmo aviso, citando o arquivo

#### Scenario: Próprio resumo com a raiz que não é texto
- **WHEN** o resumo deste caminho se lê, mas grava a raiz como um número
- **THEN** a saída não traz o aviso

#### Scenario: Resumo de outro nome que não é JSON
- **WHEN** a pasta dos dados tem um `proj-antigo-<8 dígitos hexadecimais>.json` que não é JSON, e o comando roda na raiz `proj`
- **THEN** a saída não traz o aviso
