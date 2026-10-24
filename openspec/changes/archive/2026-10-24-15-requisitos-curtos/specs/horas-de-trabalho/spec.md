## MODIFIED Requirements

### Requirement: Conversas do repositório
O comando SHALL ler as conversas do Claude Code da pasta `projects` da configuração do Claude Code (`CLAUDE_CONFIG_DIR`, ou `~/.claude` quando ela falta ou é vazia), inclusive as dos subagentes, e MUST considerar só as linhas cujo `cwd` é a raiz do repositório ou uma pasta dentro dela que não é de outro repositório git aninhado. Um worktree do próprio repositório dentro da raiz conta como dela.

#### Scenario: Conversa de outro repositório
- **WHEN** uma conversa tem todas as linhas com `cwd` num repositório vizinho cujo nome começa com o nome deste
- **THEN** nenhuma hora dela entra na apuração deste repositório

#### Scenario: Conversa numa subpasta
- **WHEN** uma conversa tem `cwd` numa subpasta do repositório
- **THEN** as horas dela entram na apuração

#### Scenario: Caminho com acento
- **WHEN** a raiz do repositório tem acento no nome (`projeto-ação`) e a conversa foi gravada com os acentos como são
- **THEN** as horas dela entram na apuração

#### Scenario: Pasta de configuração trocada
- **WHEN** `CLAUDE_CONFIG_DIR` aponta para outra pasta, com as conversas dentro dela
- **THEN** o comando lê as conversas dessa pasta

#### Scenario: Clone dentro da raiz
- **WHEN** a raiz tem uma pasta `vendor/lib` que é um repositório git próprio, e uma conversa tem `cwd` nela
- **THEN** as horas dessa conversa não entram na apuração da raiz

#### Scenario: Worktree do próprio repositório dentro da raiz
- **WHEN** a raiz tem um worktree dela mesma em `.claude/worktrees/w1`, e uma conversa tem `cwd` nele
- **THEN** as horas dessa conversa entram na apuração da raiz

#### Scenario: Subpasta sem permissão
- **WHEN** uma conversa tem `cwd` em `fechada/sub`, dentro da raiz, e a pasta `fechada` não se abre, por falta de permissão
- **THEN** o comando termina com o código de saída 0, e as horas dessa conversa entram na apuração da raiz

### Requirement: Estimativa pelos commits nos dias sem conversa
O dia sem nenhum tempo ativo apurado das conversas SHALL ter as horas estimadas pelos commits do usuário (as branches, as remotas e as tags, cada commit uma vez, pela data de autor): commits com até 2 horas de intervalo formam uma sessão, que começa 30 minutos antes do primeiro, sem passar da meia-noite do dia dele, e o dia com commit tem pelo menos 1 minuto. O dia com tempo das conversas MUST usar só as conversas.

#### Scenario: Sessões de commits
- **WHEN** um dia sem conversa tem commits às 10:00, 11:00 e 14:00
- **THEN** o dia tem 2 horas estimadas: das 09:30 às 11:00 e das 13:30 às 14:00

#### Scenario: Commit logo depois da meia-noite
- **WHEN** o único commit de um dia sem conversa é às 00:10
- **THEN** o dia tem 10 minutos estimados, e o dia anterior não ganha horas

#### Scenario: Dia com conversa e commits
- **WHEN** um dia tem tempo apurado das conversas e também commits
- **THEN** as horas do dia são só as das conversas, e a fonte do dia é "conversas"

#### Scenario: Commit em duas branches
- **WHEN** o mesmo commit está em duas branches
- **THEN** ele conta uma vez só

#### Scenario: Commit de outro autor
- **WHEN** o `user.email` é o do usuário, e um dia sem conversa só tem um commit com o e-mail do Dependabot
- **THEN** esse dia não aparece na apuração

#### Scenario: Sem e-mail configurado
- **WHEN** o git não tem `user.email` nem `author.email`, o `GIT_AUTHOR_EMAIL` e o `EMAIL` não estão definidos, e um dia sem conversa tem um commit de qualquer autor
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: Commit à meia-noite em ponto
- **WHEN** um dia sem conversa tem um commit às 23:30 do dia anterior e outro às 00:00:00
- **THEN** o dia do segundo aparece, com 1 minuto estimado

#### Scenario: E-mail de autor do git
- **WHEN** o `user.email` é `eu@exemplo.br`, o `author.email` é `autor@exemplo.br`, e um dia sem conversa só tem um commit de `autor@exemplo.br`
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: E-mail de autor no ambiente
- **WHEN** o `user.email` é `eu@exemplo.br`, o comando roda com `GIT_AUTHOR_EMAIL=amb@exemplo.br`, e um dia sem conversa só tem um commit de `amb@exemplo.br`
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: E-mail da configuração global
- **WHEN** o `user.email` do repositório é `eu@exemplo.br`, o da configuração global é `velho@exemplo.br`, e um dia sem conversa só tem um commit de `velho@exemplo.br`
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: Variável EMAIL
- **WHEN** o git não tem e-mail configurado, o comando roda com `EMAIL=var@exemplo.br`, e há um commit de `var@exemplo.br` num dia e um de `outro@exemplo.br` noutro
- **THEN** só o dia do commit de `var@exemplo.br` aparece

### Requirement: Repositório que mudou de pasta
Quando há outro resumo do mesmo nome de repositório com outro caminho de raiz, e esse caminho já não tem a pasta `.git`, o comando SHALL juntar as conversas dele às deste resumo, renomear o arquivo dele e a página dele com o sufixo `.juntado`, sem apagá-los nem sobrescrever um `.juntado` anterior, e avisar, sem falhar, citando-o, salvo quando o resumo dele não se lê ("Resumo antigo ilegível"). O comando MUST NOT tomar por ele o resumo de um repositório cujo nome só começa com o deste.

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
- **THEN** o comando termina com o código de saída 0, o resumo de `/a/proj` não é juntado nem renomeado, e a saída de cada execução traz um aviso de que não deu para conferir `/a/proj`, citando o resumo

#### Scenario: Raiz antiga com caminho inválido
- **WHEN** o resumo de mesmo nome tem gravada uma raiz com um caractere nulo no caminho
- **THEN** o comando termina com o código de saída 0, com o aviso de que não deu para conferir, e o resumo não é juntado nem renomeado

#### Scenario: Vizinho de nome parecido
- **WHEN** a pasta dos dados tem só o resumo de um repositório `proj-antigo`, e o comando roda na raiz `proj`
- **THEN** a saída não traz o aviso

## ADDED Requirements

### Requirement: Subpasta que não se confere
A subpasta da raiz cujo `.git` não se consegue conferir (sem permissão) MUST contar como da raiz na apuração das conversas, sem o comando falhar.

#### Scenario: Conversa sob uma pasta fechada
- **WHEN** uma conversa tem `cwd` numa subpasta da raiz que fica sob uma pasta sem permissão de leitura
- **THEN** o comando termina com o código de saída 0, e as horas dessa conversa entram na apuração da raiz

### Requirement: Commits do usuário
Os commits do usuário, na estimativa pelos commits, SHALL ser os dos e-mails de autor do git (o `GIT_AUTHOR_EMAIL`, o `author.email` e o `user.email` de qualquer configuração do git, ou o `EMAIL` quando nenhum deles existe) e os do `trilha.email` ("Outros e-mails do usuário"). Sem nenhum e-mail de autor, MUST contar os commits de qualquer autor, mesmo com o `trilha.email`.

#### Scenario: Só os commits dos e-mails do usuário
- **WHEN** o `user.email` é o do usuário, e um dia sem conversa só tem um commit de outro e-mail
- **THEN** esse dia não aparece na apuração

### Requirement: Resumo antigo ilegível
Quando o resumo de mesmo nome aponta uma raiz que já não tem repositório e não se lê (de uma versão que o comando não conhece, por exemplo), o comando SHALL avisar, citando-o e dizendo que se corrija ou mova o arquivo, sem juntá-lo nem renomeá-lo.

#### Scenario: Resumo antigo de versão desconhecida
- **WHEN** a raiz antiga já não existe, e o resumo dela é de uma versão que o comando não conhece
- **THEN** a saída traz um aviso que cita esse resumo e diz "corrija-o ou mova-o", o resumo continua com o nome de antes, e as horas dele não entram

### Requirement: Raiz antiga que não se confere
Quando não se consegue conferir o `.git` do caminho de raiz de outro resumo do mesmo nome (sem permissão, um caminho inválido), o comando MUST NOT juntar nem renomear o resumo dele, MUST avisar em toda execução que não conseguiu conferir, citando o resumo, e MUST terminar com o código de saída 0.

#### Scenario: Raiz antiga sob uma pasta fechada
- **WHEN** a pasta acima da raiz antiga não se abre, por falta de permissão
- **THEN** o comando termina com o código de saída 0, o resumo antigo não é juntado nem renomeado, e a saída de cada execução traz o aviso de que não deu para conferir, citando o resumo

### Requirement: Raiz antiga que ainda é repositório
Quando o caminho de raiz de outro resumo do mesmo nome ainda tem a pasta `.git`, mesmo que o git a recuse, e não há resumo para o caminho da raiz, o comando SHALL só avisar, citando o outro resumo.

#### Scenario: Repositório copiado para outra pasta
- **WHEN** o comando já rodou numa raiz que ainda tem o repositório, e roda agora noutra pasta com o mesmo nome
- **THEN** a saída traz um aviso que cita o resumo da outra raiz, e o comando termina com o código de saída 0
