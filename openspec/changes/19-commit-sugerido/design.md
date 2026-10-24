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
O `atualizar` lê o `git status --short` logo antes de rodar o `openspec update`, depois da cópia, das travas, das regras e da página. Não vazio, a cópia mudou o projeto.

*Alternativa:* comparar o `git status` do fim com a lista do dry-run. Recusada: o mesmo arquivo poderia aparecer nas duas, e a leitura antes do update separa as duas fontes sem adivinhar.

### D2. O que o OpenSpec mudou: o plano do dry-run
O `_preparar_o_openspec` passa a devolver se o dry-run previu alguma mudança dentro do projeto (qualquer ação num caminho do projeto). Sem `preparado`, não há parte do OpenSpec (e, com `--openspec`, o `atualizar` termina com 1 antes da mensagem, pela migração do `check.sh` que falha); a parte só sai com o código 0, que exige o update sem falha.

*Alternativa:* comparar o `git status` de antes e de depois do update. Recusada: um arquivo que a cópia e o update mudassem não mudaria a linha do status.

### D3. A mensagem
As partes, nesta ordem: a da cópia, quando a versão muda ou a cópia mudou o projeto; a do OpenSpec, quando o plano previu mudanças. Unidas por ", e ". Sem parte nenhuma, mas com o projeto mudado (o que nenhum caminho conhecido produz), vale a da cópia, como hoje sem a opção. Com a versão do comum diferente da do kit, a cópia sempre muda o projeto (troca o próprio `trilha/CLAUDE-comum.md`), então a parte da versão fica coberta pela da cópia; com `--openspec`, a mensagem desse caso passa a citar também o OpenSpec quando o plano previu mudanças.

### D4. A regra do check.sh num lugar só
Uma função recebe o texto devolvido pelo `_check_migrado` (ou o `None`) e diz se a migração deu certo: o texto existe e não chama mais os `scripts/confere_*`. A previsão e a migração a usam.

## Risks / Trade-offs

- [Com `--openspec`, a reserva do D3 traz de volta "comum V → V" (o achado R9 da change 16), se algum caminho desconhecido mudar o projeto sem cópia nem plano] → Aceito: o `git status` impresso acima da sugestão mostra o que mudou.
- [O dry-run previu mudanças que o update, por algum motivo, não fez] → A mensagem citaria o OpenSpec sem arquivo dele no commit; o `git status` impresso logo acima mostra o que mudou de fato.

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
