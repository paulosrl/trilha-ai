# Design

## Context

Ver `proposal.md` (Why). O `kit.py atualizar` copia a `trilha/`, cria o que falta do modelo, avisa a parte fixa e roda a conferência das regras e a do método, que avisa a versão do OpenSpec diferente da do CI do projeto e o que o `openspec update` mudaria (change 14). A versão que o kit espera está no CI do modelo (`modelo/.github/workflows/verificacao.yml`, `npm install -g @fission-ai/openspec@X`), e um teste do kit cobra que ela seja um número.

O `openspec update` da 1.15.0, num terminal, pergunta se instala a versão nova antes de rodar ("Upgrade to v1.15.0 now?"), e a variável `OPENSPEC_NO_UPDATE_CHECK=1` desliga essa consulta. Com um perfil da máquina que não traz o que o projeto versiona, ele apaga os arquivos gerados que sobram.

## Goals / Non-Goals

**Goals:**
- Um comando só põe a máquina e o projeto na versão do OpenSpec do kit, sem o risco de o perfil errado apagar o que o projeto versiona.

**Non-Goals:**
- Instalar o OpenSpec por outro meio que não o `npm`, ou mudar o perfil.

## Decisions

### D1. A versão alvo é a do CI do modelo do kit
O alvo é o `@fission-ai/openspec@X` do `modelo/.github/workflows/verificacao.yml` do kit, lido pelo mesmo padrão do `PIN_DO_OPENSPEC` da conferência. O CI do projeto pode estar atrás (é parte fixa, que o `atualizar` só avisa); o kit é a versão para a qual o projeto está sendo atualizado.

*Alternativa:* a versão do CI do projeto. Recusada: ela é a de antes da atualização.

### D2. A ordem
A parte do OpenSpec roda depois da cópia e dos avisos da parte fixa e antes das conferências, para elas já verem o OpenSpec novo: (1) o `openspec --version`; (2) o `npm install -g @fission-ai/openspec@X`, se a versão for outra ou faltar, e o `openspec --version` de novo, que tem de responder X; (3) o `openspec update --dry-run --json` na pasta; (4) o `openspec update` na pasta. A saída de cada um aparece recuada, como a das conferências (`_rodar`). Os comandos do OpenSpec rodam com `OPENSPEC_NO_UPDATE_CHECK=1` e `OPENSPEC_TELEMETRY=0`, o que também tira a pergunta do update.

### D3. O dry-run que apagaria
Se o dry-run listar algum caminho do projeto com `action: "delete"`, o update não roda: a falha cita os arquivos e o `openspec config list`, porque o caso típico é o perfil da máquina sem o verify, ou só com comandos. Os caminhos fora do projeto (com `~` ou absolutos) não contam, como na conferência. O dry-run que falha, ou cuja saída não é o JSON dele, conta como falha (D4): sem ele não se sabe o que o update faria.

### D4. A falha
Qualquer passo que falha para os seguintes e termina com 1, com "FALHA: ..." dizendo o comando, sem o "commit sugerido". As conferências ainda rodam, para mostrar o resto. O que o kit copiou fica, como na falha da conferência hoje.

### D5. O aviso sem a opção
Sem `--openspec`, o `atualizar` pergunta só o `openspec --version`; com a versão diferente da do kit, avisa com as duas e a opção. Sem o `openspec` no PATH, não avisa: a conferência do método e o README já cobrem a instalação.

## Risks / Trade-offs

- [A instalação global muda a máquina inteira, e outros projetos dela ficam na versão nova] → Só com a opção, que é a escolha do usuário; a conferência de cada outro projeto avisa a versão diferente da do CI dele.
- [O `npm install -g` pede permissão de administrador em algumas máquinas] → A falha mostra a saída do `npm` e o comando, para o usuário rodá-lo do jeito da máquina dele.
- [O dry-run evita o pior caso, mas não o update que troca arquivos] → Trocar é o que o update faz; o `git status` do fim mostra cada arquivo, e nada é commitado.

## Verificação

**Os testes antes do código (tarefa 1.1):** seis dos oito falharam antes do código. Os dois que passaram, `test_atualizar_sem_a_opcao_nao_mexe_no_openspec` e `test_atualizar_versao_igual_sem_aviso_da_opcao`, conferem o que não acontece (nem `npm`, nem update, nem o aviso), e o código de antes nunca fazia nada disso.

**Execução manual (tarefa 3.2), em 2026-10-24,** com o OpenSpec 1.15.0, num projeto de teste feito pelo `kit.py novo` e inicializado com `openspec init --tools claude`, com o `verify.md` alterado e commitado:
- o `kit.py atualizar --openspec` terminou com 0, sem chamar o `npm` (a máquina já estava na 1.15.0), rodou o `openspec update`, e o `verify.md` voltou ao que o OpenSpec gera (o `git status` o mostrou, e o commit sugerido apareceu);
- com o PATH sem o `npm` e um `openspec` falso que responde 1.14.1, terminou com 1: "npm: No such file or directory" e "FALHA: o OpenSpec da máquina não ficou na 1.15.0: rode npm install -g @fission-ai/openspec@1.15.0", sem o commit sugerido;
- no mesmo PATH, sem a opção, avisou "o OpenSpec da máquina está na 1.14.1 e o kit usa a 1.15.0: rode de novo com --openspec".
