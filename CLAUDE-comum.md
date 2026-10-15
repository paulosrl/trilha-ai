# CLAUDE-comum.md

Versão 1.15, de 2026-10-14. Não edite este arquivo: o que é deste repositório vai no `CLAUDE.md`.

Regras comuns a todo repositório que segue o método Trilha AI (PRD → TDD → OpenSpec) com o Claude Code, o OpenSpec, o plugin `sdd` e o Python 3, em Linux ou WSL. Cada repositório o importa no seu `CLAUDE.md` com `@CLAUDE-comum.md`. Este arquivo só traz o que vale para todo projeto; o que é de um projeto (o que ele é, comandos, stack, dados, armadilhas próprias) fica no `CLAUDE.md` dele, no esqueleto da última seção. Regra do `CLAUDE.md` do repositório sobre o mesmo assunto prevalece sobre esta, desde que declarada em "Exceções ao comum", com o motivo.

## O método: documentos que mandam, nesta ordem

Os documentos do método vivem na pasta `sdd/`, na raiz.

1. `sdd/prd-<nome>.md`: o quê e o porquê. Nenhuma palavra de tecnologia. Escrito com a skill `sdd:prd` e aprovado seção por seção pelo usuário (gate 1).
2. `sdd/tdd-<nome>.md`: as decisões técnicas, como ADRs. Escrito com a skill `sdd:tdd` e aprovado seção por seção pelo usuário (gate 2). Não se redecidem numa change.
3. `sdd/decomposicao-<nome>.md`: as changes, a ordem de execução com a razão, as regras de convivência e a tabela "Ciclo". Vem da skill `sdd:briefing`, que também escreve cada briefing e audita o gate 3.
4. `sdd/briefing-openspec/briefing-change-NN-<nome>.md`: a entrada de cada change, autossuficiente: requisitos, regras, critérios de aceite e ADRs na íntegra, mais "o que já existe".
5. `openspec/specs/`: o comportamento já entregue. O `openspec/config.yaml` traz o contexto do projeto e as regras por artefato (a língua, a origem citada de cada requisito e cenário, um teste por cenário); o OpenSpec o lê ao gerar cada artefato, e o briefing não repete o que está nele.

- `sdd/documentacao.html` é a página do método, gerada por `python3 scripts/gerar_pagina_sdd.py` ao fechar cada etapa (PRD, TDD, decomposição, change arquivada); não se edita à mão.
- Um registro de processo (o que foi pedido e feito em cada etapa) é opcional; quem o mantém declara no `CLAUDE.md` onde ele fica e quando é atualizado.
- Faltou requisito: a pendência volta ao PRD. Faltou decisão técnica: volta ao TDD. Não improvise.
- PRD e spec em desacordo: vale o PRD aprovado, e uma change corrige o comportamento e o spec; se o certo for o spec, o PRD ganha versão nova. O usuário escolhe qual dos dois está certo.
- Para contrariar ou estender um ADR, pare e pergunte. Mudança de decisão técnica é uma nova versão do TDD, aprovada antes do código.
- Projeto que nasceu sem PRD ou TDD escreve o que falta antes da próxima change que toque requisito ou tecnologia. Até lá, uma correção de comportamento que um spec já descreve nasce de um briefing curto, escrito a partir desse spec (o requisito e o cenário corrigidos, o defeito, o esperado, o que já existe), sem requisito novo nem decisão técnica, aprovado pelo usuário; o resto do ciclo é o mesmo. Nesse caso, o passo do ciclo de cada change fica no `ANDAMENTO.md`, e a change arquivada entra na tabela "Ciclo" quando a decomposição nascer. Com o PRD e o TDD aprovados, a decomposição vem antes de qualquer change.
- Toda mudança de requisito, comportamento observável, infraestrutura ou contrato passa por uma change. Typo, documentação, refatoração sem efeito e ajuste de teste dispensam change.

## O ciclo de cada change (OpenSpec), sem pular etapa

1. briefing aprovado pelo usuário;
2. `/opsx:propose @sdd/briefing-openspec/briefing-…md`: só planejamento, nenhum código;
3. a revisão dos artefatos, que o OpenSpec pede ao fim do propose, antes do apply, feita como a auditoria do gate 3, pelo checklist de 8 itens da skill `sdd:briefing`. O que reprovar se corrige com `/opsx:update`, depois da escolha do usuário; a revisão termina com a auditoria aprovada;
4. `/opsx:apply`, no fluxo do OpenSpec; a última tarefa do `tasks.md` é a execução manual, em dado descartável, com o usuário olhando (regra das tarefas no `openspec/config.yaml`);
5. `/opsx:verify`: cada sugestão aplicada ou recusada por escrito, com o motivo;
6. `/opsx:archive`; em seguida, os passos que o `operations.archive` do `openspec/config.yaml` lista.

- Não edite `openspec/specs/` à mão, exceto typo ou link: os specs mudam por delta e archive. Se editou, registre uma change retroativa.
- Nome das pastas: a change ativa nasce como `NN-nome`, e o archive do OpenSpec acrescenta a data (`AAAA-MM-DD-NN-nome`); o número tem dois dígitos até 99 e três a partir de 100, sem renomear os anteriores. Os specs seguem o nome que o OpenSpec dá: o comportamento que o spec descreve, em kebab-case, sem data nem número; o delta de um spec existente usa exatamente o nome da pasta principal. Confira com `ls` antes de criar e depois de arquivar.
- Espere a escolha do usuário antes de ampliar o escopo de uma change aprovada. Achado fora do escopo vira outra change ou revisão do PRD ou do TDD; achado que o spec já cobre é correção dentro da change, com o teste que falha escrito antes.

## Registrar cada decisão no artefato dono dela

- Decisão de produto: nova versão do PRD. Decisão técnica: nova versão do TDD. Decisão local de uma change: o `design.md` dela. O passo do ciclo em que cada change está: a tabela "Ciclo" da decomposição. Desvio ou incidente, às claras e nunca escondido: o `design.md` da change em curso, ou a decomposição se estiver fora de change. Nada fica só na conversa.
- Correção de texto no PRD, no TDD ou na decomposição que não muda requisito, decisão nem ordem (redação, erro, referência) não sobe a versão dele nem a linha "de origem" de quem o cita: fica no registro de processo, se houver, ou na mensagem do commit. Só a mudança de sentido é versão nova, aprovada pelo usuário.

## Trabalho interrompível: saber onde parou

Uma sessão pode cair a qualquer momento (energia, créditos, erro). O que não está em disco se perde, e o que não está anotado precisa ser adivinhado. Por isso:

- `ANDAMENTO.md`, na raiz, existe sempre e diz, em até dez linhas: o estado ("em andamento" ou "nada em andamento"), a etapa (PRD, TDD, decomposição, a change e o passo do ciclo, ou o trabalho fora de change), a unidade em curso (o artefato, ou o apply, cujo progresso é o `tasks.md`), o que já está feito nela, o próximo passo exato e a hora; não guarda o estado do envio ao remoto, que o `git status` mostra. Escreva-o **antes** de começar cada unidade de trabalho e reescreva-o ao terminá-la; ao fechar a etapa, volte a "nada em andamento". É versionado e vai no commit de cada unidade.
- Durante o apply, o ponto de retomada é o `tasks.md`, que o OpenSpec marca tarefa a tarefa. Faça um commit ao fim do propose, outro quando a auditoria do gate 3 for aprovada e outro a cada parada do apply, nunca um só commit no fim: o commit é o ponto de retomada que sobrevive a qualquer queda.
- Ao fechar uma etapa, diga ao usuário quantos commits estão por enviar ao remoto; envie só com "sim".
- Ao começar qualquer sessão, antes de agir: leia `ANDAMENTO.md`, `git status`, `git log -3` e, se houver change ativa, `openspec list`; diga onde parou, o que está por commitar e qual é o próximo passo. Trabalho não commitado que você encontrar só é continuado ou descartado com a escolha do usuário.

## Como trabalhar com o usuário

- Responda em PT-BR, com acentos, resumido, com as ações em ordem.
- Aprovações e decisões em linguagem simples: frases curtas, sem siglas nem códigos; os códigos ficam nos arquivos.
- Toda decisão com a consequência de cada opção e uma recomendação. O usuário aprova ou veta, nunca escolhe no vácuo.
- Pedido curto, com erro de digitação ou com mais de uma leitura: diga a leitura adotada antes de agir.
- Pedido que contraria requisito ou ADR volta ao usuário com opções; nunca é atendido em silêncio.
- Delegação ("escolha o melhor") não dispensa o gate: siga a recomendação já apresentada e registre a delegação.
- Revisão ou auditoria: relatório e opções, sem editar nada; corrija só depois da escolha, com a causa raiz provada. Até a escolha, a auditoria não é unidade de trabalho (a do gate 3 também não): não muda o `ANDAMENTO.md` nem o registro de processo; o relatório entra no registro junto com a primeira correção.
- Ao fechar trabalho seu, releia o diff inteiro e corrija antes de entregar.
- Publique, faça deploy ou mude versão só com "sim" explícito para aquela alteração.
- Não escreva em outro repositório nem troque de projeto sem ordem explícita nomeando-o.
- Sugira `/clear` em uma linha no fim da mensagem em todo corte natural (etapa fechada, change arquivada, conferência longa terminada, antes de outra frente), só com tudo em disco e commitado, nunca no meio de uma tarefa; diga o que o usuário recupera ao voltar.

## Convenções

- Commits em Conventional Commits, em PT-BR, com escopo quando o commit toca uma parte nomeável (`feat(web): …`), e a linha de coautoria da IA.
- Temporários só no scratchpad da sessão, nunca em arquivo rastreado, nem por um minuto.

## Armadilhas

- Nunca use `pkill -f` ou `pgrep -f` com um padrão que possa casar o próprio shell; encerre processos pelo PID guardado.
- Nunca pare, remova ou mate processo ou container de outro projeto sem ordem explícita.
- Dado real nunca serve a teste manual: use uma cópia descartável e prove, antes e depois, que o real não mudou.
- `git status` limpo não prova que nada vazou: confira o `git log`.
- Ao renomear ou citar arquivo, script ou rota, faça grep do nome no repositório inteiro antes do commit.
- Ao trocar texto num documento grande, use um trecho único e confira no diff as linhas removidas.
- Teste instável só está resolvido após 5 rodadas consecutivas verdes.
- Testes sem rede; projeto que consome uma fonte externa grava a resposta real uma vez e a simula.
- Rode a verificação do repositório sozinha e confira o código de saída antes do commit; nunca a encadeie com um filtro (`| tail`, `| grep`), que esconde um lint reprovado.

## O `CLAUDE.md` de cada repositório

Só o que não se deduz lendo o código, neste esqueleto: **O que é** · **Documentos** (os nomes reais do PRD, do TDD e da decomposição, em `sdd/`; o `openspec/config.yaml` e o `ANDAMENTO.md`) · **Comandos** (rodar, testar, publicar; a verificação chama o `confere_regras.py` e o `confere_metodo.py`) · **Regras de código** · **Dados a proteger** · **Armadilhas próprias** · **Exceções ao comum**, cada uma com o motivo. O `CLAUDE.md` e o `CLAUDE-comum.md` somados têm no máximo 200 linhas.
