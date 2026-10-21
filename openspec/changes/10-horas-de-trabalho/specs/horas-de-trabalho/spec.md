# Spec Delta

## Purpose

Define o que o `trilha/tempo.py` faz: apurar, sob demanda e sem nada rodar a cada interação, as horas de trabalho de cada dia num repositório, separando o tempo do usuário do tempo da IA sozinha, a partir das conversas do Claude Code e dos commits, e mostrá-las numa página fora do repositório.

## ADDED Requirements

### Requirement: Só sob demanda
O `trilha/tempo.py` SHALL rodar só quando chamado, de dentro de um repositório git. O modelo do `.claude/settings.json` do kit MUST NOT ligar o `tempo.py` a nenhum gancho do Claude Code. Fora de um repositório git, o comando MUST terminar com código diferente de 0 e dizer por quê, sem escrever nada.

#### Scenario: Nenhum gancho no modelo
- **WHEN** o `modelo/claude-settings.json` do kit é lido
- **THEN** nenhum comando de gancho cita o `tempo.py`

#### Scenario: Fora de um repositório
- **WHEN** o comando roda numa pasta que não pertence a um repositório git
- **THEN** ele termina com código diferente de 0, com uma mensagem que diz que a pasta não é um repositório git
- **AND** nenhum arquivo é criado na pasta de dados do usuário

### Requirement: Conversas do repositório
O comando SHALL ler as conversas do Claude Code da pasta `projects` da configuração do Claude Code (`CLAUDE_CONFIG_DIR`, ou `~/.claude` quando ela falta ou é vazia), inclusive as dos subagentes, e MUST considerar só as linhas cujo `cwd` é a raiz do repositório ou uma pasta dentro dela.

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

### Requirement: Pedido do usuário
O comando SHALL contar como pedido do usuário só a mensagem escrita por ele: uma linha de usuário que não é de metadados, nem de subagente, nem resumo de compactação, e cujo conteúdo não é só o resultado de uma ferramenta. As demais linhas com hora, do assistente e dos resultados de ferramentas, MUST contar como ação da IA.

#### Scenario: Resultado de ferramenta
- **WHEN** uma linha de usuário traz só o resultado de uma ferramenta
- **THEN** ela conta como ação da IA, não como pedido do usuário

#### Scenario: Mensagem de metadados
- **WHEN** uma linha de usuário é marcada como de metadados
- **THEN** ela não conta como pedido do usuário

### Requirement: Tempo do usuário e tempo da IA
Em cada conversa, o intervalo entre dois eventos seguidos SHALL contar como tempo ativo quando for de até 30 minutos, e MUST NOT contar quando for maior. O intervalo ativo que termina num pedido do usuário MUST contar como tempo do usuário; o que termina numa ação da IA, como tempo da IA.

#### Scenario: Dois pedidos e duas respostas
- **WHEN** uma conversa tem um pedido às 09:00, a última ação da IA às 09:05, um pedido às 09:12 e a última ação da IA às 09:31
- **THEN** o dia tem 31 minutos de total, 7 do usuário e 24 da IA sozinha

#### Scenario: Pausa longa
- **WHEN** uma conversa tem um pedido às 09:00, a última ação da IA às 09:05 e o pedido seguinte às 10:00
- **THEN** o intervalo das 09:05 às 10:00 não conta, e o dia tem 5 minutos de total

#### Scenario: Atividade de segundos
- **WHEN** a única conversa de um dia tem dois eventos com 2 segundos de distância, e o dia tem um commit
- **THEN** o dia conta como sem tempo apurado das conversas, e as horas dele vêm do commit

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
O dia sem nenhum tempo ativo apurado das conversas SHALL ter as horas estimadas pelos commits do repositório (todas as branches e tags, cada commit uma vez, pela data de autor): commits com até 2 horas de intervalo formam uma sessão, e cada sessão começa 30 minutos antes do primeiro commit, sem passar da meia-noite do dia dele. O dia com tempo apurado das conversas MUST usar só as conversas.

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
Quando o resumo existe e não se lê (não é JSON, é de outra versão ou tem uma entrada fora do formato), o comando SHALL terminar com código diferente de 0, citando o arquivo, e MUST NOT sobrescrevê-lo nem gravar a página: ele é a única cópia das horas das conversas já apagadas.

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
