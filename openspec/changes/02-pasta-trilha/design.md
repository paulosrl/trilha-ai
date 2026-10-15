# Design

## Context

Hoje o kit guarda o molde em `modelo/` (desde a 1.35, sem mudar o que o projeto recebe): `modelo/CLAUDE-comum.md`, `modelo/scripts/` (os verificadores, a trava, o gerador e o modelo da página, e o `check.sh`, que é do projeto) e `modelo/.githooks/pre-commit`. O `kit.py` copia `SEM_MUDAR` arquivo a arquivo e lê as versões antigas do kit por mais de um caminho (`_caminhos`). Os cinco projetos reais estão na 1.30, com o mesmo bloco fixo no `check.sh`: `FONTE=…`, o `if … fi` do `confere_regras.py` e a chamada do `confere_metodo.py` com `--vizinho` em linha continuada; alguns têm hooks próprios em `.githooks/` (o heimdall tem um `pre-push`). A motivação está em proposal.md.

## Goals / Non-Goals

**Goals:**
- Uma pasta só do método por projeto, conferida inteira e trocada inteira na atualização.
- A parte fixa da verificação num script do método, igual em todo projeto.
- A migração do projeto antigo sem trabalho à mão no caso comum.

**Non-Goals:**
- Mexer na parte da stack do `check.sh`, do CI, do Dependabot ou do `.gitignore`, que é do projeto.
- Tirar o `openspec validate --specs` que alguns projetos têm na parte da stack: o projeto decide (a migração avisa que o `verifica.sh` já valida).
- Migrar os projetos reais nesta change.

## Decisions

**1. `trilha/` plana, com `hooks/`.** Os scripts ficam direto em `trilha/` (`trilha/confere_regras.py`, não `trilha/scripts/`) e a trava do commit em `trilha/hooks/pre-commit`, para o `core.hooksPath` apontar só para ela. Os scripts acham a raiz do projeto por `Path(__file__).parent.parent`, como hoje, porque continuam um nível abaixo dela. Alternativa: `.trilha/` oculta — descartada porque o usuário precisa ver o que é do método.

**2. `SEM_MUDAR` lido da pasta.** A lista do que se copia sem mudar passa a ser o conteúdo de `modelo/trilha/`, e não uma tupla à mão: arquivo novo no método entra sozinho em toda atualização, e a dispensa de change do comum pode citar "a pasta `trilha/`". A atualização apaga de `trilha/` o que o kit não tem mais.

**3. A conferência de cópia compara pastas.** O `--fonte` continua recebendo a pasta do kit (o `check.sh` dos projetos já passa `../trilha-ai`), e a conferência compara `trilha/` com `<kit>/modelo/trilha/` pela lista de arquivos e pelo conteúdo. O atalho `CLAUDE-comum.md` da raiz do kit sai: projeto ainda não migrado que o compare reprova com "a fonte … não existe", e a saída é o `kit.py atualizar`.

**4. `verifica.sh` com o `openspec validate`.** O `openspec validate --all --no-interactive` sai com 0 num projeto sem specs (conferido na 1.14.1), então roda sempre que o comando existe; sem ele, avisa. No CI o OpenSpec já é instalado antes do `check.sh`, e o passo próprio do validate sai do modelo do CI. Os argumentos do `verifica.sh` vão inteiros ao `confere_metodo.py`.

**5. Migração por texto exato.** A troca da parte fixa do `check.sh` só acontece quando o bloco `FONTE=…`/`fi` do kit está lá, igual: ele sai, e `python3 -I scripts/confere_metodo.py` vira `bash trilha/verifica.sh` na mesma linha, o que preserva os argumentos e a barra de continuação. Fora disso, o arquivo não muda e a ferramenta imprime a linha a pôr. O aviso da parte fixa (`_avisar_parte_fixa`) passa a aceitar a linha do kit como começo de uma linha do projeto, porque a chamada migrada ganha os `--vizinho`. A importação do `CLAUDE.md` troca a linha `@CLAUDE-comum.md` inteira; o hook do Claude Code troca, no `.claude/settings.json`, a entrada que cita `scripts/guarda.py` pela do modelo, sem duplicar.

**6. Leitura das versões antigas.** `_caminhos` passa a saber os três lugares do comum e dos demais arquivos ao longo do tempo (a raiz até a 1.34, `modelo/` na 1.35 e na 1.36, `modelo/trilha/` desde a 2.0), para o aviso da parte fixa e a sincronização das regras do `config.yaml` continuarem lendo as versões antigas.

**7. Versão 2.0.** Muda o caminho de tudo o que o projeto importa ou liga; a versão principal sobe. O comum vai a "Versão 2.0", o plugin a 2.0.0, e a tag `v2.0` vai no merge commit.

## Risks / Trade-offs

- [Projeto não migrado com o `check.sh` comparando com o kit 2.0] → a conferência dele reprova com a fonte inexistente, o que já acontece a cada versão nova do comum; a mensagem leva ao `kit.py atualizar`.
- [`check.sh` com a parte fixa alterada] → não é tocado; a ferramenta avisa e a troca fica à mão.
- [Hook próprio do projeto em `.githooks/`] → a migração só apaga o `pre-commit` do kit; o `core.hooksPath` passa a `trilha/hooks`, então um hook próprio deixa de rodar: a ferramenta avisa quando sobra arquivo em `.githooks/`, para o projeto decidir onde ligá-lo.
- [Arquivo próprio posto em `trilha/`] → a atualização o apaga e a conferência o reprova: a pasta é só do método, e o comum diz isso.

## Migration Plan

1. Na branch: o molde em `modelo/trilha/`, o `verifica.sh`, as conferências, a ferramenta com a migração, os textos com os caminhos novos, a versão 2.0 e os testes.
2. Execução manual: migrar um clone descartável do heimdall e conferir o `check.sh`, a trava do commit, a trava do Claude Code e a página.
3. Depois do merge: cada projeto real migra com `python3 ../trilha-ai/ferramentas/kit.py atualizar .`, sob a ordem do usuário nomeando-o; o que a ferramenta avisar (hook próprio, parte fixa alterada) se resolve no projeto.
4. Volta atrás: o projeto não migrado continua funcionando com a cópia que tem; reverter o merge da change devolve o kit à 1.36.
