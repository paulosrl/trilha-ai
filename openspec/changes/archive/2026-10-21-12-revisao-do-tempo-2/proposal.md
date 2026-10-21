# Proposal

## Why

Pedido do usuário, de 2026-10-21 ("ajuste"), depois do `/code-review` da `main` com a change 11 (versão 2.9). Ele achou 8 pontos no `trilha/tempo.py` e na página das horas; os que mudam o comportamento:
- o resumo da 2.8 guarda para sempre as horas a mais de uma conversa feita toda num repositório aninhado (achado 1);
- quem tem o `author.email` ou o `GIT_AUTHOR_EMAIL` perde os próprios commits da estimativa (achado 3);
- o aviso do repositório que mudou de pasta sai uma vez só, e as horas antigas ficam presas no outro resumo (achado 4);
- o aviso dos e-mails de fora repete a cada execução num repositório com colegas, e o único remédio que ele sugere contaria as horas deles (achado 5);
- a conversa de outro repositório que só cita este caminho é decodificada por inteiro a cada execução (achado 6).

A descrição curta foi aprovada pelo usuário.

## What Changes

- O resumo da versão 1 recalcula também a conversa só com eventos fora da raiz (a do repositório aninhado): as horas que a 2.8 guardou dela saem.
- Os e-mails do usuário: o `GIT_AUTHOR_EMAIL`, o `author.email` e o `user.email`, mais os do `trilha.email`; sem nenhum dos três, contam todos.
- O resumo de mesmo nome cuja raiz já não é um repositório git é juntado ao deste caminho, conversa por conversa, e renomeado para `.juntado`, com a página dele, sem ser apagado; o comando avisa. Quando a raiz dele ainda é um repositório, fica o aviso de hoje.
- Os e-mails do `trilha.outro` saem do aviso dos e-mails de fora, e o aviso ensina os dois comandos: `trilha.email` e `trilha.outro`.
- O arquivo que cita a raiz só é decodificado por inteiro depois que uma linha dele se mostra um evento da raiz.
- Limpezas sem mudança de comportamento (achados 7 e 8): o `_ler_commits` devolve os instantes e a contagem dos e-mails de fora, sem o argumento que ele alterava; na página, todo plural passa pela mesma função.
- A versão passa a 2.10 e o plugin `sdd` a 2.10.0, com a data do dia.

**Fora desta change:**
- as horas de um arquivo de subagente já apagado, na leitura do resumo da versão 1 (achado 2): recusado. O resumo da versão 1 não guarda de que arquivo veio cada intervalo, então não há como separar o que já foi apagado; e a 2.8 durou um dia, sem chegar a nenhum projeto;
- o resumo da versão 1 que uma execução da 2.9 já gravou como versão 2: não há como distingui-lo;
- os arquivos ignorados do resumo juntado, que não vêm junto;
- as horas a mais de um resumo juntado da versão 1: as conversas dele não se recalculam, porque são da raiz antiga, e a 2.8 durou um dia;
- a cópia da 2.10 nos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `horas-de-trabalho`: os e-mails de autor do git, o `trilha.outro` no aviso, o resumo de outra pasta juntado, a conversa do repositório aninhado no resumo da versão 1 e a leitura do arquivo que só cita a raiz.

## Impact

- `modelo/trilha/tempo.py` e `modelo/trilha/pagina_tempo_modelo.html`.
- `testes/test_kit.py`: um teste por cenário novo; o `_rodar` dos testes deixa de herdar o `GIT_AUTHOR_EMAIL` da máquina, e o teste do `_ler_commits` segue a nova assinatura.
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão) e `plugins/sdd/.claude-plugin/plugin.json`.
