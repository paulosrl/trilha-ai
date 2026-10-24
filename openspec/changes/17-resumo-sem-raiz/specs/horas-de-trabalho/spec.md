## ADDED Requirements

### Requirement: Resumo de mesmo nome sem a raiz legível
Quando um resumo com o nome deste repositório e de outro caminho não deixa ler a raiz gravada (não é JSON, não é um objeto, ou não tem a raiz em texto), o comando SHALL avisar em toda execução, citando-o e dizendo que, se ele for de uma pasta antiga deste repositório, as horas dele não vieram e que se corrija ou mova o arquivo; o comando MUST NOT falhar por isso nem mudar o arquivo.

#### Scenario: Resumo de mesmo nome que não é JSON
- **WHEN** a pasta dos dados tem um `proj-<8 dígitos hexadecimais>.json` de outro caminho cujo conteúdo não é JSON, e o comando roda na raiz `proj`
- **THEN** a saída traz um aviso que cita esse arquivo e diz "corrija-o ou mova-o"
- **AND** o comando termina com o código de saída 0, e o arquivo continua igual

#### Scenario: Resumo de mesmo nome sem a raiz
- **WHEN** o resumo de mesmo nome de outro caminho é JSON, mas é uma lista, ou um objeto sem a raiz em texto
- **THEN** a saída traz o mesmo aviso, citando o arquivo

#### Scenario: Resumo de outro nome que não é JSON
- **WHEN** a pasta dos dados tem um `proj-antigo-<8 dígitos hexadecimais>.json` que não é JSON, e o comando roda na raiz `proj`
- **THEN** a saída não traz o aviso
