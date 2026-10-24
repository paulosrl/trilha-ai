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

**Depois das respostas à revisão, em 2026-10-24,** no mesmo projeto de teste, com o `verify.md` alterado de novo: o `kit.py atualizar --openspec` terminou com 0, o update rodou com a entrada do terminal fechada, o `verify.md` voltou ao que o OpenSpec gera, e o commit sugerido passou a ser "chore(metodo): os arquivos gerados pelo OpenSpec 1.15.0".

## Respostas à revisão

Do `/opsx:verify` (achados V1 a V6) e do `/code-review high 17` (achados R1 a R10), de 2026-10-24, rodados por um agente sem o contexto da sessão.

- **V1 (a saída do dry-run que falha não aparecia):** aplicado. Ela sai recuada antes da FALHA; o `test_atualizar_openspec_dry_run_com_erro_falha` confere a mensagem do OpenSpec na saída.
- **V2 (o filtro dos caminhos fora do projeto sem teste):** aplicado. O dry-run falso do `test_atualizar_openspec_recusa_o_update_que_apagaria` traz um `delete` no HOME e um absoluto, que não entram na FALHA.
- **V3 (os ramos da falha sem teste):** aplicado para o dry-run com erro e para o `npm` que falha (`test_atualizar_openspec_npm_com_erro_falha`).
- **V4 (o `surrogateescape`):** aplicado, no `_openspec`, como na conferência.
- **V5 (o D3 recusa até o que não está no índice do git):** recusado. Um arquivo fora do índice que o update apagasse não se recupera pelo git, o que é pior do que perder um versionado; a recusa vale para os dois.
- **V6, R8 (os tempos e o `subprocess.run` repetidos):** aplicados em parte. O `_openspec` chama o OpenSpec com o prazo, o ambiente e a entrada fechada, para o `--version` e o dry-run; o `_aviso_do_perfil` do `kit.py novo` fica como está, fora desta change.
- **R1 (a conferência manda voltar à versão do CI do projeto):** aplicado. O `atualizar` avisa, com ou sem a opção, quando o CI do projeto fixa outra versão que a do kit, com o arquivo e que a conferência cita a do projeto até a troca (requisito "Aviso do CI do projeto atrás do kit"). A conferência do método fica como está: ela é do projeto e roda também fora do `atualizar`.
- **R2 (uma pergunta do npm ou do OpenSpec travaria calada):** aplicado. O `_rodar` passa a fechar a entrada do terminal e aceita um prazo, de 600 segundos no `npm install` e no `openspec update`.
- **R3 (dois avisos de versão sem a opção):** recusado. Com o CI do projeto igual ao do kit, os dois dizem a mesma versão, e só o do `atualizar` cita a opção; com o CI atrás, o aviso do R1 explica a diferença.
- **R4 (o OpenSpec roda mesmo com a migração do `check.sh` que falha):** aplicado. Sem a migração, o `--openspec` não chama o `npm` nem o update (cenário "Migração do check.sh que falha").
- **R5 (os deletes fora do projeto passam calados):** aplicado como aviso, sem recusar (cenário "Apagados fora do projeto"): são arquivos de outras ferramentas, que o perfil da máquina governa.
- **R6 (outro `openspec` antes no PATH):** aplicado. Com o `npm` que termina bem e a versão igual a de antes, a FALHA cita o `openspec` do PATH e diz que outro vem antes dele.
- **R7 (as constantes copiadas da conferência):** aplicado como teste: o `test_atualizar_openspec_com_as_constantes_da_conferencia` compara o padrão da versão, o ambiente e o filtro dos caminhos. Importar o `confere_metodo.py` do `modelo/` amarraria a ferramenta do kit a um arquivo que é dos projetos.
- **R9 (o commit sugerido com "comum 2.16 → 2.16"):** aplicado. Com a opção e o comum na mesma versão, a sugestão é "chore(metodo): os arquivos gerados pelo OpenSpec X".
- **R10 (a recusa não diz como corrigir):** aplicado: "confira o perfil com openspec config list e ajuste-o com openspec config profile".
