# Design

## Context

Hoje o `kit.py` soma ao `.claude/settings.json` do projeto só o hook da trava (`_ligar_travas`), lendo a entrada do `modelo/claude-settings.json`. A conferência do método (`confere_metodo.py`) lê `claude plugin list --json` na pasta de onde foi chamada e julga toda instalação `sdd@…` da lista.

Um experimento feito no propose, numa pasta descartável e desfeito depois (a lista de instalações da máquina voltou igual), mostrou como o Claude Code 2.1.301 trata o escopo de projeto:
- `claude plugin install sdd@trilha-ai --scope project` grava `enabledPlugins` no `.claude/settings.json` da pasta e cria na lista uma entrada com `"scope": "project"` e `"projectPath"`.
- Essa entrada aparece também quando a lista roda em **outra** pasta, com `"enabled": true`, mesmo sem valer ali. O `projectEnabled` só diz se o settings.json da pasta atual liga o plugin.
- O `enabled` de uma entrada de escopo `user` segue o settings.json da pasta atual: com o projeto declarando o plugin falso, a lista o dá desligado.
- Com a instalação do usuário e a do projeto, a lista traz as duas, cada uma com a sua versão.

## Goals / Non-Goals

**Goals:**
- Uma só fonte para o que o projeto declara: o `modelo/claude-settings.json`.
- O aviso do plugin certo para o projeto, e não para a máquina inteira.

**Non-Goals:**
- Rodar o `claude plugin install` pelo `kit.py`: é estado da máquina, como o perfil do OpenSpec, que a ferramenta só lê.
- Avisar a instalação de escopo `user` como excesso: ela ainda serve aos projetos não migrados.

## Decisions

1. **A soma do settings.json lê o modelo inteiro.** A função que hoje liga o hook passa a somar também as chaves `enabledPlugins` e `extraKnownMarketplaces` do modelo, entrada por entrada, só quando a entrada falta (`setdefault`): o `false` que o projeto pôs no plugin fica. O arquivo só é escrito quando algo mudou, e por isso a segunda atualização não o toca. *Alternativa descartada:* sobrescrever as duas chaves com as do modelo; apagaria os plugins e marketplaces próprios do projeto.

2. **O comando de instalação é impresso, nunca rodado.** O `novo` o põe nos próximos passos, no lugar do passo de instalar o plugin; o `atualizar` o imprime ao fim, sem recusa. O texto vem de uma constante no `kit.py`, e o da conferência, de outra no `confere_metodo.py`, que os projetos copiam sem o `kit.py`. Um teste confere que as duas dizem o mesmo comando. *Alternativa descartada:* importar uma da outra; o `confere_metodo.py` roda no projeto, onde o `kit.py` não existe.

3. **A lista roda na pasta do projeto** (`cwd` igual à raiz do projeto, a pasta acima de `trilha/`). Sem isso, o `enabled` da entrada `user` refletiria a pasta de onde o `check.sh` ou o CI chamou.

4. **A instalação que vale: a mais específica, por plugin.** Para cada id `sdd@…`, a conferência fica com a entrada de escopo `local` dessa pasta, senão a de escopo `project` dessa pasta, senão a sem `projectPath` (`user`, ou outro escopo da máquina inteira). A pasta é comparada pelo caminho resolvido. A entrada com `projectPath` de outra pasta é descartada. A ordem segue a precedência das configurações do Claude Code (local acima de projeto, projeto acima de usuário). *Alternativa descartada:* julgar todas, como hoje; com a instalação antiga do usuário ao lado da nova do projeto, o aviso de versão acusaria a do usuário, que não é a que vale ali.

5. **Os padrões técnicos são um arquivo a preencher.** `sdd/padroes-tecnicos.md` entra no `A_PREENCHER` do `kit.py`, com a origem `modelo/sdd/padroes-tecnicos.md`: o `novo` o copia, o `atualizar` só o cria quando falta e avisa, como os outros preenchidos. Não entra na parte fixa (`COM_PARTE_FIXA`): o arquivo é inteiro do projeto. O `novo` cria `sdd/` já com o arquivo; o `mkdir` de hoje passa a aceitar a pasta existente. O conteúdo é a seção "Defaults institucionais" da skill, com a primeira linha dizendo para que serve e que o desvio vira ADR, e com o Python em `requires-python = ">=3.12.3"` na seção `[project]` do `pyproject.toml`. *Alternativa descartada:* o arquivo na raiz do projeto; o comum põe os documentos do método em `sdd/`, e é a skill `tdd` quem o lê.

6. **A skill lê o arquivo; o princípio 4 continua.** A seção 4 da skill `tdd` passa a "Padrões técnicos do projeto": ler o `sdd/padroes-tecnicos.md` quando existir e tomá-lo como ponto de partida, confirmado na entrevista; sem ele, recomendar só pela entrevista, sem inventar padrão. O princípio 4 ("declarados, nunca impostos") passa a apontar para o arquivo.

7. **O esqueleto do `CLAUDE.md` lista o arquivo** na linha de `sdd/`. O comum não muda além da versão.

8. **A conferência sem `sdd/` continua.** Projetos antigos podem não ter a pasta; o teste do aviso "sem a pasta sdd/" passa a apagar a pasta que a cópia do kit agora traz, e os testes que criam `sdd/` passam a aceitá-la existente.

## Risks / Trade-offs

- [A precedência entre escopos é deduzida das configurações, não do carregamento de plugins] → a execução manual instala o plugin com `--scope project` numa pasta descartável ao lado da instalação do usuário, abre o Claude Code nela e confere qual versão da skill carrega; se for outra, a decisão 4 volta ao design antes do archive.
- [A lista do Claude Code pode mudar o formato da entrada de projeto] → sem `projectPath`, a entrada conta como da máquina inteira, que é o comportamento de hoje.
- [O projeto na 2.1 com o plugin 2.2 perde os padrões] → o aviso de versão diferente já existe e manda atualizar o que estiver atrás.

## Migration Plan

O `kit.py atualizar` de cada projeto traz a declaração e o arquivo dos padrões (item 10 do plano, com a ordem do usuário). Em cada máquina, depois: `claude plugin install sdd@trilha-ai --scope project` em cada projeto e, quando todos declararem o plugin, `claude plugin uninstall sdd@trilha-ai` (o escopo do usuário), como o README passa a dizer. Reverter é voltar à tag `v2.1`: a declaração a mais no settings.json não quebra nada.
