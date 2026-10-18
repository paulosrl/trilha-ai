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

Alternativa descartada: rodá-lo com `bash .githooks/pre-push`. Funcionaria só para script de shell e esconderia a permissão perdida.

**3. O aviso da migração deixa de citar o `pre-push`.** No `_migrar`, o `pre-push` sai da lista dos hooks que "não rodam mais". O texto do aviso para os outros fica como está. O `.githooks/` continua sendo apagado só quando fica vazio.

**4. A conferência das regras não muda.** O arquivo novo de `modelo/trilha/` entra sozinho na comparação com o kit e na conferência da permissão de execução, que valem para todo arquivo da pasta.

**5. O texto e a versão.** No item "As travas do kit não se contornam" do comum entra a meia frase: o hook de envio próprio do projeto, quando existe, fica em `.githooks/pre-push` e roda pelo `trilha/hooks/pre-push`. A versão do comum vai a 2.6, e o plugin a 2.6.0, antes de qualquer arquivo de `modelo/` mudar: o `test_kit_sem_mudanca_depois_da_tag` reprova a mudança em `modelo/` com o comum ainda na 2.5, que já tem a tag, e cada parada do apply vai com a suíte verde. O comum hoje tem 15.901 bytes, e o limite é de 16 KB (16.384); a frase cabe. Se alguma lista da pasta `trilha/` no `README.md` citar os hooks, ela ganha o `pre-push`.

## Risks / Trade-offs

- [O hook próprio confia na pasta de trabalho de quem o chama] → O git roda os hooks na raiz do repositório, e o repasse também vai a ela antes do `exec`; o hook próprio vê a mesma pasta de antes.
- [O projeto em 2.x que já tem um `.githooks/pre-push` esquecido passa a rodá-lo no envio] → Hoje nenhum dos três projetos está nesse caso: o HubIA não tem `.githooks/`, e o Heimdall e o Xavier ainda estão no layout antigo. A cópia da 2.6 vai a cada projeto sob ordem do usuário, que confere o envio.
- [Um envio com `--no-verify` pula o repasse, como pularia o hook próprio] → O `guarda.py` já barra o `--no-verify` e as abreviações dele no Claude Code.

## Migration Plan

Os projetos recebem o hook com a cópia da 2.6, pelo `kit.py atualizar`, sob ordem do usuário. Para voltar atrás, o `git revert` do commit da cópia no projeto. O kit na 2.5 não serve para isso: o `atualizar` recusa o projeto mais novo que o kit, que ele rebaixaria.

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
