# Spec Delta

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

### Requirement: Tempo do usuário e tempo da IA
Em cada conversa, o intervalo entre dois eventos seguidos do repositório SHALL contar como tempo ativo quando for de até 30 minutos, e MUST NOT contar quando for maior, nem quando os dois vêm do mesmo arquivo de conversa e esse arquivo tem, entre eles, um evento fora do repositório. O intervalo ativo que termina num pedido do usuário MUST contar como tempo do usuário; o que termina numa ação da IA, como tempo da IA.

#### Scenario: Dois pedidos e duas respostas
- **WHEN** uma conversa tem um pedido às 09:00, a última ação da IA às 09:05, um pedido às 09:12 e a última ação da IA às 09:31
- **THEN** o dia tem 31 minutos de total, 7 do usuário e 24 da IA sozinha

#### Scenario: Pausa longa
- **WHEN** uma conversa tem um pedido às 09:00, a última ação da IA às 09:05 e o pedido seguinte às 10:00
- **THEN** o intervalo das 09:05 às 10:00 não conta, e o dia tem 5 minutos de total

#### Scenario: Atividade de segundos
- **WHEN** a única conversa de um dia tem dois eventos com 2 segundos de distância, e o dia tem um commit
- **THEN** o dia conta como sem tempo apurado das conversas, e as horas dele vêm do commit

#### Scenario: Saída e volta no meio da conversa
- **WHEN** uma conversa tem um pedido às 09:00 no repositório, ações da IA às 09:05 e às 09:20 noutra pasta e uma ação da IA às 09:28 de novo no repositório
- **THEN** nenhum minuto dessa conversa entra no dia

#### Scenario: Subagente noutra pasta
- **WHEN** a conversa principal tem eventos no repositório às 09:00, 09:10 e 09:20, e um subagente dela tem eventos noutra pasta às 09:05 e 09:15
- **THEN** o dia tem 20 minutos de total

### Requirement: Estimativa pelos commits nos dias sem conversa
O dia sem nenhum tempo ativo apurado das conversas SHALL ter as horas estimadas pelos commits do usuário (todas as branches e tags, cada commit uma vez, pela data de autor; com o `user.email` do git, só os desse e-mail de autor): commits com até 2 horas de intervalo formam uma sessão, que começa 30 minutos antes do primeiro, sem passar da meia-noite do dia dele, e o dia com commit tem pelo menos 1 minuto. O dia com tempo das conversas MUST usar só as conversas.

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
- **WHEN** o repositório não tem `user.email`, e um dia sem conversa tem um commit de qualquer autor
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: Commit à meia-noite em ponto
- **WHEN** um dia sem conversa tem um commit às 23:30 do dia anterior e outro às 00:00:00
- **THEN** o dia do segundo aparece, com 1 minuto estimado

## ADDED Requirements

### Requirement: Linha de commit que não se entende
A linha do `git log` que o comando não entende SHALL ser ignorada, sem falhar, e a assinatura dos commits MUST NOT entrar na leitura, mesmo com `log.showSignature` ligado.

#### Scenario: Commit assinado com a assinatura na saída do git
- **WHEN** o repositório tem `log.showSignature` ligado e um commit assinado com uma chave ssh que o git não sabe conferir
- **THEN** o comando termina com o código de saída 0, e o dia do commit aparece

#### Scenario: Data em UTC com Z
- **WHEN** o `git log` traz a data de um commit como `2026-10-01T10:00:00Z`
- **THEN** o commit conta no dia 01/10/2026

### Requirement: Outros e-mails do usuário
Os e-mails gravados em `trilha.email` no git do repositório SHALL contar como do usuário na estimativa pelos commits, ao lado do `user.email`. Quando algum commit fica fora por causa do e-mail, o comando MUST avisar, sem falhar, quais e-mails ficaram fora, com o comando que inclui um deles.

#### Scenario: E-mail a mais
- **WHEN** o `user.email` é `eu@exemplo.br`, o `trilha.email` tem `t@t`, e um dia sem conversa só tem um commit de `t@t`
- **THEN** o dia aparece, estimado pelos commits

#### Scenario: Aviso dos e-mails de fora
- **WHEN** o `user.email` é `eu@exemplo.br`, e um commit de `t@t` fica fora da estimativa
- **THEN** a saída traz um aviso que cita `t@t` e o comando `git config --add trilha.email`
- **AND** o comando termina com o código de saída 0

### Requirement: Página com os dados uma vez
A página SHALL ter os dados da apuração só no bloco de dados, e o nome do repositório MUST entrar no título com os caracteres especiais de HTML protegidos.

#### Scenario: Dados uma vez
- **WHEN** a página é gerada
- **THEN** a lista dos dias aparece uma vez só no arquivo

#### Scenario: Nome com caracteres especiais
- **WHEN** a raiz se chama `a<b__DADOS__`
- **THEN** o título da página traz `a&lt;b__DADOS__`, e a lista dos dias continua aparecendo uma vez só

### Requirement: Repositório que mudou de pasta
Quando não há resumo para o caminho da raiz, mas há outro resumo do mesmo nome de repositório com outro caminho, o comando SHALL avisar, sem falhar, citando esse resumo, e MUST NOT tomar por ele o resumo de um repositório cujo nome só começa com o deste.

#### Scenario: Pasta trocada
- **WHEN** o comando já rodou com a raiz em `/a/proj`, e roda agora com ela em `/b/proj`
- **THEN** a saída traz um aviso que cita o resumo de `/a/proj`
- **AND** o comando termina com o código de saída 0

#### Scenario: Vizinho de nome parecido
- **WHEN** a pasta dos dados tem só o resumo de um repositório `proj-antigo`, e o comando roda na raiz `proj`
- **THEN** a saída não traz o aviso
