## MODIFIED Requirements

### Requirement: Migração da pasta trilha para trilha-ai
Num projeto com a pasta `trilha/` do método (com o `trilha/CLAUDE-comum.md`), o `kit.py atualizar` SHALL tirá-la, criar a `trilha-ai/` do kit, trocar `trilha/` por `trilha-ai/` no `CLAUDE.md` (a importação e as citações) e no `scripts/check.sh` (a chamada do `verifica.sh`, com os argumentos), e ligar a trava do Claude Code e o `core.hooksPath` pela pasta nova. Uma pasta `trilha/` sem o comum MUST ficar como está.

#### Scenario: Projeto da versão 2.18 migrado
- **WHEN** o `kit.py atualizar` roda num projeto feito pelo kit na versão 2.18, com um `--vizinho` no `scripts/check.sh`
- **THEN** a pasta `trilha/` não existe mais, e a `trilha-ai/` é igual à `modelo/trilha-ai/` do kit
- **AND** o `CLAUDE.md` importa `@trilha-ai/CLAUDE-comum.md` e não cita mais `trilha/`, o `scripts/check.sh` chama `bash trilha-ai/verifica.sh` com o mesmo `--vizinho`, o `.claude/settings.json` liga só `trilha-ai/guarda.py`, uma vez, e o `core.hooksPath` é `trilha-ai/hooks`
- **AND** a conferência das regras e a do método passam, e a saída sugere o commit da cópia, com as duas versões
- **AND** a saída avisa para reabrir a sessão do Claude Code aberta no projeto, que ainda chama a trava antiga

#### Scenario: Arquivo a mais na pasta trilha do método
- **WHEN** a pasta `trilha/` do método tem um arquivo que o kit não tem
- **THEN** depois do `kit.py atualizar` a pasta `trilha/` não existe mais
- **AND** a saída traz um aviso que cita esse arquivo

#### Scenario: Pasta trilha que não é do método
- **WHEN** o projeto já está na `trilha-ai/` e tem uma pasta `trilha/` própria, sem o `trilha/CLAUDE-comum.md`
- **THEN** depois do `kit.py atualizar` a pasta `trilha/` continua lá, sem mudança

#### Scenario: Arquivo do projeto que ainda cita a pasta trilha
- **WHEN** um arquivo versionado do projeto fora da `trilha-ai/`, do `CLAUDE.md` e do `scripts/check.sh` (por exemplo, um `docs/` qualquer) cita `trilha/`
- **THEN** a saída do `kit.py atualizar` traz um aviso que cita esse arquivo, para a troca à mão
- **AND** o aviso não cita um arquivo em que `trilha/` só aparece dentro de outro nome ou caminho (`minhatrilha/`, `trilha-ai/`, `src/trilha/`, `../trilha/`), nem o `.claude/settings.json`, cuja trava já foi trocada
- **AND** o aviso traz inteiro o nome do arquivo com acento ou espaço (`docs/decisões técnicas.md`)
- **AND** o aviso também cita o arquivo que chama a pasta depois de uma variável do shell (`"$RAIZ/trilha/hooks"`) ou pelo nome entre aspas (`Path("trilha")`)

#### Scenario: Importação com espaço no fim
- **WHEN** o `CLAUDE.md` do projeto da 2.18 importa `@trilha/CLAUDE-comum.md` com um espaço no fim da linha
- **THEN** depois do `kit.py atualizar` a linha é `@trilha-ai/CLAUDE-comum.md`, e a conferência das regras passa

#### Scenario: Arquivo ignorado na pasta trilha do método
- **WHEN** a pasta `trilha/` do método tem um arquivo que o git ignora (por exemplo, `trilha/notas.log`)
- **THEN** o `kit.py atualizar` recusa, citando o arquivo, sem mudar nada no projeto

#### Scenario: Pasta trilha do método que é um link simbólico
- **WHEN** a `trilha/` do projeto é um link simbólico para uma pasta com o comum que não é a `trilha-ai/` do projeto
- **THEN** o `kit.py atualizar` recusa, com o motivo, sem mudar nada no projeto

#### Scenario: Caminho do projeto que cita trilha
- **WHEN** o `scripts/check.sh` do projeto da 2.18 também cita `src/trilha/` e `../trilha/x`
- **THEN** depois do `kit.py atualizar` essas citações continuam como estavam, e a chamada passa a `bash trilha-ai/verifica.sh`

#### Scenario: Versão de antes lida pelo nome novo
- **WHEN** o kit lê, na tag `v2.18`, o `trilha-ai/CLAUDE-comum.md`
- **THEN** ele acha o comum da 2.18, que naquela versão ficava em `modelo/trilha/`

## ADDED Requirements

### Requirement: Link de transição criado na migração
Quando a migração da `trilha/` do método termina e um arquivo versionado do projeto, fora da `trilha-ai/`, ainda cita `trilha/` (a mesma busca do aviso das citações), o `kit.py atualizar` SHALL criar no projeto o link simbólico `trilha` para `trilha-ai`, relativo, e dizer na saída que o criou, por quê e que ele sai quando nenhum arquivo citar mais `trilha/`. Sem citação, o link MUST NOT ser criado.

#### Scenario: Projeto que ainda cita a pasta antiga
- **WHEN** o `kit.py atualizar` migra um projeto da 2.18 com um `docs/como.md` que cita `trilha/tempo.py`
- **THEN** o projeto tem o link simbólico `trilha` que aponta para `trilha-ai`, e o `trilha/tempo.py` existe por ele
- **AND** a saída diz que criou o link de transição e cita o `docs/como.md`
- **AND** a conferência das regras e a do método passam, e o `git status` mostra o link entre o que mudou

#### Scenario: Projeto que não cita mais a pasta antiga
- **WHEN** o `kit.py atualizar` migra um projeto da 2.18 sem arquivo que cite `trilha/` fora do `CLAUDE.md` e do `scripts/check.sh`
- **THEN** o projeto não tem `trilha`, nem pasta nem link

### Requirement: Link de transição no atualizar seguinte
Num projeto que já está na `trilha-ai/` e tem o link simbólico `trilha` que aponta para a `trilha-ai/` dele, o `kit.py atualizar` SHALL tratá-lo como o link de transição: MUST NOT recusar nem migrar por ele; MUST tirá-lo, com aviso, quando a busca das citações não acha mais nenhuma, e mantê-lo, com aviso e a lista, quando ainda acha.

#### Scenario: Link que fica
- **WHEN** o `kit.py atualizar` roda de novo, depois do commit da migração, com o `docs/como.md` ainda citando `trilha/tempo.py`
- **THEN** ele termina com o código de saída 0, o link `trilha` continua apontando para `trilha-ai`
- **AND** a saída diz que o link de transição fica e cita o `docs/como.md`

#### Scenario: Link que sai
- **WHEN** o `kit.py atualizar` roda de novo depois que o projeto deixou de citar `trilha/`, com o commit
- **THEN** ele termina com o código de saída 0, e o projeto não tem mais `trilha`
- **AND** a saída diz que o link de transição saiu porque nenhum arquivo cita mais `trilha/`
