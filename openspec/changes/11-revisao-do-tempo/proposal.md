# Proposal

## Why

Pedido do usuário, de 2026-10-21 ("ajuste tudo"), depois de duas revisões de código do `trilha/tempo.py` já na `main` (change 10, versão 2.8). Elas acharam defeitos que mudam as horas apuradas ou quebram o comando:
- uma linha do `git log` que ele não entende (a data em UTC com `Z` no Python 3.10, a assinatura gpg com `log.showSignature`) derruba a execução;
- os commits do Dependabot e de outras pessoas viram horas do usuário;
- o tempo em que a conversa saiu do repositório e voltou conta como trabalho nele;
- um repositório git dentro de outro tem as horas contadas nos dois;
- o commit às 00:00 em ponto faz o dia sumir;
- a página traz os dados duas vezes (uma num comentário) e põe o nome do repositório no título sem proteção.

A descrição curta foi aprovada pelo usuário, com o envio da branch liberado até o merge.

## What Changes

- Os commits:
  - a linha do `git log` que não se entende é ignorada, e a assinatura não entra na saída;
  - só contam os commits com o e-mail de autor do `user.email` do git; sem ele, todos;
  - a sessão de commits tem pelo menos 1 minuto.
- As conversas:
  - o intervalo entre um evento no repositório e outro fora dele não conta;
  - a conversa feita dentro de outro repositório git aninhado não conta, e a de um worktree do próprio repositório continua contando.
- A página:
  - os dados aparecem só no bloco de dados, e o nome vai ao título com os caracteres de HTML protegidos;
  - o singular ("1 dia");
  - sem a semana vazia a mais quando há mudança de horário;
  - sem a função que nada usa.
- O aviso do resumo deixado para trás quando o repositório muda de pasta.
- A versão passa a 2.9 e o plugin `sdd` a 2.9.0, com a data do dia.

**Fora desta change:**
- juntar o `_json_seguro` ao do `gerar_pagina_sdd.py`: os scripts rodam com `python3 -I`, que não põe a pasta do script no caminho de importação;
- pular também os arquivos do próprio repositório que não mudaram: recusado na change 10, pelo risco de errar horas;
- completar com os commits um dia de conversas apagadas antes da primeira execução: as duas fontes somariam horas duas vezes;
- o mesmo título sem proteção na página do `gerar_pagina_sdd.py`, que é outro comando;
- a cópia da 2.9 nos projetos.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `horas-de-trabalho`: os commits do usuário e a linha que não se entende, a sessão mínima, a conversa que passa por outra pasta, o repositório aninhado, a página com os dados uma vez e o aviso do repositório que mudou de pasta.

## Impact

- `modelo/trilha/tempo.py` e `modelo/trilha/pagina_tempo_modelo.html`.
- `testes/test_kit.py`: um teste por cenário novo.
- `modelo/trilha/CLAUDE-comum.md` (só a linha de versão) e `plugins/sdd/.claude-plugin/plugin.json`.
