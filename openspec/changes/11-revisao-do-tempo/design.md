# Design

## Context

Ver `proposal.md` (Why). O `trilha/tempo.py` da 2.8 lê as linhas de conversa que contêm o caminho da raiz, descarta as de `cwd` fora dela antes de medir os intervalos, lê os commits com `git log --format=%H %aI` e converte a data sem proteção, e monta a página trocando `__TITULO__` e `__DADOS__` em todo lugar do modelo, inclusive no comentário dele. As horas vão de número a texto ISO e de volta várias vezes na mesma execução.

## Goals / Non-Goals

**Goals:**
- As horas de um dia são só as do repositório, do usuário dele.
- Nenhuma linha estranha do git ou do resumo derruba o comando.

**Non-Goals:** os três itens recusados no `proposal.md`.

## Decisions

### D1. Os eventos fora do repositório
A leitura de um arquivo de conversa passa a ter dois passos. O primeiro procura o caminho da raiz no texto e para no primeiro achado; o arquivo sem ele vai para a lista dos ignorados, como na 2.8. No arquivo com ele, o segundo passo decodifica toda linha que tem `"cwd"`. O evento com `cwd` na raiz é "pedido" ou "ia", como antes; o com `cwd` fora dela, ou dentro de um repositório aninhado (D2), é "fora". O intervalo só conta quando os dois eventos são da raiz. *Alternativa:* guardar o `cwd` de cada evento e decidir depois. Recusada: dá no mesmo com mais memória.

### D2. O repositório aninhado
Para cada `cwd` diferente dentro da raiz, o comando sobe as pastas do `cwd` até a raiz, sem ela, procurando um `.git` (pasta ou arquivo, que é o caso de um worktree ou submódulo). Achou, o `cwd` é de outro repositório. O resultado fica guardado por `cwd`, na execução. Uma pasta que já não existe não tem `.git` e conta para a raiz.

### D3. Os commits
`git log --branches --remotes --tags --no-show-signature --format=%H %aE %aI`. A data passa pela mesma conversão das conversas, que aceita o `Z`; a linha que não tem os três campos ou cuja data não se converte é ignorada. Com o `user.email` do repositório (`git config user.email`), só contam os commits com esse e-mail de autor, sem diferença de maiúscula. *Alternativa:* `--author`. Recusada porque ele casa por trecho do nome ou do e-mail, e um e-mail contido noutro passaria.

### D4. A sessão mínima
Depois do corte na meia-noite do começo, a sessão termina no mais tarde entre o último commit e 1 minuto depois do começo.

### D5. A página
O `tempo.py` troca só os dois marcadores inteiros, `<title>__TITULO__</title>` e `<script id="dados" type="application/json">__DADOS__</script>`, uma vez cada, e o título passa pelo `html.escape`. O comentário do modelo deixa de citar os marcadores. No código da página: o plural pelo número ("1 dia", "2 dias"); a contagem das semanas arredonda a diferença de dias antes de somar 1, o que tira a hora a mais da mudança de horário; e sai a função `clock`, que nada usa.

### D6. O resumo de outra pasta
Sem resumo para o caminho atual, o comando lê os outros resumos da pasta com o mesmo nome de repositório (`<nome>-*.json`). Se um deles tem outra `raiz`, o aviso cita o arquivo e a raiz dele, e diz que, se o repositório mudou de pasta, as horas guardadas ficaram nele. O resumo ilegível nessa busca é ignorado: o aviso é só uma ajuda.

### D7. As horas em número
Os intervalos ficam como pares de segundos desde a época, com o tipo, do momento da leitura até a gravação; só o resumo os grava em ISO 8601 UTC. O resumo lido é convertido uma vez, na validação.

### D8. A versão
"Versão 2.9, de 2026-10-21." no comum e `2.9.0` no plugin, antes de qualquer outro arquivo de `modelo/` mudar.

## Risks / Trade-offs

- [O segundo passo decodifica as linhas de `cwd` fora da raiz no arquivo do repositório] → São poucas: a conversa costuma ficar numa pasta. O arquivo de outro repositório continua sem ser decodificado.
- [Quem faz commits com outro e-mail no mesmo repositório os perde da estimativa] → Aceito: o `user.email` do repositório é o do usuário que trabalha nele; o método da página diz isso.
- [Os testes não rodam o código da página] → O plural, a semana a mais e a função removida se conferem na execução manual, com a captura de tela.

## Migration Plan

Nada a migrar: o resumo da 2.8 continua válido.
