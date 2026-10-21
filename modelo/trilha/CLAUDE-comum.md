# CLAUDE-comum.md

Versão 2.10, de 2026-10-21. Não edite este arquivo nem a pasta `trilha/`: o que é deste repositório vai no `CLAUDE.md`.

Regras comuns a todo repositório que segue o método Trilha AI (PRD → TDD → OpenSpec) com o Claude Code, o OpenSpec, o plugin `sdd`, o Python 3 e o GitHub, em Linux ou WSL. Cada repositório o guarda na pasta `trilha/`, com o resto do que o método copia sem mudar, e o importa no seu `CLAUDE.md` com `@trilha/CLAUDE-comum.md`. Este arquivo só traz o que vale para todo projeto; o que é de um projeto (o que ele é, comandos, stack, dados, armadilhas próprias) fica no `CLAUDE.md` dele, no esqueleto da última seção. Em conflito, vale nesta ordem: as travas do kit; a escolha do usuário; o OpenSpec (fluxo e formato); a regra do `CLAUDE.md` do repositório declarada em "Exceções ao comum", com o motivo (fora dessa seção, regra contrária a esta não vale); este arquivo, que conta como parte do `CLAUDE.md` que o importa; o `openspec/config.yaml`; as skills `sdd:*`.

## O método: documentos que mandam, nesta ordem

Os documentos do método vivem na pasta `sdd/`, na raiz.

1. `sdd/prd-<nome>.md`: o quê e o porquê. Nenhuma palavra de tecnologia, salvo a restrição que o usuário declara imposta de fora, que a skill registra à parte. Escrito com a skill `sdd:prd` e aprovado bloco a bloco pelo usuário, como a skill pede (gate 1).
2. `sdd/tdd-<nome>.md`: as decisões técnicas, como ADRs. Escrito com a skill `sdd:tdd` e aprovado bloco a bloco pelo usuário, como a skill pede (gate 2).
3. `sdd/decomposicao-<nome>.md`: as changes em ordem, com a tabela "Ciclo". Vem da skill `sdd:briefing`, que também escreve cada briefing e audita o gate 3.
4. `sdd/briefing-openspec/briefing-change-NN-<nome>.md`: a entrada de cada change, no formato da skill `sdd:briefing`.
5. `openspec/specs/`: o comportamento já entregue. O `openspec/config.yaml` traz o contexto do projeto, com a língua, e as regras por artefato (a origem citada de cada requisito e cenário, um teste por cenário); o OpenSpec o lê ao gerar cada artefato, e o briefing não repete o que está nele.

- `sdd/documentacao.html` é a documentação do projeto, gerada por `python3 trilha/gerar_pagina_sdd.py` ao fechar cada etapa (PRD, TDD, decomposição, change arquivada); não se edita à mão.
- Um registro de processo (o que foi pedido e feito em cada etapa) é opcional; quem o mantém declara no `CLAUDE.md` onde ele fica e quando é atualizado.
- Faltou requisito: a pendência volta ao PRD. Faltou decisão técnica: volta ao TDD. Não improvise.
- PRD e spec em desacordo: vale o PRD aprovado, e uma change corrige o comportamento e o spec; se o certo for o spec, o PRD ganha versão nova. O usuário escolhe qual dos dois está certo.
- Para contrariar ou estender um ADR, pare e pergunte. Mudança de decisão técnica é uma nova versão do TDD, aprovada antes do código.
- Ao fechar o gate 2, antes da decomposição, a stack decidida no TDD entra no `.github/dependabot.yml`, no bloco do `.gitignore` e na linha "Stack" do `context` do `openspec/config.yaml`. A parte da stack do `scripts/check.sh` e os passos do `.github/workflows/verificacao.yml` entram na change 01, que cria o manifesto e o primeiro teste. Até lá, o `check.sh` avisa que ela falta.
- Projeto que nasceu sem PRD ou TDD escreve o que falta antes da próxima change que toque requisito ou tecnologia. Até lá, uma correção de comportamento que um spec já descreve nasce de um briefing curto, escrito a partir desse spec (o requisito e o cenário corrigidos, o defeito, o esperado, o que já existe), sem requisito novo nem decisão técnica, aprovado pelo usuário; o resto do ciclo é o mesmo. Nesse caso, o passo do ciclo de cada change fica no `ANDAMENTO.md`, e a change arquivada entra na tabela "Ciclo" quando a decomposição nascer. Com o PRD e o TDD aprovados, a decomposição vem antes de qualquer change.
- Toda mudança de requisito, comportamento observável, infraestrutura ou contrato passa por uma change. Typo, documentação, refatoração sem efeito, ajuste de teste e a cópia nova do kit (a pasta `trilha/` e o que o `kit.py atualizar` escreve) dispensam change, como o pull request do Dependabot, que vai à main com a verificação verde, merge commit e o "sim" do usuário. A mudança de infraestrutura sem requisito é change com `skip_specs: true` no `.openspec.yaml`, de briefing curto com a origem no ADR.

## O ciclo de cada change (OpenSpec)

1. briefing aprovado pelo usuário, numa branch `change/NN-nome` aberta a partir da main atualizada antes do primeiro commit da change; o usuário dá aqui um só "sim" para todos os envios da branch até o merge;
2. `/opsx:propose @sdd/briefing-openspec/briefing-…md`: só planejamento, nenhum código; commit, envio e pull request em rascunho (`gh pr create --draft`), que mostra o plano antes do código;
3. a revisão dos artefatos, que o OpenSpec pede ao fim do propose, antes do apply, feita como a auditoria do gate 3, pelo checklist da skill `sdd:briefing`. O que reprovar se corrige com `/opsx:update`, ou pelo caminho que ele indicar, depois da escolha do usuário; a revisão termina com a auditoria aprovada, em commit e envio;
4. `/opsx:apply`, no fluxo do OpenSpec; termina na tarefa que a regra das tarefas do `openspec/config.yaml` põe por último; commit e envio a cada parada, nunca um só no fim;
5. `/opsx:verify` e a revisão independente do código, o `/code-review <número do PR>` do Claude Code, rodado numa sessão nova, depois do `/clear` (o `ANDAMENTO.md` guarda o ponto de volta): quem escreveu não é o único a revisar, nem com o contexto de quem escreveu. Cada sugestão dos dois é aplicada ou recusada por escrito no `design.md` da change, com o motivo; commit e envio;
6. `/opsx:archive`; em seguida, os passos que o `operations.archive` do `openspec/config.yaml` lista; commit e envio, e o PR sai do rascunho (`gh pr ready`): código, specs e página chegam juntos à main;
7. o merge, só com a verificação do GitHub verde no PR (`gh pr checks`) e com um "sim" só para ele: `gh pr merge --merge --delete-branch` (merge commit, nunca squash nem rebase, que apagariam os pontos de retomada ou a fronteira da change). De volta à main atualizada, o `ANDAMENTO.md` vai a "nada em andamento" num commit, enviado sob o mesmo "sim". A change fecha aqui, não no archive; a próxima abre outra branch.

- O OpenSpec comanda: o método nunca se sobrepõe ao fluxo dele, e o que se sobrepuser muda no método, não no OpenSpec. O ciclo acima usa todos os passos que ele oferece; quando um comando oferece pular um (arquivar sem o verify, aplicar antes da revisão, arquivar sem atualizar os specs), quem escolhe é o usuário, com a recomendação de não pular.
- Antes de propor, rode `openspec list`: evita change duplicada ou em colisão com outra change ativa. Conte as tarefas de uma change por `openspec instructions apply --change <nome> --json` (`progress.total`) antes de escrever o número.
- Os specs em `openspec/specs/` mudam pelos caminhos do OpenSpec: o delta, que o archive aplica, e a edição direta que as instruções dele pedem (o Purpose de um spec novo). Fora disso, à mão, só typo ou link; outra edição à mão pede uma change retroativa.
- Nome das pastas: a change ativa nasce como `NN-nome`, e o archive do OpenSpec acrescenta a data (`AAAA-MM-DD-NN-nome`); o número tem dois dígitos até 99 e três a partir de 100, sem renomear os anteriores. Os specs seguem o nome que o OpenSpec dá: o comportamento que o spec descreve, em kebab-case, sem data nem número; o delta de um spec existente usa exatamente o nome da pasta principal. Confira com `ls` antes de criar e depois de arquivar.
- Espere a escolha do usuário antes de ampliar o escopo de uma change aprovada. Achado fora do escopo vira outra change ou revisão do PRD ou do TDD; achado que o spec já cobre é correção dentro da change, com o teste que falha escrito antes.

## Registrar cada decisão no artefato dono dela

- Decisão de produto: nova versão do PRD. Decisão técnica: nova versão do TDD. Decisão local de uma change: o `design.md` dela; o OpenSpec o cria só quando cabe, e, sem ele, o `notas.md` da pasta da change faz as vezes dele em todo lugar do método que cita o `design.md`. Os marcos de cada change (briefing, auditoria, archive): a tabela "Ciclo" da decomposição, atualizada no commit do passo de cada marco; o passo em curso, o `ANDAMENTO.md`. Desvio ou incidente, às claras e nunca escondido: o `design.md` da change em curso, ou a decomposição se estiver fora de change. Nada fica só na conversa.
- Correção de texto no PRD, no TDD ou na decomposição que não muda requisito, decisão nem ordem (redação, erro, referência) não sobe a versão dele nem a linha "de origem" de quem o cita: fica no registro de processo, se houver, ou na mensagem do commit. Só a mudança de sentido é versão nova, aprovada pelo usuário; ela atualiza a linha "de origem" de quem o cita, sem versão nova dele.

## Trabalho interrompível: saber onde parou

Uma sessão pode cair a qualquer momento (energia, créditos, erro). O que não está em disco se perde, e o que não está anotado precisa ser adivinhado. Por isso:

- `ANDAMENTO.md`, na raiz, existe sempre e diz, em até dez linhas: o estado ("em andamento" ou "nada em andamento"), a etapa (PRD, TDD, decomposição, a change e o passo do ciclo, ou o trabalho fora de change), a unidade em curso (o artefato, ou o apply, cujo progresso é o `tasks.md`), o que já está feito nela, o próximo passo exato e a hora, lida do relógio (`date`) e nunca estimada; não guarda o estado do envio ao remoto, que o `git status` mostra. Escreva-o **antes** de começar cada unidade de trabalho e reescreva-o ao terminá-la; ao fechar a etapa, volte a "nada em andamento". É versionado e vai no commit de cada unidade.
- Durante o apply, o ponto de retomada é o `tasks.md`, que o OpenSpec marca tarefa a tarefa. Os commits de cada passo do ciclo são os pontos de retomada que sobrevivem a qualquer queda.
- Todo repositório do método tem, desde a etapa 0, um remoto privado no GitHub (`origin`): o commit sobrevive à queda da sessão; o envio, à perda da máquina. Faltou o remoto: diga-o antes de qualquer outra coisa e proponha criá-lo com `gh repo create <nome> --private --source . --push`, só com "sim".
- Envios ao remoto: fora de change (o PRD, o TDD, a decomposição e o trabalho que dispensa change), o commit vai direto à main e, ao fechar a etapa, diga ao usuário quantos commits estão por enviar; envie só com "sim". Dentro de change, valem o "sim" dos envios da branch e o do merge (passos 1 e 7 do ciclo).
- Ao começar qualquer sessão, antes de agir: leia `ANDAMENTO.md`, `git status`, `git log -3`, se houver change ativa, `openspec list` e, numa branch `change/…`, `gh pr view` e `gh pr checks` (depois do archive, só o PR diz se falta o merge); diga onde parou, o que está por commitar e qual é o próximo passo. Trabalho não commitado que você encontrar só é continuado ou descartado com a escolha do usuário.

## Como trabalhar com o usuário

- Responda em PT-BR, com acentos, resumido, com as ações em ordem.
- Aprovações e decisões em linguagem simples: frases curtas, sem siglas nem códigos; os códigos ficam nos arquivos.
- Toda decisão com a consequência de cada opção e uma recomendação. O usuário aprova ou veta, nunca escolhe no vácuo.
- Pedido curto, com erro de digitação ou com mais de uma leitura: diga a leitura adotada antes de agir.
- Pedido que contraria requisito ou ADR volta ao usuário com opções; nunca é atendido em silêncio.
- Delegação ("escolha o melhor") não dispensa o gate: siga a recomendação já apresentada e registre a delegação.
- Revisão ou auditoria: relatório e opções, sem editar nada; corrija só depois da escolha, com a causa raiz provada. Até a escolha, a auditoria não é unidade de trabalho (a do gate 3 também não): não muda o `ANDAMENTO.md` nem o registro de processo. A escolha, com ou sem correção, é unidade de trabalho: atualiza o `ANDAMENTO.md` e leva o relatório ao registro, se houver. Uma auditoria fecha com a verificação do repositório verde e sem contradição; repetição e redação menores ficam no relatório e se corrigem quando o arquivo mudar por outro motivo.
- Ao fechar trabalho seu, releia o diff inteiro e corrija antes de entregar.
- Publique, faça deploy ou mude versão só com "sim" explícito para aquela alteração; o envio ao GitHub segue a regra dos envios, em "Trabalho interrompível".
- Um "sim" isolado responde só à pergunta principal da mensagem; o envio ao remoto perguntado à parte pede "sim" para ele (ou "sim, em tudo"). Em pergunta com mais de uma decisão, confirme cada uma.
- Não escreva em outro repositório nem troque de projeto sem ordem explícita nomeando-o.
- Sugira `/clear` em uma linha no fim da mensagem em todo corte natural (etapa fechada, change com o merge feito, conferência longa terminada, antes de outra frente), só com tudo em disco e commitado, nunca no meio de uma tarefa; diga o que o usuário recupera ao voltar e mostre, num bloco de código, o comando exato a dar na próxima sessão.

## Convenções

- Commits em Conventional Commits, em PT-BR, com escopo quando o commit toca uma parte nomeável (`feat(web): …`), e a linha de coautoria da IA.
- Temporário nunca vai a arquivo rastreado, nem por um minuto.

## Armadilhas

- As travas do kit não se contornam: o `trilha/hooks/pre-commit` (ligado por `git config core.hooksPath trilha/hooks`) confere as regras e o método antes de cada commit, o `trilha/hooks/pre-push` roda, a cada envio, o hook próprio do projeto em `.githooks/pre-push`, quando ele existe, e o `trilha/guarda.py`, hook do Claude Code no `.claude/settings.json`, barra o envio forçado, o `--no-verify`, o desligamento da trava do commit, o `pkill -f` e o `pgrep -f` (o padrão casa o próprio shell: encerre processos pelo PID guardado) e o merge sem `--merge` ou sem a verificação verde. Trava que barrar algo legítimo volta ao usuário.
- Nunca pare, remova ou mate processo ou container de outro projeto sem ordem explícita.
- Senha, chave ou token nunca entram no git; o CI os procura no histórico (gitleaks). Achado real: troque a chave antes de qualquer outra coisa, porque apagá-la do git não a desfaz no histórico; falso positivo vai ao `.gitleaksignore`, com a escolha do usuário.
- Dado real nunca serve a teste manual: use uma cópia descartável e prove, antes e depois, que o real não mudou.
- `git status` limpo não prova que nada vazou: confira o `git log`.
- Ao renomear ou citar arquivo, script ou rota, faça grep do nome no repositório inteiro antes do commit.
- Ao trocar texto num documento grande, use um trecho único e confira no diff as linhas removidas.
- Quebrou o código de propósito para provar um teste (mutação): desfaça-a por edição inversa, nunca com `git checkout`, e confira no `git diff` que só a mudança entregue sobrou.
- Teste instável só está resolvido após 5 rodadas consecutivas verdes.
- Testes sem rede; projeto que consome uma fonte externa grava a resposta real uma vez e a simula.
- Rode a verificação do repositório sozinha e confira o código de saída antes do commit; nunca a encadeie com um filtro (`| tail`, `| grep`), que esconde um lint reprovado.

## O `CLAUDE.md` de cada repositório

Só o que não se deduz lendo o código, neste esqueleto: **O que é** · **Documentos** (os nomes reais do PRD, do TDD e da decomposição, em `sdd/`; o `openspec/config.yaml` e o `ANDAMENTO.md`) · **Comandos** (rodar, testar, publicar; a verificação chama o `trilha/verifica.sh`) · **Regras de código** · **Dados a proteger** · **Armadilhas próprias** · **Exceções ao comum**, cada uma com o motivo. O `CLAUDE.md` e o `CLAUDE-comum.md` somados têm no máximo 200 linhas e 32 KB.
