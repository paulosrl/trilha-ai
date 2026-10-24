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
O `_preparar_o_openspec` passa a devolver se o dry-run previu alguma mudança dentro do projeto (qualquer ação num caminho do projeto). O update roda logo depois da cópia com esse plano, e só termina com o código 0 se não falhar.

*Alternativa:* comparar o `git status` de antes e de depois do update. Recusada: um arquivo que a cópia e o update mudassem não mudaria a linha do status.

### D3. A mensagem
As partes, nesta ordem: a da cópia, quando a versão muda ou a cópia mudou o projeto; a do OpenSpec, quando o plano previu mudanças. Unidas por ", e ". Sem parte nenhuma, mas com o projeto mudado (o que nenhum caminho conhecido produz), vale a da cópia, como hoje sem a opção.

### D4. A regra do check.sh num lugar só
Uma função recebe o texto devolvido pelo `_check_migrado` (ou o `None`) e diz se a migração deu certo: o texto existe e não chama mais os `scripts/confere_*`. A previsão e a migração a usam.

## Risks / Trade-offs

- [O dry-run previu mudanças que o update, por algum motivo, não fez] → A mensagem citaria o OpenSpec sem arquivo dele no commit; o `git status` impresso logo acima mostra o que mudou de fato.
