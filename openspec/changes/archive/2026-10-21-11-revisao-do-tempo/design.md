# Design

## Context

Ver `proposal.md` (Why). O `trilha/tempo.py` da 2.8:
- lê as linhas de conversa que contêm o caminho da raiz;
- descarta as de `cwd` fora dela antes de medir os intervalos;
- junta os eventos da conversa principal e dos subagentes pelo `sessionId`;
- lê os commits com `git log --format=%H %aI` e converte a data sem proteção;
- monta a página trocando `__TITULO__` e `__DADOS__` em todo lugar do modelo, inclusive no comentário dele.

## Goals / Non-Goals

**Goals:**
- As horas de um dia são só as do repositório, do usuário dele.
- Nenhuma linha estranha do git derruba o comando.

**Non-Goals:** os itens recusados no `proposal.md`, e as horas guardadas em número dentro do comando, que a revisão dos artefatos tirou da change (ver "Respostas à revisão").

## Decisions

### D1. Os eventos fora do repositório
A leitura de um arquivo de conversa passa a ter dois passos. O primeiro procura o caminho da raiz no texto e para no primeiro achado. No arquivo com ele, o segundo decodifica toda linha que tem `"cwd"`. O evento com `cwd` da raiz (D2) é "pedido" ou "ia", como antes; os outros são "fora". Cada evento guarda o arquivo de onde veio.

Na conversa, os eventos da raiz, de todos os arquivos dela, seguem em ordem de hora; a linha repetida em dois arquivos (a conversa retomada) é um evento só, com os dois arquivos. O par seguido conta, com até 30 minutos, salvo quando os dois têm um arquivo em comum e esse arquivo tem um evento "fora" entre eles. Assim, um subagente que trabalha noutra pasta não corta a conversa principal, e a conversa principal que sai e volta não conta o tempo fora.

*Alternativa:* calcular os intervalos arquivo por arquivo e juntar só depois. Recusada: o subagente deixaria de preencher as pausas da conversa principal, o que a change 10 conta ("Arquivo de subagente apagado").

O arquivo vai para a lista dos ignorados quando não tem nenhum evento da raiz, como na 2.8, e não quando só não cita o caminho.

### D2. A raiz, o repositório aninhado e o worktree
A pasta `.git` comum vem do `git rev-parse --git-common-dir`, resolvido a partir da raiz (o `--path-format=absolute` pediria o git 2.31). Para cada `cwd` diferente dentro da raiz, o comando sobe as pastas do `cwd` até a raiz, sem ela, procurando um `.git`:
- uma pasta `.git` é outro repositório;
- um arquivo `.git` cujo `gitdir:` aponta para dentro de `<raiz>/.git/worktrees/` é um worktree da própria raiz, e conta para ela (o Claude Code cria os dele em `.claude/worktrees/`);
- outro arquivo `.git`, como o de um submódulo (`.git/modules/`), é outro repositório.

O resultado fica guardado por `cwd`, na execução. Uma pasta que já não existe não tem `.git` e conta para a raiz.

### D3. Os commits
`git log --branches --remotes --tags --no-show-signature --format=%H%x00%ae%x00%aI`, com o caractere nulo entre os campos, que não aparece num e-mail. Usa o `%ae`, e não o `%aE`, porque o `user.email` não passa pelo `.mailmap`. A data passa pela mesma conversão das conversas, que aceita o `Z`. A linha que não tem os três campos, ou cuja data não se converte, é ignorada. Com o `user.email` do repositório (`git config user.email`), só contam os commits com esse e-mail de autor, sem diferença de maiúscula.

*Alternativa:* `--author`. Recusada porque ele casa por trecho, e um e-mail contido noutro passaria.

Os e-mails gravados em `trilha.email` (`git config --get-all trilha.email`, uma vez por repositório) também contam como do usuário: quem faz commits com mais de um e-mail grava os outros ali. Quando algum commit fica fora por causa do e-mail, o comando avisa até três dos e-mails que ficaram fora, com a contagem e o comando que inclui um deles; os de robôs (`[bot]`, como o Dependabot) e o vazio não entram no aviso, que sairia em toda execução. Assim, nada do usuário some sem aviso, e o Dependabot e as outras pessoas continuam fora. *Alternativa:* o `.mailmap` com o `%aE`. Recusada: ele é versionado no repositório, e o e-mail de uma pessoa não é regra do projeto. Achado na execução manual, com a escolha do usuário.

### D4. O dia com commit tem pelo menos 1 minuto
Depois das sessões e do corte por dia, o dia com commit que ficou com menos de 1 minuto estimado ganha o minuto que começa no primeiro commit dele. Isso cobre o commit das 00:00:00, sozinho ou emendado numa sessão do dia anterior.

### D5. A página
O `tempo.py` troca só os dois marcadores inteiros, `<title>__TITULO__</title>` e `<script id="dados" type="application/json">__DADOS__</script>`, uma vez cada. O título passa pelo `html.escape`, e o comentário do modelo deixa de citar os marcadores. No JSON dos dados, todo `<` vira `\u003c`, que o `JSON.parse` lê igual: nem `</script>` nem `<!--` fecham ou abrem nada. No código da página:
- o plural segue o número ("1 dia", "2 dias");
- a contagem das semanas arredonda a diferença de dias antes de somar 1, o que tira a hora a mais da mudança de horário;
- sai a função `clock`, que nada usa.

### D6. O resumo de outra pasta
Sem resumo para o caminho atual, o comando procura os resumos de nome `<nome>-<8 hexadecimais>.json`, exato, e confere que o nome da `raiz` gravada é o deste repositório. Se um deles tem outra `raiz`, o aviso cita o arquivo e a raiz dele. O resumo ilegível nessa busca é ignorado, porque o aviso é só uma ajuda.

### D7. A versão
"Versão 2.9, de 2026-10-21." no comum e `2.9.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [O segundo passo decodifica as linhas de `cwd` fora da raiz, no arquivo que tem a raiz] → São poucas, porque a conversa costuma ficar numa pasta. O arquivo de outro repositório continua sem ser decodificado.
- [Quem faz commits com outro e-mail no mesmo repositório os perderia da estimativa] → O `trilha.email` guarda os outros e-mails, e o aviso mostra os que ficaram fora.
- [Um par de eventos de arquivos diferentes conta mesmo que os dois arquivos tenham saído da raiz entre eles] → Aceito: é raro, e o corte de 30 minutos limita o erro.
- [Os testes não rodam o código da página] → O plural, a semana a mais e a função removida se conferem na execução manual.

## Migration Plan

O resumo da 2.8 é da versão 1 e guarda as horas que ela contou a mais (o tempo fora do repositório no meio de uma conversa, o de um repositório aninhado). A 2.9 o lê: a conversa que ainda existe é recalculada por inteiro, sem juntar as horas guardadas dela, e a já apagada fica como estava, porque não há como recontá-la. O resumo passa a ser gravado na versão 2, e daí em diante as horas se juntam como na 2.8.

## Verificação

**Execução manual (tarefas 4.2 e 5.3), em 2026-10-21,** no Xavier, só lendo, com pastas de dados vazias para a 2.8 (da `main`) e para a 2.9; o `git status --porcelain` igual antes e depois.

- **Primeira rodada:** a 2.8 deu 58 dias e 179,4 h, e a 2.9, 58 dias e 170,0 h. Mudaram 12 dias.
  - **Conversas, de 21/09 a 10/10, cerca de 4 h:** nesses dias, as mesmas conversas alternavam entre o Xavier e o Heimdall (05/10, por exemplo: 670 eventos no Heimdall e 346 no Xavier), e a 2.8 contava para o Xavier o tempo no Heimdall. É a correção do D1.
  - **Commits de 26/05, 02/06 e 15/10:** saíram 11 commits do próprio usuário, feitos com o e-mail `paulolima@uepa.br`, porque o `user.email` do Xavier é `paulosrl@gmail.com`. Achado: daí o `trilha.email` e o aviso (D3, tarefas do grupo 5), com a escolha do usuário. O `trilha.email` do Xavier foi gravado com esse e-mail, na configuração local do git, fora dos arquivos versionados.
- **Segunda rodada, com o `trilha.email`:** 58 dias e 175,4 h. 26/05 e 02/06 voltaram iguais aos da 2.8. Em 15/10, sai só o commit do Dependabot. O aviso cita só os 16 commits do Dependabot. A diferença para a 2.8, 4,0 h, é toda das conversas no Heimdall.
- **A página, no Chromium do Playwright, com 1200 e 400 px:**
  - sem erro no console, sem nenhuma requisição fora do arquivo e sem rolagem lateral;
  - a chave `"dias": [` uma vez só no arquivo;
  - nenhum "1 dias": a 2.8 escrevia "1 dias" duas vezes numa página de dois dias.
- **A semana a mais da mudança de horário não se reproduziu** num exemplo de Nova York (26/10 a 01/11/2026). Lá o horário muda às 02:00 de domingo, e a meia-noite do domingo não ganha a hora: a 2.8 e a 2.9 desenham uma semana. O defeito só aparece em fuso que muda o horário à meia-noite. A troca do `Math.ceil` pelo arredondamento não muda os outros casos.

## Respostas à revisão

### Revisão dos artefatos, antes do apply

Feita por um agente sem o contexto da sessão, em 2026-10-21. Os 11 pontos foram aplicados, com a escolha do usuário:

1. Grave: o D2 tirava das horas o worktree do próprio repositório. Aplicado: o `gitdir:` em `.git/worktrees/` conta para a raiz; cenário "Worktree do próprio repositório dentro da raiz".
2. Grave: o corte "fora" na sessão inteira deixava o subagente noutra pasta derrubar a conversa principal. Aplicado: o corte vale dentro do mesmo arquivo (D1); cenário "Subagente noutra pasta".
3. O resumo da 2.8 guarda as horas a mais, e a execução manual compararia o mesmo total. Aplicado: o Migration Plan diz como recomeçar, e a tarefa 4.2 roda com uma pasta de dados vazia.
4. Os requisitos novos contradiziam três do spec principal. Aplicado: os três viram MODIFIED, com os cenários novos dentro deles.
5. O teste da assinatura passava antes da correção. Aplicado: o commit é assinado com uma chave ssh que o git não sabe conferir.
6. A busca do D6 pegava o vizinho de nome parecido. Aplicado: o nome exato com o hash e a raiz conferida; cenário "Vizinho de nome parecido".
7. O `%aE` aplica o `.mailmap`, e o `user.email` não. Aplicado: `%ae`.
8. O D1 mudava o critério dos ignorados. Aplicado: o critério da 2.8 fica.
9. O teste da data com `Z` passa antes no Python 3.12. Aplicado: ele fica como guarda.
10. O commit das 00:00:00 emendado numa sessão do dia anterior continuava sumindo. Aplicado: o mínimo de 1 minuto vale para o dia com commit (D4).
11. As horas em número eram só refatoração, sem cenário, e arriscavam a igualdade dos números. Aplicado: saíram da change.

### Verify e code review, depois do apply

O `/opsx:verify` e o `/code-review 11`, cada um por um agente sem o contexto da sessão, em 2026-10-21. Nenhum crítico; os pontos, com a escolha do usuário:

| # | Origem | Achado | Decisão |
|---|---|---|---|
| 1 | review 1 | A linha copiada noutro arquivo da mesma conversa (conversa retomada) fazia o par cruzar arquivos e escapar do corte da saída. | Aplicado: a linha repetida é um evento só, dos dois arquivos, e o corte vale para o arquivo em comum (D1). Cenário "Conversa retomada noutro arquivo". O outro caso do review, um evento de subagente na raiz entre a saída e a volta da conversa principal, fica como está: o subagente trabalhava na raiz (risco já aceito no design). |
| 2 | review 2 | As horas a mais guardadas pela 2.8 ficariam no resumo para sempre. | Aplicado: o resumo da versão 1 é lido com as conversas que ainda existem recalculadas, e passa à versão 2 (Migration Plan). Requisito "Resumo da versão anterior". |
| 3 | verify 3, review 3 e 9 | O `--path-format=absolute` pede o git 2.31; num git mais antigo, o worktree da raiz deixaria de contar. | Aplicado: o `--git-common-dir` resolvido a partir da raiz, pelo `_git_texto` (D2). Sem teste de versão do git: o `test_tempo_worktree_da_raiz` continua guardando o caso. |
| 4 | verify 2, review 4 | Os testes de commit não isolavam a configuração do git da máquina. | Aplicado: o `_rodar` dos testes sempre põe `GIT_CONFIG_GLOBAL=/dev/null` e `GIT_CONFIG_NOSYSTEM=1`. |
| 5 | review 5 | O teste do subagente noutra pasta não exercitava a regra: o arquivo dele nem passava no primeiro filtro. | Aplicado: o arquivo do subagente ganha uma linha que cita o repositório. |
| 6 | review 6 | O e-mail com espaço era descartado, e o vazio entrava no aviso. | Aplicado: os campos separados pelo caractere nulo, e o e-mail vazio fora do aviso (D3). Teste `test_tempo_email_com_espaco_e_vazio`. |
| 7 | review 7 | O aviso dos e-mails sairia em toda execução, com todos os e-mails, num repositório com o Dependabot. | Aplicado: até três e-mails, "e mais N", sem os de robôs (D3). Cenário "Robô fora do aviso". |
| 8 | verify 4, review 8 | O JSON só protegia o `</`; um `<!--` no nome deixava a página em branco. | Aplicado: todo `<` vira `\u003c` (D5). Cenário "Nome que abre um comentário". |
| 9 | verify 1 | O proposal não citava o `trilha.email`. | Aplicado no proposal. |
| 10 | review 10 | Ler cada arquivo da raiz uma vez só; o plural de "dia" escrito à mão numa frase da página; a conferência do nome da raiz no `_aviso_de_outra_pasta`, que parece repetida. | Recusados. Uma passada só decodificaria as linhas de todo arquivo antes de saber se ele é da raiz, o que o primeiro filtro evita. Na frase "dia(s) com trabalho", o número fica em destaque, separado do texto, e o `pl` o repetiria. A conferência do nome cobre o resumo copiado ou renomeado à mão. |

**Execução manual depois das respostas (tarefa 6.8), em 2026-10-21,** no Xavier, só lendo:
- com uma pasta de dados vazia: `26/05/2026 a 21/10/2026: 58 dias, 176 h`, sem o aviso dos e-mails (só o Dependabot ficava fora);
- sobre uma cópia do resumo real da 2.8 (versão 1): o mesmo total, 176 h, e o resumo gravado na versão 2. O resumo real não foi tocado.
- O `git status` do Xavier mudou durante a rodada, mas não pelo comando: outra sessão trabalhava no Xavier ao mesmo tempo, com commits da change 18 e o `ANDAMENTO.md` alterado. O `test_tempo_nao_toca_o_repositorio` guarda que o comando não escreve no repositório.

