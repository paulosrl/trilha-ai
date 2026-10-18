# Design

## Context

O `kit.py` copia para o projeto todo arquivo versionado de `modelo/trilha/`, com a permissão dele (`shutil.copy2`), e a conferência das regras já reprova o arquivo de `trilha/` diferente do kit ou que perdeu a permissão de execução. A `trilha/hooks/` só tem o `pre-commit`, ligado pelo `core.hooksPath`, que o `guarda.py` impede de trocar. Na migração do layout antigo, o `_migrar` apaga o `.githooks/pre-commit` e avisa, para cada arquivo que sobra em `.githooks/`, que ele não roda mais. Motivação: ver `proposal.md`, em "Why".

## Goals / Non-Goals

**Goals:**
- O envio no projeto migrado roda a mesma verificação de antes da migração, com o mesmo resultado.
- No projeto sem hook próprio, o envio fica como hoje.

**Non-Goals:**
- Um lugar configurável para o hook próprio: o caminho é fixo, `.githooks/pre-push`, o do layout antigo.
- Uma verificação do kit no envio: o `trilha/hooks/pre-push` só repassa ao hook do projeto.

## Decisions

**1. O hook novo é um repasse.** O `trilha/hooks/pre-push` é um script de `bash`, como o `pre-commit`:
- vai à raiz do repositório (`git rev-parse --show-toplevel`);
- sem o `.githooks/pre-push`, nem como arquivo nem como link simbólico (`[ -e ]` e `[ -L ]` falsos), sai com 0;
- com ele executável, passa a vez a ele com `exec .githooks/pre-push "$@"`.

O `exec` troca o processo pelo hook próprio. Assim a entrada (as linhas das referências que o git manda) chega a ele inteira, e o código de saída dele é o do envio, sem cópia nem tradução.

Alternativa descartada: rodar o hook próprio como subprocesso e repassar o código. Dá o mesmo resultado com mais código, e a entrada teria de ser repassada por conta própria.

**2. O hook próprio que não pode rodar recusa o envio.** Com um hook dele que não é executável, o git só avisa (o `hint` do `advice.ignoredHook`) e deixa o envio seguir. Aqui o hook próprio existe porque o projeto quer a verificação; seguir sem ele seria o desligamento que esta change evita. Por isso o envio é recusado em dois casos, com uma mensagem que cita o arquivo:
- o `.githooks/pre-push` sem a permissão de execução, com o `chmod +x` na mensagem;
- o link simbólico quebrado: o `[ -e ]` dá falso nele, e só o `[ -L ]` o acha; sem isso ele contaria como "não existe" e o envio seguiria.
- o repasse que volta a si mesmo (o `.githooks/pre-push` como link para o `trilha/hooks/pre-push`, ou um hook próprio que chama o repasse): antes do `exec`, o repasse grava a raiz do repositório na variável `TRILHA_PRE_PUSH`; se ela já traz a mesma raiz quando ele começa, recusa em vez de rodar sem fim. A marca é pela raiz, e não um "já passei" qualquer, para que um hook próprio que envie outro repositório não seja barrado. Alternativa descartada: comparar o caminho real dos dois arquivos, que não pega o hook próprio que chama o repasse.

Alternativa descartada: rodá-lo com `bash .githooks/pre-push`. Funcionaria só para script de shell e esconderia a permissão perdida.

**3. O aviso da migração deixa de citar o `pre-push` que roda.** No `_migrar`, o `pre-push` sai da lista dos hooks que "não rodam mais". Quando ele está sem a permissão de execução ou é um link quebrado, a migração avisa que o envio será recusado até ele ser corrigido: sem isso, a saída ficaria muda e só o primeiro envio mostraria o problema. O texto do aviso para os outros fica como está. O `.githooks/` continua sendo apagado só quando fica vazio.

**4. A conferência das regras não muda.** O arquivo novo de `modelo/trilha/` entra sozinho na comparação com o kit e na conferência da permissão de execução, que valem para todo arquivo da pasta.

**5. O texto e a versão.** No item "As travas do kit não se contornam" do comum entra a meia frase: o hook de envio próprio do projeto, quando existe, fica em `.githooks/pre-push` e roda pelo `trilha/hooks/pre-push`. A versão do comum vai a 2.6, e o plugin a 2.6.0, antes de qualquer arquivo de `modelo/` mudar: o `test_kit_sem_mudanca_depois_da_tag` reprova a mudança em `modelo/` com o comum ainda na 2.5, que já tem a tag, e cada parada do apply vai com a suíte verde. O comum hoje tem 15.901 bytes, e o limite é de 16 KB (16.384); a frase cabe. Se alguma lista da pasta `trilha/` no `README.md` citar os hooks, ela ganha o `pre-push`.

## Risks / Trade-offs

- [O hook próprio confia na pasta de trabalho de quem o chama] → O git roda os hooks na raiz do repositório, e o repasse também vai a ela antes do `exec`; o hook próprio vê a mesma pasta de antes.
- [O projeto em 2.x que já tem um `.githooks/pre-push` esquecido passa a rodá-lo no envio] → Hoje nenhum dos três projetos está nesse caso: o HubIA não tem `.githooks/`, e o Heimdall e o Xavier ainda estão no layout antigo. A cópia da 2.6 vai a cada projeto sob ordem do usuário, que confere o envio.
- [Um envio com `--no-verify` pula o repasse, como pularia o hook próprio] → O `guarda.py` já barra o `--no-verify` e as abreviações dele no Claude Code.

## Migration Plan

Os projetos recebem o hook com a cópia da 2.6, pelo `kit.py atualizar`, sob ordem do usuário. Para voltar atrás, o `git revert` do commit da cópia no projeto. O kit na 2.5 não serve para isso: o `atualizar` recusa o projeto mais novo que o kit, que ele rebaixaria.

## Verificação

| O quê | Comando | Resultado |
|---|---|---|
| Suíte do kit | `python3 -m unittest discover -s testes` | 208 testes, OK, código 0 |
| Ruff | `uvx ruff@0.17.0 check --isolated --line-length 100 modelo/trilha/ ferramentas/` e o mesmo com `format --check` | "All checks passed!" e "7 files already formatted", código 0 nos dois |
| Hook no git | `git ls-files -s modelo/trilha/hooks` | `100755` no `pre-commit` e no `pre-push` |
| Tamanho do comum | `wc -c modelo/trilha/CLAUDE-comum.md` | 16.018 bytes, abaixo dos 16.384 |

**Execução manual (tarefa 4.2), em 2026-10-18,** num clone descartável do Heimdall (`master` em `b2d28f9`, comum 1.30), com um remoto `git init --bare` local e o `.env` do repositório real, que fica fora do git e falta a um teste pareado:

1. `python3 ferramentas/kit.py atualizar <clone>`, da branch: código 0. A saída não cita o `.githooks/pre-push`; o `.githooks/` ficou só com ele, e o `core.hooksPath` passou a `trilha/hooks`.
2. Envio com a cópia sem commit: o `trilha/hooks/pre-push` rodou o hook do Heimdall (encoding, `openspec validate --specs` e o `local-011`), que recusou o envio por dois testes que leem o índice do git (`teste-modos.sh` e `teste-referencias.sh`, pelos arquivos antigos ainda no índice); o remoto ficou sem o commit. É o caminho da recusa.
3. A cópia num commit, como manda o plano: o `referencias.py` do Heimdall acusou as oito citações que o plano previu; com a marca `<!-- ref-externa -->` nelas e o link do `docs/README.md` corrigido, num segundo commit, o envio passou: as três etapas do hook, 22 testes pareados `ok`, código 0, e o `master` do remoto igual ao `HEAD` do clone (`1ffc035`). É o caminho verde.

O clone foi apagado depois.

**Depois das respostas à revisão (tarefas 5.7 e 5.8), em 2026-10-18:**

- Suíte do kit: 210 testes, OK, código 0; o ruff, `check` e `format --check`, com código 0.
- Num projeto feito pelo `kit.py novo`, com o `.githooks/pre-push` como link para `../trilha/hooks/pre-push`: o `git push` a um remoto local saiu com 1 em menos de um segundo, com "envio recusado: .githooks/pre-push leva de volta ao trilha/hooks/pre-push, que rodaria sem fim", e o remoto ficou vazio.
- Num clone descartável do Heimdall, com a permissão de execução do `.githooks/pre-push` tirada num commit (feito como os testes fazem, sem a trava, que o clone ainda não tinha): o `kit.py atualizar` saiu com 0 e avisou "aviso: .githooks/pre-push está sem a permissão de execução; o envio será recusado até ele ser corrigido (chmod +x .githooks/pre-push)"; o envio seguinte foi recusado com "envio recusado: .githooks/pre-push está sem a permissão de execução; rode chmod +x .githooks/pre-push", e o remoto ficou vazio. Uma primeira tentativa, com o `chmod` sem commit, não valeu: o `atualizar` recusa o projeto com mudança por commitar.

Os dois projetos de ensaio foram apagados depois.

## Respostas à revisão

### Revisão dos artefatos, antes do apply

Feita por um agente sem o contexto da sessão. Nenhum achado grave; os sete, aplicados pelo `/opsx:update`, com a escolha do usuário:

1. A suíte ficaria vermelha entre a mudança em `modelo/` e a versão nova (o `test_kit_sem_mudanca_depois_da_tag`): aplicado, a versão sobe na tarefa 0 (decisão 5).
2. O "voltar atrás" pela cópia da 2.5 não funciona, porque o `atualizar` recusa rebaixar: aplicado, a volta é o `git revert` (Migration Plan).
3. O código de saída repassado não se prova pelo `git push`, que sai com 1 qualquer que seja o código: aplicado, o cenário "Código de saída e entrada repassados" e a tarefa 1.3.
4. O git não pula em silêncio o hook não executável, ele avisa e segue: aplicado, no requisito e na decisão 2.
5. O link simbólico quebrado contaria como "não existe": aplicado, o cenário "Link simbólico quebrado", a decisão 2 e a tarefa 1.6.
6. O hook novo precisa entrar no git antes dos testes, porque o `kit.py novo` copia o que o git lista: aplicado, na tarefa 1.7.
7. O envio dos testes dependeria da configuração do git da máquina: aplicado, o destino explícito na nota das tarefas.

### Verify, depois do apply

Feito por um agente sem o contexto da sessão: pronta para o archive, sem crítico nem aviso. Uma sugestão:

1. O `assertNotIn("pre-push", …)` do `test_migracao_preserva_o_pre_push_sem_aviso` reprovaria qualquer saída que citasse o hook novo: aplicado, o teste confere só a frase do aviso (é o item 5 do code review, abaixo).

### Code review do PR #8

Feito por um agente sem o contexto da sessão, pela skill `code-review`, sem comentários no PR. Nenhum achado grave; os cinco, aplicados com a escolha do usuário:

1. Médio: a migração ficava muda com o `.githooks/pre-push` sem a permissão de execução ou como link quebrado, e só o primeiro envio mostraria o problema: aplicado, o cenário "Hook de envio do projeto que não pode rodar" e a decisão 3.
2. Leve: o teste da migração usava um hook sem a permissão de execução, e nenhum teste automático provava que o envio do projeto migrado chega ao hook dele: aplicado, o teste dá o `chmod` e faz um `git push` depois da migração.
3. Leve: o repasse que volta a si mesmo rodaria sem fim: aplicado, o cenário "Repasse que volta a si mesmo" e a marca `TRILHA_PRE_PUSH` (decisão 2).
4. Leve: o caminho do arquivo de registro entrava sem aspas no script gerado pelos testes: aplicado, com o `shlex.quote`.
5. Leve: a conferência ampla demais do item do verify: aplicado.

O agente deixou fora, por não terem efeito, quatro pontos da skill, e a recusa fica: a pasta no lugar do hook (o envio já é recusado, só a mensagem é a do bash); generalizar o repasse para todos os hooks (contraria a escolha do que fica fora, no `proposal.md`); a configuração global do git nos testes (o resto da suíte também não a isola, e o destino explícito já tira a dependência que importa); o gerador dentro do `for` no `_migrar` (estilo).
