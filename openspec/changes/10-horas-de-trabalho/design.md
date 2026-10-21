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
O comando percorre `<configuração>/projects/**/*.jsonl` e só decodifica a linha que contém o caminho da raiz como ele aparece no JSON: com os acentos como são (`json.dumps(raiz, ensure_ascii=False)[1:-1]`), que é como o Claude Code grava, e com o escape `\u`, por garantia. O arquivo lido sem nenhuma linha do repositório fica no resumo com a data e o tamanho, e não se lê de novo enquanto eles não mudam; o que tem alguma linha do repositório se lê sempre. Depois confere de verdade: `cwd == raiz` ou `cwd` começa com `raiz + "/"`, o que separa `xavier` de `xavier-antigo`. Linha que não é JSON válido ou que não tem `timestamp` é ignorada. *Alternativa:* ler só a pasta de `projects` com o nome do repositório. Recusada porque a sessão aberta noutra pasta e que trabalha no repositório ficaria de fora, e o nome da pasta é um detalhe interno do Claude Code.

### D4. Eventos e intervalos de cada conversa
Os eventos de uma conversa (`sessionId`) são as linhas `user` e `assistant` com hora, das conversas principal e dos subagentes, em ordem de hora. O evento é "pedido" quando a linha é `user`, sem `isMeta`, sem `isSidechain`, sem `isCompactSummary`, e com conteúdo que não é só `tool_result`; os demais são "IA". Entre dois eventos seguidos com até 30 minutos de distância nasce um intervalo, do tipo "usuario" se o segundo evento é um pedido, e "ia" se não é. As linhas `attachment`, `system` e as de controle não são eventos. *Alternativa:* contar do pedido até o fim da resposta inteira, como na descrição. Recusada porque uma resposta parada horas à espera de uma permissão contaria horas de IA; o corte de 30 minutos entre eventos resolve isso e mede o mesmo nos casos normais.

### D5. União por dia
Os intervalos de todas as conversas viram pares de segundos desde a época e são cortados na meia-noite local. Por dia: o total é o tamanho da união de todos; o tempo do usuário, o da união dos intervalos "usuario"; e o da IA sozinha, a diferença. *Alternativa:* somar os intervalos sem unir. Recusada porque duas conversas em paralelo dobrariam as horas.

### D6. O resumo
JSON com `versao: 1`, a `raiz` e `conversas`, um mapa de `sessionId` para a lista de intervalos `[início, fim, tipo]`, com início e fim em ISO 8601 UTC. A cada execução, a conversa que ainda tem arquivo é recalculada e juntada à guardada, numa união por tipo de intervalo; a que não tem mais arquivo fica como estava. Assim o intervalo novo de uma conversa que cresceu entra uma vez só, e a conversa apagada, ou só o arquivo de um subagente dela, continua contando. O resumo que existe e não se lê (não é JSON, é de outra versão, tem uma entrada fora do formato) faz o comando parar com erro, sem gravar nada: ele é a única cópia das horas já apagadas. O arquivo é gravado num temporário de nome único da mesma pasta, levado ao disco (`fsync`) e renomeado, para que nem uma queda nem outra execução ao mesmo tempo o corrompam. *Alternativa:* guardar os eventos crus. Recusada porque o intervalo é menor e é o que a apuração usa.

### D7. Os commits
`git log --branches --remotes --tags --format=%H %aI`, cada hash uma vez, pela data de autor, convertida ao fuso local. *Alternativa:* `--all`. Recusada porque inclui o `stash`, que não é trabalho entregue. As sessões seguem o método da página avulsa: até 2 horas entre commits, 30 minutos antes do primeiro, sem passar da meia-noite do dia dele, e corte na meia-noite. Os commits só valem nos dias em que as conversas não deram tempo nenhum.

### D8. A página
O Python monta os dados: um registro por dia com a data, a fonte, o total, o tempo do usuário e o da IA sozinha (só na fonte "conversas") e os intervalos do dia nas posições do relógio local, em minutos de 0 a 1440 (no dia da mudança de horário, a posição segue o relógio); o dia cujo total arredonda a zero não entra; mais os totais e as datas de início e fim. O modelo desenha:
- a linha do tempo semana a semana, com segunda a domingo nas linhas e um quadrado por dia, preenchido conforme as horas numa escala fixa de 0 a 20 h;
- as horas somadas por dia da semana;
- a fita hora a hora de cada dia;
- a fonte de cada dia e o método.

A página só usa fontes do sistema e nenhum endereço externo, e segue o tema claro ou escuro do sistema. *Alternativa:* fontes do Google, como na página avulsa. Recusadas porque carregar da rede contraria o requisito e a página pode ser aberta sem conexão.

### D9. A configuração e o aviso
A pasta de configuração é `CLAUDE_CONFIG_DIR`, ou `~/.claude` quando ela falta ou é vazia; a de dados, `XDG_DATA_HOME`, ou `~/.local/share` nas mesmas condições (a regra de tratar vazio como ausente vale também aqui). O aviso da guarda lê `cleanupPeriodDays` de `<configuração>/settings.json`: ausente, não numérico ou menor que 365 dá o aviso; um `settings.json` que não existe ou não é JSON válido também. O aviso cita o prazo de verdade (o valor definido, ou os 30 dias do padrão), vai para a saída de erro, e o código de saída continua 0.

### D10. A saída
Três linhas, no máximo: o período e o total (`26/05/2026 a 20/10/2026: 57 dias, 201 h`), o caminho da página e, quando couber, o aviso da guarda.

## Risks / Trade-offs

- [O formato das conversas é interno do Claude Code e pode mudar] → Os testes fixam o formato lido hoje com conversas de exemplo. Uma linha que não se entende é ignorada, e o dia sem conversa entendida cai na estimativa pelos commits, com a fonte "commits" na página: a falha aparece, não quebra.
- [1 GB de conversas a cada execução, e mais a cada ano com a guarda longa] → O arquivo sem nada do repositório que não mudou não se lê de novo, e o filtro pelo texto do caminho antes de decodificar o JSON deixa só as linhas do repositório. Os arquivos do próprio repositório se leem a cada execução: guardar o estado por conversa custaria mais complexidade e risco de hora errada do que o tempo que ganharia.
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

## Respostas à revisão

O `/opsx:verify` (sessão sem o contexto de quem escreveu a change) e o `/code-review 10`, de 2026-10-21. Cada ponto, com a decisão; os testes novos estão no grupo 7 das tarefas e falharam antes do código, salvo o `test_tempo_arquivo_que_mudou_e_relido`, que já passava.

| # | Origem | Achado | Decisão |
|---|---|---|---|
| 1 | verify 1, review 1 | A raiz com acento no caminho: o filtro usava o escape `\u` do `json.dumps`, e o Claude Code grava os acentos como são; nenhuma conversa entrava. Conferido numa sonda com `projeto-ação`: 0 conversas no resumo. | Aplicado: o filtro procura as duas formas (D3). Cenário "Caminho com acento". |
| 2 | review 2 | O resumo ilegível ou de outra versão era lido como vazio e sobrescrito, e as horas das conversas já apagadas se perdiam. | Aplicado: o comando para com erro, sem gravar (D6). Requisito "Resumo ilegível preservado", cenário "Resumo corrompido". |
| 3 | review 3 | A conversa recalculada substituía a guardada: apagado só o arquivo de um subagente, sumiam as horas que os eventos dele preenchiam. | Aplicado: as horas guardadas e as recalculadas se juntam por tipo (D6). Cenário "Arquivo de subagente apagado". |
| 4 | review 4 | Uma entrada fora do formato no resumo derrubava toda execução, com rastro de exceção. | Aplicado: o resumo é conferido por inteiro e tratado como o do item 2. Cenário "Entrada fora do formato". |
| 5 | review 5 | O temporário tinha nome fixo e não ia ao disco antes da troca. | Aplicado: nome único (`mkstemp`) e `fsync` (D6). Teste `test_tempo_temporario_antigo_nao_atrapalha`, sem cenário: é da gravação. |
| 6 | review 6 | Os 30 minutos antes de um commit das 00:10 caíam no dia anterior, que aparecia como dia trabalhado sem commit. | Aplicado: o começo da sessão não passa da meia-noite do dia do commit (D7). Cenário "Commit logo depois da meia-noite". No Xavier, tirou 23/06 e 07/09, dois dias de 12 minutos sem commit. |
| 7 | verify 2, review 7 | O aviso falava em "prazo padrão de 30 dias" também com um valor definido abaixo de 365. | Aplicado: o aviso cita o valor de verdade (D9). Cenário "Guarda curta definida". |
| 8 | review 8 | O dia de conversa com total arredondado a zero dava `NaN%` na página. | Aplicado no Python: o dia sem tempo apurado das conversas cai nos commits, ou não entra (D8). Cenário "Atividade de segundos". |
| 9 | review 9 | A fita do dia da mudança de horário saía deslocada uma hora, e podia passar dos 1440 minutos. | Aplicado: a posição segue o relógio local (D8). Cenário "Dia da mudança de horário", com `TZ=EST5EDT,M3.2.0,M11.1.0`, que não depende do banco de fusos da máquina. |
| 10 | review 10 | Toda execução relia todas as conversas da máquina, e a guarda longa faz isso crescer sem fim. | Aplicado em parte: o arquivo sem nada do repositório que não mudou não se lê de novo (D3), com o requisito "Leitura só do que mudou". Recusado, com o motivo, guardar o estado por conversa para pular também os arquivos do repositório: o arquivo de um subagente que muda sem o da conversa principal exigiria reler a conversa inteira, e o ganho não paga o risco de hora errada. O `sorted()` do `rglob` saiu. No Xavier, de 4,4 s para 1,4 s, com 350 dos 508 arquivos pulados. |
| 11 | verify 3 | "1 dias" na saída. | Aplicado. Teste `test_tempo_um_dia_no_singular`. |
| 12 | verify 4 | O resumo guardava a `raiz`, que o requisito não citava. | Aplicado no requisito: ele passa a listar o que o resumo guarda, com a raiz e a lista do item 10. |

O teste `test_scripts_cabem_no_lint_de_quem_copia` pegou uma linha de 101 caracteres na docstring nova, que o ruff com `--isolated` não confere; a frase foi quebrada.

## Execução manual depois da revisão (tarefa 7.11), em 2026-10-21

- Comando: `python3 -I ../trilha-ai/modelo/trilha/tempo.py`, dentro do Xavier, sobre o resumo da execução de 2026-10-20. Resultado: `26/05/2026 a 21/10/2026: 58 dias, 179 h`, com o código de saída 0, e o `git status --porcelain` igual antes e depois.
- Contra o código antes da revisão, rodado no mesmo momento com uma pasta de dados vazia: 60 dias e 179,4 h; agora, 58 dias e 178,9 h. A diferença é toda do item 6: 23/06 e 07/09, com 12,3 e 12,4 minutos e nenhum commit no dia, saíram. A hora a mais em relação a 2026-10-20 (178 h) é o trabalho feito no Xavier desde então.
- A primeira execução levou 4,4 s; as duas seguintes, 1,4 s, com 350 dos 508 arquivos de conversa da máquina pulados.

