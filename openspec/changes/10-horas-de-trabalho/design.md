# Design

## Context

Ver `proposal.md` (Why). O que já existe e molda a abordagem:

- O `kit.py` copia toda a `modelo/trilha/` para os projetos (`SEM_MUDAR`, lido da pasta), e a conferência da pasta `trilha/` com `--fonte` compara arquivo a arquivo com a versão do projeto. Um arquivo novo na pasta não pede mudança em nenhum dos dois.
- O `trilha/gerar_pagina_sdd.py` já gera uma página a partir de um modelo HTML (`pagina_sdd_modelo.html`), trocando `__TITULO__` e `__DADOS__` por texto e por JSON seguro (`</` escapado). O comando novo segue o mesmo molde.
- As conversas do Claude Code ficam em `<configuração>/projects/<pasta>/<sessão>.jsonl`, e as dos subagentes em `<sessão>/subagents/*.jsonl`. Medido nesta máquina em 2026-10-20: 1,3 GB em 492 arquivos. Cada linha útil traz `type`, `timestamp` (UTC), `sessionId` e `cwd`. As dos subagentes têm o mesmo `sessionId` da conversa e `isSidechain: true`. O pedido do usuário é a linha `user` sem `isMeta`, com conteúdo em texto; o resultado de ferramenta é a linha `user` cujo conteúdo é só `tool_result`.
- O kit é Python 3 puro, sem dependências; os testes, `unittest` em `testes/test_kit.py`.

## Goals / Non-Goals

**Goals:**
- Responder às mesmas perguntas da página avulsa (quando, quantas horas por dia e por dia da semana, quanto do usuário e quanto da IA), com custo zero no dia a dia.
- Ler 1 GB de conversas em poucos segundos, sem dependências.

**Non-Goals:**
- Opções de linha de comando nesta versão (período, formato, saída): o comando não tem nenhuma.
- Horas por pessoa: o comando apura a máquina onde roda, que é de um usuário só.
- Somar as horas de várias máquinas.

## Decisions

### D1. Um arquivo de código e um modelo de página
`modelo/trilha/tempo.py` faz a leitura, a apuração, o resumo e a página; `modelo/trilha/pagina_tempo_modelo.html` tem o visual e o código da página, que desenha tudo a partir do JSON embutido, como o `pagina_sdd_modelo.html`. *Alternativa:* gerar o HTML todo no Python. Recusada porque mistura o visual com a apuração e foge do molde que o kit já tem.

### D2. O repositório e os nomes dos arquivos
A raiz vem de `git rev-parse --show-toplevel`, rodado na pasta atual. O resumo é `<nome da raiz>-<8 primeiros hexadecimais do SHA-1 do caminho absoluto>.json` e a página tem o mesmo nome, com `.html`, ambos em `<dados do usuário>/trilha-ai/tempo/`. O hash separa dois clones com o mesmo nome. *Alternativa:* usar o endereço do `origin`. Recusada porque as conversas se ligam ao repositório pelo `cwd`, que é um caminho, e um clone em outro caminho é outra apuração.

### D3. Leitura rápida das conversas
O comando percorre `<configuração>/projects/**/*.jsonl` e só decodifica a linha que contém o caminho da raiz como ele aparece no JSON (`json.dumps(raiz)[1:-1]`). Depois confere de verdade: `cwd == raiz` ou `cwd` começa com `raiz + "/"`, o que separa `xavier` de `xavier-antigo`. Linha que não é JSON válido ou que não tem `timestamp` é ignorada. *Alternativa:* ler só a pasta de `projects` com o nome do repositório. Recusada porque a sessão aberta noutra pasta e que trabalha no repositório ficaria de fora, e o nome da pasta é um detalhe interno do Claude Code.

### D4. Eventos e intervalos de cada conversa
Os eventos de uma conversa (`sessionId`) são as linhas `user` e `assistant` com hora, das conversas principal e dos subagentes, em ordem de hora. O evento é "pedido" quando a linha é `user`, sem `isMeta`, sem `isSidechain`, sem `isCompactSummary`, e com conteúdo que não é só `tool_result`; os demais são "IA". Entre dois eventos seguidos com até 30 minutos de distância nasce um intervalo, do tipo "usuario" se o segundo evento é um pedido, e "ia" se não é. As linhas `attachment`, `system` e as de controle não são eventos. *Alternativa:* contar do pedido até o fim da resposta inteira, como na descrição. Recusada porque uma resposta parada horas à espera de uma permissão contaria horas de IA; o corte de 30 minutos entre eventos resolve isso e mede o mesmo nos casos normais.

### D5. União por dia
Os intervalos de todas as conversas viram pares de segundos desde a época e são cortados na meia-noite local. Por dia: o total é o tamanho da união de todos; o tempo do usuário, o da união dos intervalos "usuario"; e o da IA sozinha, a diferença. *Alternativa:* somar os intervalos sem unir. Recusada porque duas conversas em paralelo dobrariam as horas.

### D6. O resumo
JSON com `versao: 1`, a `raiz` e `conversas`, um mapa de `sessionId` para a lista de intervalos `[início, fim, tipo]`, com início e fim em ISO 8601 UTC. A cada execução, a conversa que ainda tem arquivo é recalculada por inteiro e substitui a guardada; a que não tem mais arquivo fica como estava. Assim o intervalo novo de uma conversa que cresceu entra uma vez só, e a conversa apagada continua contando. O arquivo é gravado num temporário da mesma pasta e renomeado, para que uma queda no meio não o corrompa. *Alternativa:* guardar os eventos crus. Recusada porque o intervalo é menor e é o que a apuração usa.

### D7. Os commits
`git log --branches --remotes --tags --format=%H %aI`, cada hash uma vez, pela data de autor, convertida ao fuso local. *Alternativa:* `--all`. Recusada porque inclui o `stash`, que não é trabalho entregue. As sessões seguem o método da página avulsa: até 2 horas entre commits, 30 minutos antes do primeiro e corte na meia-noite. Os commits só valem nos dias em que as conversas não deram tempo nenhum.

### D8. A página
O Python monta os dados: um registro por dia com a data, a fonte, o total, o tempo do usuário e o da IA sozinha (só na fonte "conversas") e os intervalos do dia em minutos desde a meia-noite; mais os totais e as datas de início e fim. O modelo desenha:
- a linha do tempo semana a semana, com segunda a domingo nas linhas e um quadrado por dia, preenchido conforme as horas numa escala fixa de 0 a 20 h;
- as horas somadas por dia da semana;
- a fita hora a hora de cada dia;
- a fonte de cada dia e o método.

A página só usa fontes do sistema e nenhum endereço externo, e segue o tema claro ou escuro do sistema. *Alternativa:* fontes do Google, como na página avulsa. Recusadas porque carregar da rede contraria o requisito e a página pode ser aberta sem conexão.

### D9. A configuração e o aviso
A pasta de configuração é `CLAUDE_CONFIG_DIR`, ou `~/.claude` quando ela falta ou é vazia; a de dados, `XDG_DATA_HOME`, ou `~/.local/share` nas mesmas condições (a regra de tratar vazio como ausente vale também aqui). O aviso da guarda lê `cleanupPeriodDays` de `<configuração>/settings.json`: ausente, não numérico ou menor que 365 dá o aviso; um `settings.json` que não existe ou não é JSON válido também. O aviso vai para a saída de erro e o código de saída continua 0.

### D10. A saída
Três linhas, no máximo: o período e o total (`26/05/2026 a 20/10/2026: 57 dias, 201 h`), o caminho da página e, quando couber, o aviso da guarda.

## Risks / Trade-offs

- [O formato das conversas é interno do Claude Code e pode mudar] → Os testes fixam o formato lido hoje com conversas de exemplo. Uma linha que não se entende é ignorada, e o dia sem conversa entendida cai na estimativa pelos commits, com a fonte "commits" na página: a falha aparece, não quebra.
- [1 GB de conversas a cada execução] → O filtro pelo texto do caminho antes de decodificar o JSON deixa só as linhas do repositório. O comando roda sob demanda, não a cada interação.
- [A IA trabalhando sozinha por mais de 30 minutos sem nenhum evento (um comando longo) não conta] → Aceito: o corte é o mesmo para os dois tipos e evita contar espera como trabalho. Fica escrito no método da página.
- [O tempo que antecede o primeiro pedido de uma sessão (leitura, preparação) não conta] → Aceito e escrito no método. O mesmo acontece com a estimativa pelos commits, que compensa com os 30 minutos antes.
- [O resumo fica numa máquina só] → Aceito, e está fora do escopo. O backup da pasta pessoal o leva junto.

## Migration Plan

Nada a migrar. Os projetos recebem o comando com a cópia da 2.8, sob ordem do usuário. A primeira execução cria a pasta de dados e o resumo. Para desfazer, basta apagar `~/.local/share/trilha-ai/tempo/`; nada no repositório depende dela.

## Notas do apply

- Os 25 testes dos grupos 2 a 4 foram escritos juntos, antes de qualquer linha do `tempo.py` e da página. Rodados antes do código, 24 falharam; o `test_tempo_sem_gancho_no_modelo` passou, como a tarefa 2.1 previa. A ordem das tarefas por grupo ficou para o código, não para os testes: escrever o código de um grupo sem o do outro seria artificial, porque a apuração por dia e o resumo saem do mesmo caminho.
- O ruff pediu três trocas no `tempo.py`: `datetime.UTC`, `itertools.pairwise` e o `fromisoformat` sem trocar o `Z`. Só o `pairwise` foi aceito como veio. As outras duas pedem o Python 3.11, e o Ubuntu 22.04, comum no WSL, traz o 3.10. Por isso o `UTC` é uma constante própria (`timezone(timedelta(0))`) e o `Z` é trocado por fatia. O ruff passa sem nenhum `noqa`.
- O conjunto do kit só passou depois do `git add` dos dois arquivos novos de `modelo/trilha/`, porque o `kit.py` lista a pasta pelo índice do git (`git ls-files`). Sem isso, o projeto de teste nasce sem eles, e a conferência da pasta `trilha/` reprova.
- O resumo do Xavier saiu com 2,7 MB na primeira execução: um intervalo por par de eventos, gravado com recuo. Ele passou a ser gravado compacto, e os intervalos seguidos do mesmo tipo da mesma conversa se juntam num só. Isso não muda nenhuma soma e levou o resumo a 104 KB, com as mesmas 178 h.

## Execução manual (tarefa 6.2), em 2026-10-20

- Comando: `python3 -I ../trilha-ai/modelo/trilha/tempo.py`, dentro do Xavier, com a guarda das conversas da máquina já em 3650 dias. Resultado: `26/05/2026 a 20/10/2026: 59 dias, 178 h` e o caminho da página, em 4 segundos, sobre 1,3 GB de conversas, sem o aviso da guarda e com o código de saída 0.
- O `git status --porcelain` do Xavier foi o mesmo antes e depois.
- Na página, 26/05/2026 é o primeiro dia. 18 dias vêm das conversas, com a divisão entre o usuário e a IA (33% do usuário), e 41 são estimados pelos commits.
- Capturas de tela, sem arquivo versionado:
  - 1200 px no tema claro e 400 px no tema escuro, sem rolagem lateral, sem erro no console e sem nenhuma requisição fora do arquivo local;
  - as quatro seções da decisão D8 desenhadas, com a legenda das três fontes, e a tabela recolhida.
