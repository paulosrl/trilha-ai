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

Na conversa, os eventos da raiz, de todos os arquivos dela, seguem em ordem de hora. O par seguido conta, com até 30 minutos, salvo quando os dois vêm do mesmo arquivo e esse arquivo tem um evento "fora" entre eles. Assim, um subagente que trabalha noutra pasta não corta a conversa principal, e a conversa principal que sai e volta não conta o tempo fora.

*Alternativa:* calcular os intervalos arquivo por arquivo e juntar só depois. Recusada: o subagente deixaria de preencher as pausas da conversa principal, o que a change 10 conta ("Arquivo de subagente apagado").

O arquivo vai para a lista dos ignorados quando não tem nenhum evento da raiz, como na 2.8, e não quando só não cita o caminho.

### D2. A raiz, o repositório aninhado e o worktree
Para cada `cwd` diferente dentro da raiz, o comando sobe as pastas do `cwd` até a raiz, sem ela, procurando um `.git`:
- uma pasta `.git` é outro repositório;
- um arquivo `.git` cujo `gitdir:` aponta para dentro de `<raiz>/.git/worktrees/` é um worktree da própria raiz, e conta para ela (o Claude Code cria os dele em `.claude/worktrees/`);
- outro arquivo `.git`, como o de um submódulo (`.git/modules/`), é outro repositório.

O resultado fica guardado por `cwd`, na execução. Uma pasta que já não existe não tem `.git` e conta para a raiz.

### D3. Os commits
`git log --branches --remotes --tags --no-show-signature --format=%H %ae %aI`. Usa o `%ae`, e não o `%aE`, porque o `user.email` não passa pelo `.mailmap`. A data passa pela mesma conversão das conversas, que aceita o `Z`. A linha que não tem os três campos, ou cuja data não se converte, é ignorada. Com o `user.email` do repositório (`git config user.email`), só contam os commits com esse e-mail de autor, sem diferença de maiúscula.

*Alternativa:* `--author`. Recusada porque ele casa por trecho, e um e-mail contido noutro passaria.

### D4. O dia com commit tem pelo menos 1 minuto
Depois das sessões e do corte por dia, o dia com commit que ficou com menos de 1 minuto estimado ganha o minuto que começa no primeiro commit dele. Isso cobre o commit das 00:00:00, sozinho ou emendado numa sessão do dia anterior.

### D5. A página
O `tempo.py` troca só os dois marcadores inteiros, `<title>__TITULO__</title>` e `<script id="dados" type="application/json">__DADOS__</script>`, uma vez cada. O título passa pelo `html.escape`, e o comentário do modelo deixa de citar os marcadores. No código da página:
- o plural segue o número ("1 dia", "2 dias");
- a contagem das semanas arredonda a diferença de dias antes de somar 1, o que tira a hora a mais da mudança de horário;
- sai a função `clock`, que nada usa.

### D6. O resumo de outra pasta
Sem resumo para o caminho atual, o comando procura os resumos de nome `<nome>-<8 hexadecimais>.json`, exato, e confere que o nome da `raiz` gravada é o deste repositório. Se um deles tem outra `raiz`, o aviso cita o arquivo e a raiz dele. O resumo ilegível nessa busca é ignorado, porque o aviso é só uma ajuda.

### D7. A versão
"Versão 2.9, de 2026-10-21." no comum e `2.9.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [O segundo passo decodifica as linhas de `cwd` fora da raiz, no arquivo que tem a raiz] → São poucas, porque a conversa costuma ficar numa pasta. O arquivo de outro repositório continua sem ser decodificado.
- [Quem faz commits com outro e-mail no mesmo repositório os perde da estimativa] → Aceito: o `user.email` do repositório é o do usuário que trabalha nele.
- [Um par de eventos de arquivos diferentes conta mesmo que os dois arquivos tenham saído da raiz entre eles] → Aceito: é raro, e o corte de 30 minutos limita o erro.
- [Os testes não rodam o código da página] → O plural, a semana a mais e a função removida se conferem na execução manual.

## Migration Plan

O resumo da 2.8 continua válido, mas guarda as horas que a 2.8 contou a mais: o tempo fora do repositório no meio de uma conversa e o de um repositório aninhado. Como as horas guardadas e as recalculadas se juntam, essas horas ficam nele. Para recomeçar do certo, mova o resumo (`~/.local/share/trilha-ai/tempo/<nome>-<hash>.json`) e rode de novo. As conversas que ainda existem são recontadas; as já apagadas, não.

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
