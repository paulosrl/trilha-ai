# Spec Delta

## MODIFIED Requirements

### Requirement: Estimativa pelos commits nos dias sem conversa
O dia sem nenhum tempo ativo apurado das conversas SHALL ter as horas estimadas pelos commits do usuário (todas as branches e tags, cada commit uma vez, pela data de autor; com o e-mail de autor do git, que é o `GIT_AUTHOR_EMAIL`, o `author.email` ou o `user.email` de qualquer configuração do git, ou o `EMAIL` quando nenhum deles existe, só os commits dos e-mails do usuário): commits com até 2 horas de intervalo formam uma sessão, que começa 30 minutos antes do primeiro, sem passar da meia-noite do dia dele, e o dia com commit tem pelo menos 1 minuto. O dia com tempo das conversas MUST usar só as conversas.

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

### Requirement: Outros e-mails do usuário
Os e-mails gravados em `trilha.email` no git do repositório SHALL contar como do usuário na estimativa pelos commits, ao lado dos e-mails de autor do git. Quando algum commit fica fora por causa do e-mail, o comando MUST avisar, sem falhar, até três dos e-mails que ficaram fora, sem os de robôs (com `[bot]`) e sem os gravados em `trilha.outro`, com o comando que inclui um deles (`trilha.email`) e o que o tira do aviso (`trilha.outro`).

#### Scenario: E-mail a mais
- **WHEN** o `user.email` é `eu@exemplo.br`, o `trilha.email` tem `t@t`, e um dia sem conversa só tem um commit de `t@t`
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: Aviso dos e-mails de fora
- **WHEN** o `user.email` é `eu@exemplo.br`, e um commit de `t@t` fica fora da estimativa
- **THEN** a saída traz um aviso que cita `t@t` e os comandos `git config --add trilha.email` e `git config --add trilha.outro`
- **AND** o comando termina com o código de saída 0

#### Scenario: Robô fora do aviso
- **WHEN** o único commit que fica fora é do e-mail do Dependabot, com `[bot]`
- **THEN** a saída não traz o aviso dos e-mails

#### Scenario: Colega fora do aviso
- **WHEN** o `user.email` é `eu@exemplo.br`, o `trilha.outro` tem `colega@x`, e o único commit que fica fora é de `colega@x`
- **THEN** a saída não traz o aviso dos e-mails, e o commit continua fora da estimativa

### Requirement: Repositório que mudou de pasta
Quando há outro resumo do mesmo nome de repositório com outro caminho de raiz, e esse caminho já não tem um repositório git (a pasta `.git`), o comando SHALL juntar as conversas dele às deste resumo, renomear o arquivo dele e a página dele com o sufixo `.juntado`, sem apagá-los nem sobrescrever um `.juntado` anterior, e avisar, sem falhar, citando-o; quando o resumo dele não se lê, o comando SHALL avisar, citando-o, sem juntá-lo nem renomeá-lo. Quando esse caminho ainda tem um repositório e não há resumo para o caminho da raiz, o comando SHALL só avisar, citando o outro resumo. O comando MUST NOT tomar por ele o resumo de um repositório cujo nome só começa com o deste.

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
- **THEN** a saída traz um aviso que cita esse resumo, que continua com o nome de antes, e as horas dele não entram

#### Scenario: Pasta antiga com um .git que o git recusa
- **WHEN** a pasta `/a/proj` ainda tem um `.git`, mas o git não a abre
- **THEN** o resumo de `/a/proj` não é juntado nem renomeado

#### Scenario: Vizinho de nome parecido
- **WHEN** a pasta dos dados tem só o resumo de um repositório `proj-antigo`, e o comando roda na raiz `proj`
- **THEN** a saída não traz o aviso

### Requirement: Resumo da versão anterior
O resumo da versão 1, gravado pela 2.8, SHALL ser lido: as conversas que ainda existem MUST ser recalculadas por inteiro, sem juntar as horas que a 2.8 guardou delas, inclusive a que só tem linhas fora da raiz ou num repositório aninhado, e as já apagadas ficam como estavam. O resumo passa a ser gravado na versão 2.

#### Scenario: Horas a mais da 2.8
- **WHEN** o resumo da versão 1 guarda, para uma conversa que ainda existe, 28 minutos que a 2.9 não conta
- **THEN** o dia dela não traz esses minutos, e o resumo gravado é da versão 2

#### Scenario: Conversa já apagada no resumo antigo
- **WHEN** o resumo da versão 1 guarda uma conversa cujo arquivo já foi apagado
- **THEN** as horas dela continuam no dia

#### Scenario: Conversa do repositório aninhado no resumo antigo
- **WHEN** o resumo da versão 1 guarda 20 minutos de uma conversa que ainda existe e tem todas as linhas com `cwd` num repositório git aninhado na raiz
- **THEN** o dia dela não traz esses minutos, e o resumo gravado não traz essa conversa
