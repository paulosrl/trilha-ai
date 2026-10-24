# horas-de-trabalho Specification

## Purpose

Define o que o `trilha-ai/tempo.py` faz: apurar, sob demanda e sem nada rodar a cada interação, as horas de trabalho de cada dia num repositório, separando o tempo do usuário do tempo da IA sozinha, a partir das conversas do Claude Code e dos commits, e mostrá-las numa página fora do repositório.

## Requirements

### Requirement: Só sob demanda
O `trilha-ai/tempo.py` SHALL rodar só quando chamado, de dentro de um repositório git. O modelo do `.claude/settings.json` do kit MUST NOT ligar o `tempo.py` a nenhum gancho do Claude Code. Fora de um repositório git, o comando MUST terminar com código diferente de 0 e dizer por quê, sem escrever nada.

#### Scenario: Nenhum gancho no modelo
- **WHEN** o `modelo/claude-settings.json` do kit é lido
- **THEN** nenhum comando de gancho cita o `tempo.py`

#### Scenario: Fora de um repositório
- **WHEN** o comando roda numa pasta que não pertence a um repositório git
- **THEN** ele termina com código diferente de 0, com uma mensagem que diz que a pasta não é um repositório git
- **AND** nenhum arquivo é criado na pasta de dados do usuário

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

### Requirement: Pedido do usuário
O comando SHALL contar como pedido do usuário só a mensagem escrita por ele: uma linha de usuário que não é de metadados, nem de subagente, nem resumo de compactação, e cujo conteúdo não é só o resultado de uma ferramenta. As demais linhas com hora, do assistente e dos resultados de ferramentas, MUST contar como ação da IA.

#### Scenario: Resultado de ferramenta
- **WHEN** uma linha de usuário traz só o resultado de uma ferramenta
- **THEN** ela conta como ação da IA, não como pedido do usuário

#### Scenario: Mensagem de metadados
- **WHEN** uma linha de usuário é marcada como de metadados
- **THEN** ela não conta como pedido do usuário

### Requirement: Tempo do usuário e tempo da IA
Em cada conversa, o intervalo entre dois eventos seguidos do repositório SHALL contar como tempo ativo quando for de até 30 minutos, e MUST NOT contar quando for maior, nem quando os dois vêm do mesmo arquivo de conversa e esse arquivo tem, entre eles, um evento fora do repositório. A linha repetida em dois arquivos da conversa é um evento só, dos dois. O intervalo ativo que termina num pedido do usuário MUST contar como tempo do usuário; o que termina numa ação da IA, como tempo da IA.

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
- **WHEN** a conversa principal tem eventos no repositório às 09:00, 09:10 e 09:20, e um subagente dela, cujo arquivo também cita o repositório, tem eventos noutra pasta às 09:05 e 09:15
- **THEN** o dia tem 20 minutos de total

#### Scenario: Conversa retomada noutro arquivo
- **WHEN** as linhas da "Saída e volta no meio da conversa" estão copiadas em dois arquivos da mesma conversa
- **THEN** nenhum minuto dessa conversa entra no dia

### Requirement: Conversas em paralelo
O tempo em que duas ou mais conversas estavam ativas ao mesmo tempo SHALL contar uma vez só. O tempo do usuário MUST ser a união dos intervalos do usuário; o total, a união de todos; e o tempo da IA sozinha, o total menos o tempo do usuário.

#### Scenario: Duas conversas na mesma hora
- **WHEN** duas conversas têm, cada uma, a IA ativa das 10:00 às 11:00
- **THEN** o dia tem 1 hora de total, toda da IA sozinha

#### Scenario: Usuário numa conversa enquanto a IA trabalha na outra
- **WHEN** a IA está ativa numa conversa das 10:00 às 10:30 e o usuário está ativo noutra das 10:20 às 10:30
- **THEN** o dia tem 30 minutos de total, 10 do usuário e 20 da IA sozinha

### Requirement: Dias pelo relógio da máquina
As horas SHALL ser contadas no fuso horário local da máquina, e um intervalo que passa da meia-noite MUST ser dividido entre os dois dias pelo relógio.

#### Scenario: Intervalo na virada do dia
- **WHEN** a IA está ativa das 23:50 de um dia às 00:10 do dia seguinte, no fuso local
- **THEN** cada um dos dois dias recebe 10 minutos

#### Scenario: Dia da mudança de horário
- **WHEN** a IA está ativa das 23:00 às 23:20, pelo relógio local, no dia em que o horário de verão termina
- **THEN** a faixa do dia na página vai dos 1380 aos 1400 minutos, a posição pelo relógio

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

### Requirement: Fonte de cada dia
Cada dia apurado SHALL dizer a fonte das suas horas: "conversas", com o tempo do usuário e o da IA sozinha, ou "commits", só com o total estimado.

#### Scenario: Dia estimado pelos commits
- **WHEN** um dia tem horas só pelos commits
- **THEN** a fonte do dia é "commits" e ele não traz a divisão entre o usuário e a IA

### Requirement: Resumo fora do repositório
O comando SHALL guardar, na pasta `trilha-ai/tempo/` dos dados do usuário (`XDG_DATA_HOME`, ou `~/.local/share` quando ela falta ou é vazia), um resumo por repositório só com o caminho da raiz, identificadores de conversa, datas, horas e tipos de intervalo, e o caminho, o tamanho e a data dos arquivos de conversa lidos sem nada do repositório. O resumo MUST NOT conter texto das conversas, e o comando MUST NOT escrever nada dentro do repositório.

#### Scenario: Nenhum texto no resumo
- **WHEN** uma conversa tem um pedido com o texto "frase-que-nao-pode-vazar"
- **THEN** o resumo gravado não contém esse texto

#### Scenario: Repositório intocado
- **WHEN** o comando termina
- **THEN** o `git status --porcelain` do repositório é o mesmo de antes

#### Scenario: Pasta de dados trocada
- **WHEN** `XDG_DATA_HOME` aponta para outra pasta
- **THEN** o resumo e a página são gravados em `trilha-ai/tempo/` dentro dela

### Requirement: Horas que sobrevivem às conversas
A cada execução, o comando SHALL juntar ao resumo as horas das conversas que ainda existem, e MUST continuar contando as horas guardadas de uma conversa, ou de parte dela, cujo arquivo já foi apagado.

#### Scenario: Conversa apagada depois da primeira execução
- **WHEN** o comando roda, a conversa é apagada e o comando roda de novo
- **THEN** as horas de cada dia são as mesmas nas duas execuções

#### Scenario: Arquivo de subagente apagado
- **WHEN** um subagente preencheu 50 minutos de uma conversa, o arquivo dele é apagado depois da primeira execução e o da conversa principal continua
- **THEN** a segunda execução conta os mesmos minutos que a primeira

#### Scenario: Conversa que cresceu
- **WHEN** uma conversa ganha um pedido novo entre duas execuções
- **THEN** a segunda execução conta o intervalo novo uma vez só

### Requirement: Resumo ilegível preservado
Quando o resumo existe e não se lê (não é JSON, é de uma versão que o comando não conhece ou tem uma entrada fora do formato), o comando SHALL terminar com código diferente de 0, citando o arquivo, e MUST NOT sobrescrevê-lo nem gravar a página: ele é a única cópia das horas das conversas já apagadas.

#### Scenario: Resumo corrompido
- **WHEN** o resumo do repositório tem um texto que não é JSON
- **THEN** o comando termina com código diferente de 0, com uma mensagem que cita o resumo
- **AND** o resumo continua igual

#### Scenario: Entrada fora do formato
- **WHEN** uma conversa do resumo tem um intervalo com dois campos em vez de três
- **THEN** o comando termina com código diferente de 0, sem rastro de exceção, e o resumo continua igual

### Requirement: Leitura só do que mudou
O comando SHALL guardar no resumo o caminho, o tamanho e a data de modificação de cada arquivo de conversa lido que não tem nenhuma linha do repositório, e MUST NOT lê-lo de novo enquanto o tamanho e a data não mudarem. O arquivo com alguma linha do repositório MUST ser lido a cada execução.

#### Scenario: Arquivo de outro repositório sem mudança
- **WHEN** um arquivo de conversa sem nada do repositório é trocado, entre duas execuções, por um de mesmo tamanho e mesma data com uma conversa do repositório
- **THEN** a segunda execução não conta essa conversa

#### Scenario: Arquivo que mudou
- **WHEN** a data de modificação desse arquivo muda
- **THEN** a execução seguinte o lê e conta a conversa

### Requirement: Página das horas
O comando SHALL gerar uma página HTML na mesma pasta do resumo, com as horas de cada dia numa linha do tempo semana a semana, do primeiro ao último dia apurado, as horas somadas por dia da semana, a fonte de cada dia e o método da apuração, e MUST imprimir o caminho dela. A página MUST NOT carregar nada da rede.

#### Scenario: Caminho impresso
- **WHEN** o comando termina
- **THEN** a saída cita o caminho da página gerada, e o arquivo existe

#### Scenario: Nada da rede
- **WHEN** a página é gerada
- **THEN** ela não tem script, folha de estilo, fonte nem imagem com endereço `http://` ou `https://`

### Requirement: Aviso da guarda curta das conversas
O comando SHALL avisar, sem falhar, quando o `cleanupPeriodDays` do `settings.json` do usuário, na pasta de configuração do Claude Code, falta ou é menor que 365, e o aviso MUST citar a linha de configuração que resolve.

#### Scenario: Guarda padrão
- **WHEN** o `settings.json` do usuário não tem `cleanupPeriodDays`
- **THEN** a saída traz um aviso que cita `"cleanupPeriodDays": 3650`
- **AND** o comando termina com o código de saída 0

#### Scenario: Guarda curta definida
- **WHEN** o `settings.json` do usuário tem `"cleanupPeriodDays": 90`
- **THEN** o aviso cita os 90 dias e não fala em prazo padrão

#### Scenario: Guarda longa
- **WHEN** o `settings.json` do usuário tem `"cleanupPeriodDays": 3650`
- **THEN** a saída não traz o aviso da guarda

### Requirement: Linha de commit que não se entende
A linha do `git log` que o comando não entende SHALL ser ignorada, sem falhar, e a assinatura dos commits MUST NOT entrar na leitura, mesmo com `log.showSignature` ligado.

#### Scenario: Commit assinado com a assinatura na saída do git
- **WHEN** o repositório tem `log.showSignature` ligado e um commit assinado com uma chave ssh que o git não sabe conferir
- **THEN** o comando termina com o código de saída 0, e o dia do commit aparece

#### Scenario: Data em UTC com Z
- **WHEN** o `git log` traz a data de um commit como `2026-10-01T10:00:00Z`
- **THEN** o commit conta no dia 01/10/2026

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

### Requirement: Página com os dados uma vez
A página SHALL ter os dados da apuração só no bloco de dados, e o nome do repositório MUST entrar no título com os caracteres especiais de HTML protegidos.

#### Scenario: Dados uma vez
- **WHEN** a página é gerada
- **THEN** a lista dos dias aparece uma vez só no arquivo

#### Scenario: Nome com caracteres especiais
- **WHEN** a raiz se chama `a<b__DADOS__`
- **THEN** o título da página traz `a&lt;b__DADOS__`, e a lista dos dias continua aparecendo uma vez só

#### Scenario: Nome que abre um comentário
- **WHEN** a raiz se chama `x<!--<script`
- **THEN** o bloco de dados da página não traz o texto `<!--`

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
