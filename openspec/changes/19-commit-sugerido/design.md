# Design

## Context

Ver `proposal.md` (Why). Hoje o fim do `atualizar` escolhe a mensagem só pelo `--openspec` e pela versão: com a opção e o comum na mesma versão, "os arquivos gerados pelo OpenSpec X" (achado R9 da change 16, para não sugerir "comum 2.16 → 2.16"); senão, "cópia do kit Trilha AI, comum A → B". O `git status` do fim junta o que a cópia e o update mudaram.

## Goals / Non-Goals

**Goals:**
- A mensagem nomeia cada uma das duas fontes de mudança que houve.

**Non-Goals:**
- Separar o que vai em cada commit: a sugestão segue uma só.

## Decisions

### D1. O que a cópia mudou: o git status antes do update
O `atualizar` lê os caminhos do `git status` (um por arquivo, também os novos) logo antes de rodar o `openspec update`, depois da cópia, das travas, das regras e da página. Algum, a cópia mudou o projeto.

*Alternativa:* comparar o `git status` do fim com a lista do dry-run. Recusada: o mesmo arquivo poderia aparecer nas duas, e a leitura antes do update separa as duas fontes sem adivinhar.

### D2. O que o OpenSpec mudou: o que o commit leva dele
O `_preparar_o_openspec` passa a devolver os caminhos do projeto que o dry-run prevê mudar. No fim, com o `--openspec`, a parte do OpenSpec entra quando um caminho previsto está no `git status` final, ou quando o status final tem um caminho que a cópia não tinha mudado (só o update roda depois dela). Assim, a previsão que o update não cumpriu não cita o OpenSpec (achado R1 do code review), e o update que mudou além da previsão o cita (R2). Sem `preparado`, não há parte do OpenSpec (e, com `--openspec`, o `atualizar` termina com 1 antes da mensagem, pela migração do `check.sh` que falha); a parte só sai com o código 0, que exige o update sem falha.

*Alternativa:* só o plano do dry-run, a primeira versão desta change. Recusada pelo code review: o plano é feito antes da cópia e pode não bater com o que o update fez. *Alternativa:* só o `git status` de antes e de depois do update. Recusada: um arquivo que a cópia e o update mudassem não apareceria como mudança do update; o plano cobre esse caso.

### D3. A mensagem
As partes, nesta ordem: a da cópia, quando a versão muda ou a cópia mudou o projeto; a do OpenSpec, pela regra do D2. Unidas por ", e ". Sem parte nenhuma, mas com o projeto mudado (o que nenhum caminho conhecido produz), vale a da cópia, como hoje sem a opção. Com a versão do comum diferente da do kit, a cópia sempre muda o projeto (troca o próprio `trilha/CLAUDE-comum.md`), então a parte da versão fica coberta pela da cópia; com `--openspec`, a mensagem desse caso passa a citar também o OpenSpec quando o plano previu mudanças.

### D4. A regra do check.sh num lugar só
Uma função recebe o texto devolvido pelo `_check_migrado` (ou o `None`) e diz se a migração deu certo: o texto existe e não chama mais os `scripts/confere_*`. A previsão e a migração a usam.

## Risks / Trade-offs

- [Com `--openspec`, a reserva do D3 traz de volta "comum V → V" (o achado R9 da change 16), se algum caminho desconhecido mudar o projeto sem cópia nem plano] → Aceito: o `git status` impresso acima da sugestão mostra o que mudou.
- [Um arquivo que a cópia mudou, que o dry-run previu e que o update não mudou] → A mensagem citaria o OpenSpec sem mudança dele; a cópia não toca os arquivos que o OpenSpec gera (change 18, D1), então o caso não aparece, e o `git status` impresso logo acima mostra o que mudou de fato.

## Verificação

**Os testes antes do código (tarefa 1.1):** o `test_atualizar_openspec_commit_da_copia_e_do_openspec` e o `test_atualizar_openspec_commit_so_da_copia` falharam antes do código, com a mensagem antiga "os arquivos gerados pelo OpenSpec 1.15.0"; o `test_atualizar_openspec_commit_so_do_openspec` e o `test_atualizar_commit_sem_openspec` passaram antes, como previsto, e protegem o comportamento de antes.

**Execução manual (tarefa 3.2), em 2026-10-24,** com o OpenSpec 1.15.0 de verdade, no projeto descartável da change 18 (no scratchpad, com o `XDG_CONFIG_HOME` e o `HOME` nele), com a `trilha/verifica.sh` editada e a skill `openspec-propose` alterada, commitadas; o dry-run listava a troca da skill. O `kit.py atualizar --openspec` terminou com 0, o `git status` mostrou a skill e a `trilha/verifica.sh`, e a sugestão foi "commit sugerido: chore(metodo): cópia do kit Trilha AI, comum 2.18 → 2.18, e os arquivos gerados pelo OpenSpec 1.15.0".

**Depois das respostas ao verify e ao code review (tarefa 4.2), em 2026-10-24,** no mesmo projeto, de volta ao estado commitado: a mesma sugestão, com as duas partes, e o mesmo `git status`.

## Respostas à revisão

### Revisão dos artefatos, antes do apply

De 2026-10-24, por um agente sem o contexto da sessão. Todos aplicados.

- **A1 (o "sem o --openspec, nada muda" sem cenário nem teste):** aplicado. O cenário "Sem o --openspec" e o `test_atualizar_commit_sem_openspec`, que passa antes do código.
- **A2 (a versão que muda junto com o `--openspec`):** aplicado no D3: a versão diferente sempre faz a cópia mudar o projeto, e a mensagem desse caso passa a citar também o OpenSpec.
- **A3 (o D2 dizia que o update recebe o plano):** aplicado. O texto diz o que vale sem `preparado` e que a parte do OpenSpec exige o código 0.
- **A4 (V, X e "a versão do kit" sem definição):** aplicado, no requisito.
- **A5 (a tarefa 1.1 punha o update que muda a skill nos três testes):** aplicado: só nos dois primeiros.
- **A6 (o comando da 2.1 sem os testes da migração, que o D4 toca):** aplicado, com o `-k test_migra`.
- **A7 (o risco da reserva do D3 com `--openspec`):** aplicado, nos riscos.

### O verify e o code review

Do `/opsx:verify` (V1 e V2) e do `/code-review` da branch, no nível high (R1 a R6), de 2026-10-24, cada um por um agente sem o contexto da sessão. Nenhum achado crítico; todos aplicados.

- **R1 (a previsão do dry-run que o update não cumpriu citava o OpenSpec) e R2 (o update que mudou sem a previsão era atribuído à cópia, com "V → V"):** aplicados, com a regra nova do D2, pelo que o commit leva; os cenários "O dry-run previu, e o update não mudou" e "O update mudou sem o dry-run prever", e os testes `test_atualizar_openspec_commit_previsto_e_nao_feito` e `test_atualizar_openspec_commit_feito_sem_previsao`, que falharam antes da correção.
- **V1 e R3 (sem teste da versão do comum que muda):** aplicado. O `test_atualizar_openspec_commit_de_outra_versao`, com o comum do projeto na 2.17, confere "comum 2.17 → V, e os arquivos gerados pelo OpenSpec X"; passou antes, porque o código já fazia isso.
- **R4 (sem teste do filtro dos caminhos de fora do projeto na mensagem):** aplicado. O `test_atualizar_openspec_commit_sem_os_de_fora`, que passou antes e protege o filtro.
- **R5 (a docstring do `_migrado_por_inteiro` dizia "existe", e o texto vazio, sem check.sh, também passa):** aplicado.
- **V2 e R6 (a frase da cópia escrita duas vezes, e o filtro das mudanças válidas repetido):** aplicados, numa variável e numa lista única. A segunda leitura do CI do modelo pelo `_openspec_do_kit` fica: é uma leitura de um arquivo pequeno, e devolver a versão junto com os caminhos complicaria a função mais do que ajuda.
